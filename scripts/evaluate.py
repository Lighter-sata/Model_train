#!/usr/bin/env python3
"""
金融文本相似度分类竞赛 - 评估脚本
计算准确率、混淆矩阵、分类报告，并分析错误样本
"""

import os
import json
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from swift.utils import read_from_jsonl
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)

def load_test_labels() -> List[int]:
    """加载测试集标签"""

    try:
        from datasets import load_dataset
        labels = load_dataset('json', data_files='test_label.jsonl', split='train')['label']
        return labels
    except Exception as e:
        print(f"❌ 无法加载测试标签: {e}")
        print("请确保test_label.jsonl文件存在")
        return []

def load_predictions(result_file: str) -> Tuple[List[int], List[Dict]]:
    """加载预测结果"""

    if not os.path.exists(result_file):
        print(f"❌ 找不到结果文件: {result_file}")
        return [], []

    try:
        predictions_data = read_from_jsonl(result_file)
        predictions = []

        for pred in predictions_data:
            # 提取预测值
            response = pred.get('response', '').strip()
            if response in ['0', '1']:
                predictions.append(int(response))
            else:
                # 尝试从其他字段提取
                prediction = pred.get('prediction')
                if prediction is not None:
                    predictions.append(int(prediction))
                else:
                    print(f"⚠️ 无法解析预测结果: {pred}")
                    predictions.append(0)  # 默认值

        return predictions, predictions_data

    except Exception as e:
        print(f"❌ 加载预测结果失败: {e}")
        return [], []

def calculate_metrics(y_true: List[int], y_pred: List[int]) -> Dict:
    """计算各种评估指标"""

    metrics = {}

    try:
        # 基本指标
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision_macro'] = precision_score(y_true, y_pred, average='macro')
        metrics['recall_macro'] = recall_score(y_true, y_pred, average='macro')
        metrics['f1_macro'] = f1_score(y_true, y_pred, average='macro')
        metrics['precision_micro'] = precision_score(y_true, y_pred, average='micro')
        metrics['recall_micro'] = recall_score(y_true, y_pred, average='micro')
        metrics['f1_micro'] = f1_score(y_true, y_pred, average='micro')

        # 类别特定的指标
        metrics['precision_class_0'] = precision_score(y_true, y_pred, pos_label=0)
        metrics['precision_class_1'] = precision_score(y_true, y_pred, pos_label=1)
        metrics['recall_class_0'] = recall_score(y_true, y_pred, pos_label=0)
        metrics['recall_class_1'] = recall_score(y_true, y_pred, pos_label=1)
        metrics['f1_class_0'] = f1_score(y_true, y_pred, pos_label=0)
        metrics['f1_class_1'] = f1_score(y_true, y_pred, pos_label=1)

        # 计算AUC（如果需要概率值，这里简化处理）
        # 对于二分类，AUC可以使用预测值近似计算
        try:
            metrics['auc'] = roc_auc_score(y_true, y_pred)
        except:
            metrics['auc'] = None

    except Exception as e:
        print(f"⚠️ 计算指标时出错: {e}")

    return metrics

def plot_confusion_matrix(y_true: List[int], y_pred: List[int], save_path: str = 'evaluation_results/confusion_matrix.png'):
    """绘制混淆矩阵"""

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))

    # 使用seaborn绘制热力图
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['不相似(0)', '相似(1)'],
                yticklabels=['不相似(0)', '相似(1)'])

    plt.title('混淆矩阵')
    plt.ylabel('真实标签')
    plt.xlabel('预测标签')

    # 添加指标文本
    accuracy = np.trace(cm) / np.sum(cm)
    plt.text(0.5, -0.1, '.3f',
             ha='center', va='center', transform=plt.gca().transAxes,
             fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    print("📊 混淆矩阵已保存至:")
    print(f"  {save_path}")

def analyze_errors(y_true: List[int], y_pred: List[int], predictions_data: List[Dict]) -> Dict:
    """分析错误样本"""

    error_analysis = {
        'total_errors': 0,
        'error_types': {'FP': 0, 'FN': 0, 'other': 0},  # FP: 假正例, FN: 假负例
        'error_samples': []
    }

    # 找出错误样本
    for i, (true, pred) in enumerate(zip(y_true, y_pred)):
        if true != pred:
            error_analysis['total_errors'] += 1

            # 分类错误类型
            if true == 0 and pred == 1:  # 假正例：预测相似但实际不相似
                error_type = 'FP'
            elif true == 1 and pred == 0:  # 假负例：预测不相似但实际相似
                error_type = 'FN'
            else:
                error_type = 'other'

            error_analysis['error_types'][error_type] += 1

            # 保存错误样本详情
            if len(error_analysis['error_samples']) < 50:  # 只保存前50个错误样本
                sample_info = {
                    'index': i,
                    'true_label': true,
                    'pred_label': pred,
                    'error_type': error_type
                }

                # 添加文本内容（如果可用）
                if i < len(predictions_data):
                    pred_data = predictions_data[i]
                    query = pred_data.get('query', '')

                    # 从query中提取句子
                    import re
                    text1_match = re.search(r'句子1:\s*(.*?)(?:\n|$)', query, re.DOTALL)
                    text2_match = re.search(r'句子2:\s*(.*?)(?:\n|$)', query, re.DOTALL)

                    if text1_match and text2_match:
                        sample_info['text1'] = text1_match.group(1).strip()
                        sample_info['text2'] = text2_match.group(1).strip()

                error_analysis['error_samples'].append(sample_info)

    return error_analysis

def plot_error_analysis(error_analysis: Dict, save_path: str = 'evaluation_results/error_analysis.png'):
    """绘制错误分析图表"""

    if error_analysis['total_errors'] == 0:
        print("🎉 没有错误样本，无需绘制错误分析图")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # 错误类型分布
    error_types = error_analysis['error_types']
    ax1.bar(error_types.keys(), error_types.values(), color=['skyblue', 'lightcoral', 'lightgreen'])
    ax1.set_title('错误类型分布')
    ax1.set_xlabel('错误类型')
    ax1.set_ylabel('样本数')

    # 添加数值标签
    for i, (k, v) in enumerate(error_types.items()):
        ax1.text(i, v + 0.5, str(v), ha='center', va='bottom')

    # 错误率随时间的变化（如果有足够样本）
    errors_by_position = []
    window_size = 100

    # 简单的时间序列错误分析
    error_positions = [i for i, (true, pred) in enumerate(zip(error_analysis.get('y_true', []),
                                                               error_analysis.get('y_pred', [])))
                      if true != pred]

    if len(error_positions) > 10:
        # 计算滑动窗口错误率
        total_samples = len(error_analysis.get('y_true', []))
        error_rates = []

        for start in range(0, total_samples, window_size):
            end = min(start + window_size, total_samples)
            window_errors = sum(1 for pos in error_positions if start <= pos < end)
            window_rate = window_errors / (end - start)
            error_rates.append(window_rate)

        ax2.plot(range(len(error_rates)), error_rates, marker='o')
        ax2.set_title(f'滑动窗口错误率 (窗口大小={window_size})')
        ax2.set_xlabel('窗口编号')
        ax2.set_ylabel('错误率')
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, '错误样本过少\n无法进行趋势分析',
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    print("📊 错误分析图表已保存至:")
    print(f"  {save_path}")

def save_evaluation_report(metrics: Dict, error_analysis: Dict,
                          result_file: str, output_dir: str = 'evaluation_results'):
    """保存评估报告"""

    os.makedirs(output_dir, exist_ok=True)

    report = {
        'evaluation_summary': {
            'result_file': result_file,
            'total_samples': len(error_analysis.get('y_true', [])),
            'accuracy': metrics.get('accuracy', 0),
            'evaluation_time': str(error_analysis.get('timestamp', 'unknown'))
        },
        'metrics': metrics,
        'error_analysis': {
            'total_errors': error_analysis['total_errors'],
            'error_rate': error_analysis['total_errors'] / len(error_analysis.get('y_true', [])) if error_analysis.get('y_true') else 0,
            'error_types': error_analysis['error_types']
        }
    }

    # 保存JSON报告
    report_path = f"{output_dir}/evaluation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 保存详细错误样本
    if error_analysis['error_samples']:
        error_samples_path = f"{output_dir}/error_samples.json"
        with open(error_samples_path, 'w', encoding='utf-8') as f:
            json.dump(error_analysis['error_samples'], f, ensure_ascii=False, indent=2)

    print("📄 评估报告已保存:")
    print(f"  • 完整报告: {report_path}")
    if error_analysis['error_samples']:
        print(f"  • 错误样本: {error_samples_path}")

def print_evaluation_summary(metrics: Dict, error_analysis: Dict):
    """打印评估摘要"""

    print("\n" + "="*60)
    print("🎯 模型评估结果")
    print("="*60)

    print(f"🎯 准确率: {metrics.get('accuracy', 0):.4f}")

    print("\n📊 详细指标:")
    print(f"  精确率: {metrics.get('precision_macro', 0):.4f}")
    print(f"  召回率: {metrics.get('recall_macro', 0):.4f}")
    print(f"  F1值: {metrics.get('f1_macro', 0):.4f}")
    print(f"  精确率(微平均): {metrics.get('precision_micro', 0):.4f}")
    print(f"  召回率(微平均): {metrics.get('recall_micro', 0):.4f}")
    print(f"  F1值(微平均): {metrics.get('f1_micro', 0):.4f}")

    if metrics.get('auc'):
        print(f"  AUC: {metrics.get('auc', 0):.4f}")
    print("\n🏷️ 类别特定指标:")
    print(f"  • 类别0 (不相似) - 精确率: {metrics.get('precision_class_0', 0):.4f}, 召回率: {metrics.get('recall_class_0', 0):.4f}, F1: {metrics.get('f1_class_0', 0):.4f}")
    print(f"  • 类别1 (相似) - 精确率: {metrics.get('precision_class_1', 0):.4f}, 召回率: {metrics.get('recall_class_1', 0):.4f}, F1: {metrics.get('f1_class_1', 0):.4f}")

    print(f"\n❌ 错误分析:")
    print(f"  • 总错误数: {error_analysis['total_errors']}")
    print(".2f")
    print(f"  • FP (假正例): {error_analysis['error_types']['FP']} - 预测相似但实际不相似")
    print(f"  • FN (假负例): {error_analysis['error_types']['FN']} - 预测不相似但实际相似")

    # 基线对比
    baseline_acc = 0.764
    current_acc = metrics.get('accuracy', 0)
    improvement = current_acc - baseline_acc

    print(f"\n🏆 与基线对比:")
    print(".4f")
    print(".4f")
    if improvement > 0:
        print(".4f")
    elif improvement < 0:
        print(".4f")
    else:
        print("  • 与基线持平")

def main():
    """主评估函数"""

    print("📊 开始模型评估")
    print("=" * 60)

    # 检查结果文件
    result_files = ['enhanced_result.jsonl', 'enhanced_result.json', 'result.jsonl', 'result.json']

    result_file = None
    for file in result_files:
        if os.path.exists(file):
            result_file = file
            break

    if not result_file:
        print("❌ 未找到预测结果文件")
        print("请先运行推理脚本生成结果文件")
        print("尝试的文件:", result_files)
        return

    print(f"✅ 找到结果文件: {result_file}")

    # 加载测试标签
    print("\n📥 加载测试标签...")
    y_true = load_test_labels()
    if not y_true:
        return

    # 加载预测结果
    print("\n📥 加载预测结果...")
    y_pred, predictions_data = load_predictions(result_file)
    if not y_pred:
        return

    # 检查长度一致性
    if len(y_true) != len(y_pred):
        print(f"❌ 标签和预测长度不匹配: {len(y_true)} vs {len(y_pred)}")
        return

    print(f"✅ 数据加载完成: {len(y_true)} 个测试样本")

    # 计算指标
    print("\n🧮 计算评估指标...")
    metrics = calculate_metrics(y_true, y_pred)

    # 错误分析
    print("\n🔍 分析错误样本...")
    error_analysis = analyze_errors(y_true, y_pred, predictions_data)
    error_analysis['y_true'] = y_true  # 保存用于绘图
    error_analysis['y_pred'] = y_pred

    # 创建输出目录
    output_dir = 'evaluation_results'
    os.makedirs(output_dir, exist_ok=True)

    # 生成可视化
    print("\n📈 生成可视化图表...")
    plot_confusion_matrix(y_true, y_pred, f"{output_dir}/confusion_matrix.png")
    plot_error_analysis(error_analysis, f"{output_dir}/error_analysis.png")

    # 保存评估报告
    save_evaluation_report(metrics, error_analysis, result_file, output_dir)

    # 打印总结
    print_evaluation_summary(metrics, error_analysis)

    print("\n🎉 评估完成！")
    print(f"📁 结果保存在: {output_dir}/")

    # 提供建议
    accuracy = metrics.get('accuracy', 0)
    if accuracy >= 0.90:
        print("🏆 优秀！准确率达到90%以上，排名有望进入前20名！")
    elif accuracy >= 0.85:
        print("🎯 良好！准确率达到85%以上，有望进入前30名！")
    elif accuracy >= 0.80:
        print("👍 不错！准确率达到80%以上，继续优化！")
    else:
        print("📚 需要进一步优化，可以尝试调整Prompt或超参数")

if __name__ == '__main__':
    main()
