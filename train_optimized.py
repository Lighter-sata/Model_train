#!/usr/bin/env python3
"""
金融文本相似度分类 - 高准确率优化版本
使用更大的模型和优化的超参数
"""

# ===========================================
# 紧急修复：datasets兼容性问题
# 在任何导入之前执行
# ===========================================

print("🔧 [train] 开始紧急修复datasets兼容性...")

try:
    # 1. 修复pyarrow问题
    import pyarrow as pa
    print("🔧 [train] pyarrow修复完成")

    if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
        pa.PyExtensionType = pa.ExtensionType
        print("🔧 [train] 已修复pyarrow.PyExtensionType")

    # 2. 修复datasets LargeList问题
    import datasets
    print("🔧 [train] datasets修复开始")

    if not hasattr(datasets, 'LargeList'):
        try:
            from datasets.features import Sequence
            datasets.LargeList = Sequence
            print("🔧 [train] 已修复datasets LargeList (使用Sequence)")
        except ImportError:
            class LargeList:
                def __init__(self, dtype, length=None):
                    self.dtype = dtype
                    self.length = length
            datasets.LargeList = LargeList
            print("🔧 [train] 已创建datasets LargeList兼容类")

    # 3. 修复_FEATURE_TYPES
    from datasets.features import features
    if not hasattr(features, '_FEATURE_TYPES'):
        _FEATURE_TYPES = {}
        for attr_name in dir(features):
            attr = getattr(features, attr_name)
            if (hasattr(attr, '__name__') and
                hasattr(attr, '__module__') and
                attr.__module__ == 'datasets.features.features' and
                (attr_name.endswith('Type') or 'Array' in attr_name or 'Value' in attr_name or 'Class' in attr_name)):
                _FEATURE_TYPES[attr_name] = attr

        if hasattr(features, 'Sequence'):
            _FEATURE_TYPES['LargeList'] = features.Sequence

        features._FEATURE_TYPES = _FEATURE_TYPES
        print(f"🔧 [train] 已创建_FEATURE_TYPES ({len(_FEATURE_TYPES)}个类型)")

    print("🔧 [train] 所有兼容性修复完成")

except Exception as e:
    print(f"🔧 [train] 修复失败: {e}")

print("🔧 [train] 开始正常导入...\n")

# ===========================================
# 正常导入开始
# ===========================================

import os
from typing import Dict, Any

# 设置GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

# ===========================================
# 修复Swift库兼容性问题
# ===========================================

print("🔧 修复Swift库兼容性问题...")

try:
    # 1. 修复transformers ALLOWED_LAYER_TYPES
    import sys
    try:
        import transformers
        print("🔧 修复transformers兼容性...")

        # 修复ALLOWED_LAYER_TYPES
        if not hasattr(transformers.configuration_utils, 'ALLOWED_LAYER_TYPES'):
            transformers.configuration_utils.ALLOWED_LAYER_TYPES = [
                'Linear', 'Conv1D', 'Conv2d', 'Embedding', 'LayerNorm', 'Dropout'
            ]
            print("🔧 已添加 ALLOWED_LAYER_TYPES 到 transformers")

        # 修复Gemma3Config
        if not hasattr(transformers, 'Gemma3Config'):
            # 创建一个基本的配置类
            from transformers.configuration_utils import PretrainedConfig
            class Gemma3Config(PretrainedConfig):
                model_type = "gemma3"
                def __init__(self, **kwargs):
                    super().__init__(**kwargs)
            transformers.Gemma3Config = Gemma3Config
            print("🔧 已添加 Gemma3Config 到 transformers")

    except ImportError:
        print("⚠️ transformers未安装，跳过修复")

    # 2. 修复lmdeploy EngineGenerationConfig
    try:
        import lmdeploy
        if not hasattr(lmdeploy, 'EngineGenerationConfig'):
            # 创建一个基本的兼容类
            class EngineGenerationConfig:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            lmdeploy.EngineGenerationConfig = EngineGenerationConfig
            print("🔧 已添加 EngineGenerationConfig 到 lmdeploy")
    except ImportError:
        print("⚠️ lmdeploy未安装，跳过修复")

    print("✅ Swift库兼容性修复完成")

except Exception as e:
    print(f"⚠️ Swift库修复失败，继续尝试: {e}")

# ===========================================
# 验证修复效果
# ===========================================

print("🔍 验证修复效果...")
try:
    # 测试datasets是否正常
    import datasets
    assert hasattr(datasets, 'LargeList'), "LargeList不存在"
    from datasets.features import features
    assert hasattr(features, '_FEATURE_TYPES'), "_FEATURE_TYPES不存在"
    print("✅ datasets兼容性修复验证通过")
except Exception as e:
    print(f"❌ datasets修复验证失败: {e}")
    exit(1)

# 现在安全地导入Swift
print("🔧 导入Swift...")
try:
    from swift.llm import (
        TrainArguments, sft_main, register_dataset, DatasetMeta, ResponsePreprocessor, SubsetDataset
    )
    print("✅ Swift导入成功")
except ImportError as e:
    print(f"❌ Swift导入失败: {e}")
    # 如果Swift导入失败，提供替代方案
    print("💡 尝试使用简化版本...")
    try:
        # 尝试只导入需要的部分
        import swift
        print(f"✅ Swift基础导入成功 (版本: {swift.__version__})")
        print("⚠️ 但llm模块可能有兼容性问题")
        print("💡 建议:")
        print("1. 检查Swift版本兼容性")
        print("2. 或使用Swift的命令行工具")
        print("3. 或手动安装兼容版本的依赖")
    except ImportError:
        print("❌ Swift完全不可用")
    exit(1)

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
