#!/usr/bin/env python3
"""
金融文本相似度分类竞赛 - 模型训练和推理脚本
合并训练和推理功能
"""

import os
import re
import json
import torch
import argparse
from typing import Dict, Any, List, Optional
from swift.llm import (
    TrainArguments, sft_main, register_dataset, DatasetMeta, ResponsePreprocessor, SubsetDataset,
    InferArguments, infer_main
)
from swift.utils import read_from_jsonl, write_to_jsonl
from pathlib import Path

os.environ['CUDA_VISIBLE_DEVICES'] = '0'

def get_project_root():
    """获取项目根目录"""
    # 从当前脚本位置向上两级到达项目根目录
    current_file = Path(__file__).resolve()
    return current_file.parent.parent

class EnhancedPreprocessor(ResponsePreprocessor):
    """优化的数据预处理器"""

    def preprocess(self, row: Dict[str, Any]) -> Dict[str, Any]:
        query = f"""判断下面两句金融咨询文本是否表达相同的语义含义。

句子1: {row['text1']}
句子2: {row['text2']}

规则：
- 含义相同或非常相似: 输出1
- 含义不同或不相似: 输出0
- 只输出单个数字0或1

结果: """

        response = str(row['label'])
        row = {
            'query': query,
            'response': response
        }
        return super().preprocess(row)

def register_datasets():
    """注册数据集"""
    register_dataset(
        DatasetMeta(
            ms_dataset_id='swift/financial_classification',
            subsets=[
                SubsetDataset('train', split=['train']),
                SubsetDataset('val', split=['train[:1000]']),  # 使用前1000个样本作为验证集
                SubsetDataset('test', split=['test'])
            ],
            preprocess_func=EnhancedPreprocessor(),
            dataset_config={
                'trust_remote_code': True,
                'download_mode': 'reuse_dataset_if_exists'
            }
        )
    )

def load_config():
    """加载训练配置"""
    import json
    project_root = get_project_root()
    config_file = project_root / 'config' / 'train_config.json'

    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_training_args(output_dir: Optional[str] = None) -> TrainArguments:
    """获取优化的训练参数"""
    if output_dir is None:
        project_root = get_project_root()
        output_dir = str(project_root / 'models' / 'enhanced_output')

    # 加载配置文件
    config = load_config()

    return TrainArguments(
        model=config['model']['model_id'],
        model_type=config['model']['model_type'],
        dataset=['swift/financial_classification:train'],
        dataset_config={
            'trust_remote_code': True,
            'download_mode': 'reuse_dataset_if_exists'
        },
        # 类别平衡调整（训练集中0:69%, 1:31%）
        loss_scale_config={
            '0': 0.7,  # 减少多数类权重
            '1': 1.3   # 增加少数类权重
        },
        train_type='lora',
        torch_dtype=config['model']['torch_dtype'],
        output_dir=output_dir,
        num_train_epochs=config['training']['num_train_epochs'],
        per_device_train_batch_size=config['training']['per_device_train_batch_size'],
        per_device_eval_batch_size=config['training']['per_device_eval_batch_size'],
        gradient_accumulation_steps=config['training']['gradient_accumulation_steps'],
        learning_rate=config['training']['learning_rate'],
        lr_scheduler_type='cosine',
        warmup_ratio=config['training']['warmup_ratio'],
        weight_decay=config['training']['weight_decay'],
        max_grad_norm=config['training']['max_grad_norm'],
        max_length=config['training']['max_length'],
        gradient_checkpointing=config['training']['gradient_checkpointing'],
        optim=config['training']['optim'],
        dataloader_num_workers=config['training']['dataloader_num_workers'],
        dataloader_pin_memory=config['training']['dataloader_pin_memory'],
        # 显存优化设置
        packing=True,
        dataset_num_proc=1,  # 减少进程数节省显存
        ddp_find_unused_parameters=False,
        # 额外显存优化
        use_flash_attn=True,  # 启用flash attention
        model_kwargs={
            "trust_remote_code": True,
            "torch_dtype": "bfloat16",
            "use_cache": False  # 训练时关闭KV cache节省显存
        },
        save_steps=config['training']['save_steps'],
        eval_steps=config['training']['eval_steps'],
        logging_steps=config['training']['logging_steps'],
        save_total_limit=config['training']['save_total_limit'],
        load_best_model_at_end=config['training']['load_best_model_at_end'],
        metric_for_best_model=config['training']['metric_for_best_model'],
        greater_is_better=config['training']['greater_is_better'],
        lora_rank=config['lora']['lora_rank'],
        lora_alpha=config['lora']['lora_alpha'],
        lora_dropout=config['lora']['lora_dropout'],
        target_modules=config['lora']['target_modules'],
        max_grad_norm=1.0,
        save_only_model=True,
        packing=True,
        dataset_num_proc=4,
        dataloader_num_workers=4,
        attn_impl='flash_attn',
        use_nested_quant=True,
        system="你是一个专业的金融文本相似度判断专家。请仔细分析两句话在金融语境下的语义相似性，只输出0或1，不要输出其他内容。",
        seed=42,
        gradient_checkpointing=True,
        ddp_find_unused_parameters=False,
        early_stopping=True,
        early_stopping_patience=3,
        early_stopping_threshold=0.001,
    )

def extract_prediction(response: str) -> int:
    """从模型输出中提取预测结果"""
    if not response:
        return 0

    response = response.strip()

    # 直接匹配数字0或1
    if response in ['0', '1']:
        return int(response)

    # 匹配包含数字的模式
    digit_match = re.search(r'\b([01])\b', response)
    if digit_match:
        return int(digit_match.group(1))

    # 基于关键词判断
    response_lower = response.lower()
    positive_keywords = ['相似', '相同', '类似', '一致', '是', 'yes', 'true']
    negative_keywords = ['不同', '不相似', '不相同', '差异', '不是', 'no', 'false']

    positive_score = sum(1 for word in positive_keywords if word in response_lower)
    negative_score = sum(1 for word in negative_keywords if word in response_lower)

    if positive_score > negative_score:
        return 1
    elif negative_score > positive_score:
        return 0
    else:
        return 0

def find_best_checkpoint(output_dir: Optional[str] = None) -> Optional[str]:
    """查找最佳checkpoint"""
    if output_dir is None:
        project_root = get_project_root()
        output_dir = str(project_root / 'models' / 'enhanced_output')
    """查找最佳checkpoint"""
    import glob

    checkpoint_pattern = f"{output_dir}/checkpoint-*"
    checkpoint_dirs = glob.glob(checkpoint_pattern)

    if not checkpoint_dirs:
        print(f"❌ 未找到checkpoint文件: {checkpoint_pattern}")
        return None

    try:
        latest_checkpoint = max(checkpoint_dirs, key=lambda x: int(x.split('-')[-1]))
        print(f"✅ 找到最佳模型: {latest_checkpoint}")
        return latest_checkpoint
    except ValueError:
        print(f"⚠️ 无法确定最佳checkpoint，使用: {checkpoint_dirs[0]}")
        return checkpoint_dirs[0]

def get_inference_args(ckpt_dir: str) -> InferArguments:
    """获取推理参数"""
    project_root = get_project_root()
    result_path = str(project_root / 'results' / 'enhanced_result.jsonl')

    # 加载配置文件
    config = load_config()

    return InferArguments(
        adapters=[ckpt_dir],
        temperature=config['inference']['temperature'],
        max_batch_size=16,
        max_new_tokens=config['inference']['max_new_tokens'],
        val_dataset=["swift/financial_classification:test"],
        infer_backend='pt',
        do_sample=config['inference']['do_sample'],
        repetition_penalty=config['inference']['repetition_penalty'],
        result_path=result_path
    )

def run_training():
    """运行模型训练"""
    print("🚀 开始模型训练")
    print("=" * 50)

    # 检查GPU
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✅ GPU可用: {gpu_count} × {gpu_name}")
    else:
        print("❌ 未检测到GPU，使用CPU训练")
        return False

    # 注册数据集
    print("\n📝 注册数据集...")
    try:
        register_datasets()
        print("✅ 数据集注册成功")
    except Exception as e:
        print(f"❌ 数据集注册失败: {e}")
        return False

    # 获取训练参数
    train_args = get_training_args()
    print("\n📋 训练配置:")
    print(f"  • 模型: {train_args.model}")
    print(f"  • 训练轮数: {train_args.num_train_epochs}")
    print(f"  • 学习率: {train_args.learning_rate}")
    print(f"  • LoRA rank: {train_args.lora_rank}")
    print(f"  • 输出目录: {train_args.output_dir}")

    # 开始训练
    print("\n🚀 开始训练...")
    print("💡 提示: 训练过程可能需要较长时间，请耐心等待...")
    try:
        sft_main(train_args)
        print("\n🎉 训练完成！")
        return True
    except Exception as e:
        print(f"\n❌ 训练失败: {e}")
        print("\n🔍 详细错误信息:")
        print("=" * 50)
        import traceback
        traceback.print_exc()
        print("=" * 50)

        print("\n🔧 可能的解决方法:")
        print("1. 检查GPU是否可用: python -c 'import torch; print(torch.cuda.is_available())'")
        print("2. 检查GPU内存是否充足")
        print("3. 检查数据集文件是否存在")
        print("4. 尝试使用更小的batch_size")
        print("5. 检查依赖是否正确安装: python test_setup.py")

        return False

def run_inference():
    """运行模型推理"""
    print("🧠 开始模型推理")
    print("=" * 50)

    # 查找最佳模型
    print("\n📁 查找最佳模型...")
    ckpt_dir = find_best_checkpoint()
    if not ckpt_dir:
        print("❌ 未找到可用的模型checkpoint")
        return False

    # 注册数据集
    print("\n📝 注册推理数据集...")
    try:
        register_datasets()
        print("✅ 数据集注册成功")
    except Exception as e:
        print(f"❌ 数据集注册失败: {e}")
        return False

    # 获取推理参数
    infer_args = get_inference_args(ckpt_dir)

    print("📋 推理配置:")
    print(f"  • 模型: {ckpt_dir}")
    print(f"  • 温度: {infer_args.temperature}")
    print(f"  • 批次大小: {infer_args.max_batch_size}")
    print(f"  • 输出文件: {infer_args.result_path}")

    # 开始推理
    print("\n🧠 开始推理...")
    try:
        result = infer_main(infer_args)
        print("✅ 推理完成！")
        return True
    except Exception as e:
        print(f"\n❌ 推理失败: {e}")
        print("\n🔍 详细错误信息:")
        print("=" * 50)
        import traceback
        traceback.print_exc()
        print("=" * 50)

        print("\n🔧 可能的解决方法:")
        print("1. 检查模型文件是否存在")
        print("2. 检查GPU内存是否充足")
        print("3. 检查数据集是否正确注册")
        print("4. 查看训练日志确认模型训练是否正常完成")

        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="模型训练和推理脚本")
    parser.add_argument('action', choices=['train', 'inference', 'all'],
                       help='执行操作: train(训练), inference(推理), all(训练+推理)')

    args = parser.parse_args()

    success = True

    if args.action in ['train', 'all']:
        success &= run_training()

    if args.action in ['inference', 'all']:
        success &= run_inference()

    if success:
        print("\n🎉 操作完成！")
        if args.action in ['inference', 'all']:
            print("\n📤 结果文件:")
            print("  • 推理结果: results/enhanced_result.jsonl")
            print("  • 竞赛提交: cp results/enhanced_result.jsonl results/result.json")
    else:
        print("\n❌ 操作失败")

if __name__ == '__main__':
    main()
