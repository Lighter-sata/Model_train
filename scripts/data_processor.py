#!/usr/bin/env python3
"""
金融文本相似度分类竞赛 - 数据处理脚本
合并数据下载和分析功能
"""

import os
import json
import requests
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import jieba
from wordcloud import WordCloud
import argparse

def download_dataset_files():
    """直接下载数据集文件"""

    print("🔍 下载数据集")
    print("=" * 50)

    # 创建目录
    os.makedirs('../results/dataset_analysis', exist_ok=True)
    os.makedirs('../data', exist_ok=True)

    try:
        # 下载训练集
        print("📥 下载训练集...")
        train_url = "https://www.modelscope.cn/api/v1/datasets/swift/financial_classification/repo?Source=SDK&Revision=master&FilePath=train.jsonl"
        response = requests.get(train_url)
        response.raise_for_status()

        train_file = '../data/train.jsonl'
        with open(train_file, 'w', encoding='utf-8') as f:
            f.write(response.text)

        # 下载测试集
        print("📥 下载测试集...")
        test_url = "https://www.modelscope.cn/api/v1/datasets/swift/financial_classification/repo?Source=SDK&Revision=master&FilePath=test.jsonl"
        response = requests.get(test_url)
        response.raise_for_status()

        test_file = '../data/test.jsonl'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print("✅ 数据集下载完成")
        return train_file, test_file

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None, None

def load_jsonl_data(file_path):
    """加载JSONL格式的数据"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line.strip()))
        return data
    except Exception as e:
        print(f"❌ 加载{file_path}失败: {e}")
        return []

def analyze_dataset():
    """分析数据集"""

    print("\n📊 分析数据集")
    print("=" * 50)

    # 检查数据文件是否存在
    train_file = '../data/train.jsonl'
    test_file = '../data/test.jsonl'

    if not os.path.exists(train_file) or not os.path.exists(test_file):
        print("❌ 数据文件不存在，请先运行数据下载")
        return

    # 加载数据
    print("📥 加载数据...")
    train_data = load_jsonl_data(train_file)
    test_data = load_jsonl_data(test_file)

    print(f"训练集: {len(train_data)} 条")
    print(f"测试集: {len(test_data)} 条")

    if not train_data:
        return

    # 基本信息
    print("\n📋 数据集基本信息")
    print("-" * 30)
    print(f"训练集大小: {len(train_data)}")
    print(f"测试集大小: {len(test_data)}")
    print(f"特征字段: {list(train_data[0].keys())}")

    # 示例
    print("\n🔍 示例样本")
    for i in range(min(3, len(train_data))):
        sample = train_data[i]
        print(f"样本 {i+1}:")
        print(f"  text1: {sample['text1']}")
        print(f"  text2: {sample['text2']}")
        print(f"  label: {sample['label']}")
        print()

    # 类别分布
    print("📈 类别分布分析")
    print("-" * 30)

    train_labels = [sample['label'] for sample in train_data]
    train_counter = Counter(train_labels)
    print(f"训练集类别分布: {dict(train_counter)}")

    test_labels = [sample.get('label') for sample in test_data if sample.get('label') is not None]
    test_counter = Counter(test_labels)
    print(f"测试集类别分布: {dict(test_counter)}")

    # 可视化
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.bar(train_counter.keys(), train_counter.values(), color=['skyblue', 'lightcoral'])
    ax1.set_title('训练集类别分布')
    ax1.set_xlabel('类别')
    ax1.set_ylabel('样本数')

    ax2.bar(test_counter.keys(), test_counter.values(), color=['skyblue', 'lightcoral'])
    ax2.set_title('测试集类别分布')
    ax2.set_xlabel('类别')
    ax2.set_ylabel('样本数')

    plt.tight_layout()
    plt.savefig('../results/dataset_analysis/class_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("✅ 类别分布图已保存")

    # 文本长度分析
    print("\n📏 文本长度分析")
    print("-" * 30)

    train_text1_lens = [len(sample['text1']) for sample in train_data]
    train_text2_lens = [len(sample['text2']) for sample in train_data]

    print("训练集text1长度统计:")
    print(f"  平均: {sum(train_text1_lens)/len(train_text1_lens):.1f}")
    print(f"  最大: {max(train_text1_lens)}")
    print(f"  最小: {min(train_text1_lens)}")

    print("训练集text2长度统计:")
    print(f"  平均: {sum(train_text2_lens)/len(train_text2_lens):.1f}")
    print(f"  最大: {max(train_text2_lens)}")
    print(f"  最小: {min(train_text2_lens)}")

    # 词汇分析
    print("\n📝 词汇分析")
    print("-" * 30)

    all_words = []
    word_freq = Counter()

    for sample in tqdm(train_data[:1000], desc="分词处理"):  # 只处理前1000个样本
        words1 = jieba.cut(sample['text1'])
        words2 = jieba.cut(sample['text2'])

        for word in words1:
            if len(word.strip()) > 1:
                word_freq[word] += 1
                all_words.append(word)

        for word in words2:
            if len(word.strip()) > 1:
                word_freq[word] += 1
                all_words.append(word)

    top_words = word_freq.most_common(20)
    print("高频词汇TOP 20:")
    for word, freq in top_words:
        print(f"{word}: {freq}")

    # 词云
    try:
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            max_words=100
        ).generate_from_frequencies(dict(top_words))

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('高频词汇词云图')
        plt.savefig('../results/dataset_analysis/wordcloud.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 词云图已保存")
    except Exception as e:
        print(f"词云图生成失败: {e}")

    # 保存分析报告
    report = {
        'dataset_info': {
            'train_size': len(train_data),
            'test_size': len(test_data),
            'features': list(train_data[0].keys())
        },
        'class_distribution': {
            'train': dict(train_counter),
            'test': dict(test_counter)
        },
        'text_stats': {
            'train_text1_avg_len': sum(train_text1_lens)/len(train_text1_lens),
            'train_text2_avg_len': sum(train_text2_lens)/len(train_text2_lens)
        },
        'vocabulary': {
            'total_words': len(all_words),
            'unique_words': len(word_freq),
            'top_words': top_words[:10]
        }
    }

    with open('../results/dataset_analysis/analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("✅ 分析报告已保存")

    print("\n🎉 数据集处理完成！")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据处理脚本")
    parser.add_argument('action', choices=['download', 'analyze', 'all'],
                       help='执行操作: download(下载), analyze(分析), all(全部)')

    args = parser.parse_args()

    if args.action in ['download', 'all']:
        train_file, test_file = download_dataset_files()
        if not train_file:
            return

    if args.action in ['analyze', 'all']:
        analyze_dataset()

if __name__ == '__main__':
    main()
