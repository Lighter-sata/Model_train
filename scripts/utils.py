#!/usr/bin/env python3
"""
金融文本相似度分类竞赛 - 工具函数模块
包含输出清洗、后处理、数据处理等通用函数
"""

import re
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import jieba
from swift.utils import read_from_jsonl, write_to_jsonl

def clean_prediction_output(response: str) -> str:
    """
    清洗模型输出，只保留预测结果

    Args:
        response: 模型原始输出

    Returns:
        清洗后的预测结果字符串
    """
    if not response:
        return "0"

    # 移除所有空白字符
    response = response.strip()

    # 直接匹配数字0或1
    if response in ['0', '1']:
        return response

    # 移除可能的额外内容，如"输出:"、"结果:"等
    patterns_to_remove = [
        r'^.*?(?:输出|结果|判断结果|类别|预测)[:：]\s*',
        r'^.*?(?:我认为|答案是|预测为)[:：]?\s*',
        r'^.*?[:：]\s*'
    ]

    for pattern in patterns_to_remove:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            response = response[match.end():].strip()
            break

    # 再次检查是否为纯数字
    if response in ['0', '1']:
        return response

    # 提取第一个数字字符
    digits = re.findall(r'[01]', response)
    if digits:
        return digits[0]

    # 基于关键词判断
    response_lower = response.lower()
    positive_keywords = ['相似', '相同', '类似', '一致', '是', 'yes', 'true']
    negative_keywords = ['不同', '不相似', '不相同', '差异', '不是', 'no', 'false']

    positive_score = sum(1 for word in positive_keywords if word in response_lower)
    negative_score = sum(1 for word in negative_keywords if word in response_lower)

    if positive_score > negative_score:
        return "1"
    elif negative_score > positive_score:
        return "0"
    else:
        # 默认返回"0"（基于数据集分布，类别0更多）
        return "0"

def batch_clean_predictions(predictions: List[Dict]) -> List[Dict]:
    """
    批量清洗预测结果

    Args:
        predictions: 预测结果列表

    Returns:
        清洗后的预测结果列表
    """
    cleaned_predictions = []

    for pred in predictions:
        original_response = pred.get('response', '')
        cleaned_response = clean_prediction_output(original_response)

        cleaned_pred = pred.copy()
        cleaned_pred['original_response'] = original_response
        cleaned_pred['response'] = cleaned_response
        cleaned_pred['prediction'] = int(cleaned_response) if cleaned_response.isdigit() else 0

        cleaned_predictions.append(cleaned_pred)

    return cleaned_predictions

def calculate_text_similarity(text1: str, text2: str) -> Dict[str, float]:
    """
    计算两段文本的相似度特征

    Args:
        text1: 文本1
        text2: 文本2

    Returns:
        相似度特征字典
    """
    features = {}

    # Jaccard相似度（字符级别）
    set1 = set(text1)
    set2 = set(text2)
    features['jaccard_char'] = len(set1 & set2) / len(set1 | set2) if len(set1 | set2) > 0 else 0

    # Jaccard相似度（词级别）
    words1 = list(jieba.cut(text1))
    words2 = list(jieba.cut(text2))
    set1_word = set(words1)
    set2_word = set(words2)
    features['jaccard_word'] = len(set1_word & set2_word) / len(set1_word | set2_word) if len(set1_word | set2_word) > 0 else 0

    # 长度特征
    features['len1'] = len(text1)
    features['len2'] = len(text2)
    features['len_diff'] = abs(len(text1) - len(text2))
    features['len_ratio'] = min(len(text1), len(text2)) / max(len(text1), len(text2)) if max(len(text1), len(text2)) > 0 else 0

    # 词数特征
    features['word_count1'] = len(words1)
    features['word_count2'] = len(words2)
    features['word_count_diff'] = abs(len(words1) - len(words2))

    # 公共词数
    features['common_words'] = len(set1_word & set2_word)

    return features

def analyze_prediction_errors(predictions: List[Dict], labels: List[int]) -> Dict[str, Any]:
    """
    分析预测错误模式

    Args:
        predictions: 预测结果列表
        labels: 真实标签列表

    Returns:
        错误分析结果
    """
    error_analysis = {
        'total_samples': len(predictions),
        'total_errors': 0,
        'error_rate': 0,
        'error_types': {'FP': 0, 'FN': 0},
        'error_patterns': defaultdict(int),
        'error_samples': []
    }

    for i, (pred, true_label) in enumerate(zip(predictions, labels)):
        pred_label = pred.get('prediction', 0)

        if pred_label != true_label:
            error_analysis['total_errors'] += 1

            # 错误类型
            if true_label == 0 and pred_label == 1:
                error_type = 'FP'  # 假正例
            elif true_label == 1 and pred_label == 0:
                error_type = 'FN'  # 假负例
            else:
                error_type = 'other'

            error_analysis['error_types'][error_type] += 1

            # 提取文本进行模式分析
            query = pred.get('query', '')
            text1_match = re.search(r'句子1:\s*(.*?)(?:\n|$)', query, re.DOTALL)
            text2_match = re.search(r'句子2:\s*(.*?)(?:\n|$)', query, re.DOTALL)

            if text1_match and text2_match:
                text1 = text1_match.group(1).strip()
                text2 = text2_match.group(1).strip()

                # 计算相似度特征
                similarity_features = calculate_text_similarity(text1, text2)

                # 简单错误模式识别
                if similarity_features['jaccard_char'] > 0.8 and error_type == 'FN':
                    error_analysis['error_patterns']['high_similarity_FN'] += 1
                elif similarity_features['jaccard_char'] < 0.2 and error_type == 'FP':
                    error_analysis['error_patterns']['low_similarity_FP'] += 1

                # 保存错误样本（最多保存20个）
                if len(error_analysis['error_samples']) < 20:
                    error_sample = {
                        'index': i,
                        'text1': text1,
                        'text2': text2,
                        'true_label': true_label,
                        'pred_label': pred_label,
                        'error_type': error_type,
                        'similarity': similarity_features
                    }
                    error_analysis['error_samples'].append(error_sample)

    error_analysis['error_rate'] = error_analysis['total_errors'] / error_analysis['total_samples']

    return error_analysis

def create_enhanced_prompt(text1: str, text2: str, similarity_features: Optional[Dict] = None) -> str:
    """
    创建增强的Prompt，包含相似度特征信息

    Args:
        text1: 句子1
        text2: 句子2
        similarity_features: 相似度特征（可选）

    Returns:
        增强的Prompt
    """
    prompt = f"""请判断下面两句话在金融语境下是否表达相同的语义含义。

句子1: {text1}
句子2: {text2}

"""

    # 如果有相似度特征，添加到prompt中
    if similarity_features:
        prompt += f"""文本相似度特征：
- 字符级Jaccard相似度: {similarity_features.get('jaccard_char', 0):.3f}
- 词级Jaccard相似度: {similarity_features.get('jaccard_word', 0):.3f}
- 长度差异: {similarity_features.get('len_diff', 0)} 字符
- 公共词数: {similarity_features.get('common_words', 0)} 个

"""

    prompt += """要求：
- 如果两句话含义相同或非常相似，输出1
- 如果两句话含义不同或不相似，输出0
- 只输出数字0或1，不要输出其他内容

判断结果: """

    return prompt

def save_checkpoint_info(output_dir: str, checkpoint_path: str, metrics: Dict[str, Any]):
    """
    保存checkpoint信息和性能指标

    Args:
        output_dir: 输出目录
        checkpoint_path: checkpoint路径
        metrics: 性能指标
    """
    os.makedirs(output_dir, exist_ok=True)

    checkpoint_info = {
        'checkpoint_path': checkpoint_path,
        'step': extract_step_from_checkpoint(checkpoint_path),
        'metrics': metrics,
        'timestamp': str(os.times())
    }

    info_path = os.path.join(output_dir, 'checkpoint_info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_info, f, ensure_ascii=False, indent=2)

def extract_step_from_checkpoint(checkpoint_path: str) -> Optional[int]:
    """
    从checkpoint路径中提取训练步数

    Args:
        checkpoint_path: checkpoint路径

    Returns:
        训练步数
    """
    import re
    match = re.search(r'checkpoint-(\d+)', checkpoint_path)
    return int(match.group(1)) if match else None

def load_best_checkpoint(output_dir: str, metric: str = 'accuracy') -> Optional[str]:
    """
    加载最佳checkpoint

    Args:
        output_dir: 输出目录
        metric: 用于选择最佳checkpoint的指标

    Returns:
        最佳checkpoint路径
    """
    info_path = os.path.join(output_dir, 'checkpoint_info.json')

    if not os.path.exists(info_path):
        return None

    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            checkpoint_info = json.load(f)

        # 简单实现：返回最新的checkpoint
        # 可以根据metrics扩展为更复杂的选择逻辑
        return checkpoint_info.get('checkpoint_path')

    except Exception as e:
        print(f"加载checkpoint信息失败: {e}")
        return None

def ensemble_predictions(prediction_files: List[str], method: str = 'majority_vote') -> List[Dict]:
    """
    对多个预测结果进行集成

    Args:
        prediction_files: 预测结果文件列表
        method: 集成方法 ('majority_vote', 'average', 'weighted')

    Returns:
        集成后的预测结果
    """
    if not prediction_files:
        return []

    all_predictions = []
    for file in prediction_files:
        if os.path.exists(file):
            preds = read_from_jsonl(file)
            all_predictions.append(preds)

    if not all_predictions:
        return []

    # 确保所有预测文件有相同数量的样本
    num_samples = len(all_predictions[0])
    if not all(preds and len(preds) == num_samples for preds in all_predictions):
        print("预测文件长度不一致，无法进行集成")
        return []

    ensemble_results = []

    for sample_idx in range(num_samples):
        votes = []
        sample_data = all_predictions[0][sample_idx].copy()

        # 收集所有模型的预测
        for preds in all_predictions:
            pred = preds[sample_idx]
            response = pred.get('response', '0')
            prediction = clean_prediction_output(response)
            votes.append(int(prediction) if prediction.isdigit() else 0)

        # 多数投票
        final_prediction = 1 if sum(votes) > len(votes) / 2 else 0

        sample_data['original_responses'] = [preds[sample_idx].get('response', '0') for preds in all_predictions]
        sample_data['votes'] = votes
        sample_data['response'] = str(final_prediction)
        sample_data['prediction'] = final_prediction
        sample_data['vote_count'] = len(votes)

        ensemble_results.append(sample_data)

    return ensemble_results

def validate_dataset_integrity(dataset_path: str) -> Dict[str, Any]:
    """
    验证数据集完整性

    Args:
        dataset_path: 数据集路径

    Returns:
        验证结果
    """
    validation_results = {
        'is_valid': True,
        'issues': [],
        'stats': {}
    }

    try:
        data = read_from_jsonl(dataset_path)
        validation_results['stats']['total_samples'] = len(data)

        if not data:
            validation_results['is_valid'] = False
            validation_results['issues'].append("数据集为空")
            return validation_results

        # 检查必要字段
        required_fields = ['text1', 'text2', 'label']
        missing_fields = []

        for i, sample in enumerate(data):
            for field in required_fields:
                if field not in sample:
                    missing_fields.append(f"样本{i}缺少字段: {field}")

            # 检查字段内容
            if 'text1' in sample and not sample['text1'].strip():
                validation_results['issues'].append(f"样本{i}的text1为空")

            if 'text2' in sample and not sample['text2'].strip():
                validation_results['issues'].append(f"样本{i}的text2为空")

            if 'label' in sample and sample['label'] not in [0, 1, None]:
                validation_results['issues'].append(f"样本{i}的label无效: {sample['label']}")

        if missing_fields:
            validation_results['is_valid'] = False
            validation_results['issues'].extend(missing_fields)

        # 统计信息
        labels = [s.get('label') for s in data if s.get('label') is not None]
        validation_results['stats']['valid_labels'] = len(labels)
        validation_results['stats']['label_distribution'] = dict(Counter(labels))

    except Exception as e:
        validation_results['is_valid'] = False
        validation_results['issues'].append(f"读取数据集失败: {e}")

    return validation_results
