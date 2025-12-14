#!/usr/bin/env python3
"""
金融文本相似度分类 - 高准确率优化版本
使用更大的模型和优化的超参数
"""

import os
from typing import Dict, Any

# 设置GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

# 直接导入 - Swift官方推荐方式
from swift.llm import (
    TrainArguments, sft_main, register_dataset, DatasetMeta, ResponsePreprocessor, SubsetDataset
)

class FinancialSimilarityPreprocessor(ResponsePreprocessor):
    """金融文本相似度专用预处理器"""

    def preprocess(self, row: Dict[str, Any]) -> Dict[str, Any]:
        # 优化prompt，增强金融领域理解
        query = f"""你是一个专业的金融文本分析专家。请仔细分析下面两句话在金融语境下的语义相似性。

句子1: {row['text1']}
句子2: {row['text2']}

请只输出一个数字：0或1
- 0: 含义不同或不相似
- 1: 含义相同或高度相似

你的回答："""

        response = str(row['label'])

        row = {
            'query': query,
            'response': response
        }
        return super().preprocess(row)

# 注册数据集
register_dataset(
    DatasetMeta(
        ms_dataset_id='swift/financial_classification',
        subsets=[
            SubsetDataset('train', split=['train']),
            SubsetDataset('test', split=['test'])
        ],
        preprocess_func=FinancialSimilarityPreprocessor(),
    ))

if __name__ == '__main__':
    print("🚀 开始金融文本相似度分类训练...")
    print("📊 使用Qwen2-7B模型，目标准确率: 0.87+")
    print("💾 显存要求: <22GB")

    # 高准确率优化配置
    sft_main(TrainArguments(
        # 🎯 大模型选择 - Qwen2-7B提供更好的性能
        model='Qwen/Qwen2-7B-Instruct',

        # 📚 数据集配置
        dataset=['swift/financial_classification:train'],

        # 🔧 训练类型
        train_type='lora',

        # ⚡ 精度设置
        torch_dtype='bfloat16',

        # 📈 训练轮数 - 增加到5轮提高准确率
        num_train_epochs=5,

        # 📦 批次大小优化 - 在22G显存下最大化利用
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8,  # 1*8=8有效批次

        # 🎯 学习率优化 - 更稳定的收敛
        learning_rate=5e-5,  # 从1e-4降低到5e-5

        # 🔍 LoRA配置优化 - 提高rank增强表达能力
        lora_rank=16,  # 从8增加到16
        lora_alpha=32,  # 保持alpha=2*rank比例

        # 🎯 目标模块 - 全面微调
        target_modules=['all-linear'],

        # 📏 序列长度 - 适合金融文本特征
        max_length=512,  # 从2048降低到512，适合平均13字符文本

        # 💾 内存优化
        attn_impl='flash_attn',
        packing=False,  # 关闭packing节省显存

        # 📊 评估和保存
        eval_steps=100,
        save_steps=100,
        save_total_limit=3,

        # 📝 日志频率
        logging_steps=10,

        # 🔥 预热和正则化
        warmup_ratio=0.1,  # 增加预热比例

        # ⚙️ 数据处理
        dataset_num_proc=4,
        dataloader_num_workers=2,  # 减少worker避免内存竞争

        # 📁 输出配置
        output_dir='output_qwen2_7b_optimized',
        save_only_model=True,

        # 🎯 系统提示 - 增强金融领域专业性
        system="你是一个专业的金融文本相似度判断专家。请仔细分析两句话在金融语境下的语义相似性，只输出0或1，不要输出其他内容。",
    ))

    print("✅ 训练完成！请检查output_qwen2_7b_optimized目录")
