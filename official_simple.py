#!/usr/bin/env python3
"""
官方简化版本 - 直接使用，不需要复杂修复
"""

import os
from typing import Dict, Any

# 设置GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

# 直接导入 - 不需要修复
from swift.llm import (
    TrainArguments, sft_main, register_dataset, DatasetMeta, ResponsePreprocessor, SubsetDataset
)

class CustomPreprocessor(ResponsePreprocessor):
    def preprocess(self, row: Dict[str, Any]) -> Dict[str, Any]:
        query = f"""任务：判断下面两句话语意是否相似。

句子1: {row['text1']}

句子2: {row['text2']}

请输出类别[0/1]: 0代表含义不同, 1代表含义相似。

"""
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
        subsets=[SubsetDataset('train', split=['train']), SubsetDataset('test', split=['test'])],
        preprocess_func=CustomPreprocessor(),
    ))

if __name__ == '__main__':
    # 官方参数配置
    sft_main(TrainArguments(
        model='Qwen/Qwen3-4B-Instruct-2507',  # 使用官方推荐的3B模型
        dataset=['swift/financial_classification:train'],
        train_type='lora',
        torch_dtype='bfloat16',
        num_train_epochs=3,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        learning_rate=1e-4,
        lora_rank=8,  # 减小rank节省显存
        lora_alpha=32,
        target_modules=['all-linear'],  # 官方推荐设置
        gradient_accumulation_steps=4,
        eval_steps=50,
        save_steps=50,
        save_total_limit=2,
        logging_steps=5,
        max_length=2048,
        output_dir='output',
        warmup_ratio=0.05,
        dataset_num_proc=4,
        dataloader_num_workers=4,
        attn_impl='flash_attn',  # 官方参数名
        packing=True,
        save_only_model=True,
    ))
