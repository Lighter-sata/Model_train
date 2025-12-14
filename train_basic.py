#!/usr/bin/env python3
"""
金融文本相似度分类 - 基础PyTorch版本
不依赖Swift库，直接使用transformers训练
"""

import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from datasets import load_dataset
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

# 设置GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class FinancialSimilarityDataset(Dataset):
    """金融文本相似度数据集"""

    def __init__(self, tokenizer, data, max_length=512):
        self.tokenizer = tokenizer
        self.data = data
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # 构建输入文本
        text = f"判断以下两句话是否语义相似：句子1: {item['text1']} 句子2: {item['text2']}"

        # 编码
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(item['label'], dtype=torch.long)
        }

def compute_metrics(eval_pred):
    """计算评估指标"""
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)

    accuracy = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average='weighted')

    return {
        'accuracy': accuracy,
        'f1': f1
    }

def main():
    print("🚀 金融文本相似度分类 - 基础PyTorch版本")
    print("🎯 目标准确率: 0.85+")
    print("🤖 使用模型: Qwen2-7B (分类头)")
    print("="*50)

    # 1. 加载数据
    print("📚 加载数据集...")
    try:
        dataset = load_dataset('swift/financial_classification')
        train_data = dataset['train']
        test_data = dataset['test']

        # 转换为列表格式
        train_list = []
        for item in train_data:
            train_list.append({
                'text1': item['text1'],
                'text2': item['text2'],
                'label': item['label']
            })

        test_list = []
        for item in test_data:
            test_list.append({
                'text1': item['text1'],
                'text2': item['text2'],
                'label': item['label']
            })

        print(f"✅ 数据加载完成 - 训练集: {len(train_list)}, 测试集: {len(test_list)}")

    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        print("💡 请确保数据集可用或手动下载")
        return

    # 2. 加载模型和tokenizer
    print("🤖 加载Qwen2-7B模型...")
    try:
        model_name = "Qwen/Qwen2-7B-Instruct"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2,
            torch_dtype=torch.bfloat16,
        )

        # 调整模型以适应分类任务
        if hasattr(model, 'score'):
            # Qwen模型的分类头调整
            model.score = nn.Linear(model.config.hidden_size, 2)

        model.to(device)
        print("✅ 模型加载完成")

    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return

    # 3. 创建数据集
    print("🔧 创建数据集...")
    train_dataset = FinancialSimilarityDataset(tokenizer, train_list)
    test_dataset = FinancialSimilarityDataset(tokenizer, test_list)

    # 4. 训练参数
    training_args = TrainingArguments(
        output_dir='./results_qwen2_7b_basic',
        num_train_epochs=5,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8,  # 有效批次大小=8
        learning_rate=5e-5,
        warmup_ratio=0.1,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=100,
        save_steps=500,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
        fp16=False,  # 使用bf16
        bf16=True,
        dataloader_num_workers=2,
        remove_unused_columns=False,
    )

    # 5. 创建Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
        data_collator=DataCollatorWithPadding(tokenizer),
    )

    # 6. 开始训练
    print("🏃 开始训练...")
    print("💡 这将需要约2-3小时，具体取决于硬件")
    print("="*50)

    try:
        trainer.train()
        print("✅ 训练完成！")

        # 7. 评估
        print("📊 最终评估...")
        eval_results = trainer.evaluate()
        print(f"🎯 准确率: {eval_results['eval_accuracy']:.4f}")
        print(f"🎯 F1得分: {eval_results['eval_f1']:.4f}")

        # 8. 保存模型
        print("💾 保存模型...")
        trainer.save_model('./best_model_qwen2_7b')
        tokenizer.save_pretrained('./best_model_qwen2_7b')
        print("✅ 模型已保存到: ./best_model_qwen2_7b")

    except KeyboardInterrupt:
        print("⏹️ 训练被用户中断")
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
