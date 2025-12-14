"""
金融文本相似度分类竞赛 - 脚本包
"""

from .data_processor import download_dataset_files, analyze_dataset
from .model_trainer import run_training, run_inference
from .evaluate import main as evaluate_main
from .utils import clean_prediction_output, calculate_text_similarity

__version__ = "1.0.0"
__all__ = [
    'download_dataset_files',
    'analyze_dataset',
    'run_training',
    'run_inference',
    'evaluate_main',
    'clean_prediction_output',
    'calculate_text_similarity'
]
