"""
金融文本相似度分类竞赛 - 脚本包
"""

# 在导入任何可能依赖datasets的库之前，先修复datasets兼容性问题
def fix_datasets_import():
    """修复datasets导入问题"""
    try:
        import datasets
        if not hasattr(datasets, 'LargeList'):
            # 尝试从features导入
            try:
                from datasets.features import Sequence
                datasets.LargeList = Sequence
                print("🔧 [scripts] 已自动修复datasets LargeList导入问题")
            except ImportError:
                # 创建基础兼容类
                class LargeList:
                    pass
                datasets.LargeList = LargeList
                print("🔧 [scripts] 已创建datasets LargeList兼容类")

        # 修复_FEATURE_TYPES
        from datasets.features import features
        if not hasattr(features, '_FEATURE_TYPES'):
            print("🔧 [scripts] _FEATURE_TYPES不存在，开始修复...")

            # 创建所有feature类型的字典
            _FEATURE_TYPES = {}
            for attr_name in dir(features):
                attr = getattr(features, attr_name)
                if (hasattr(attr, '__name__') and
                    hasattr(attr, '__module__') and
                    attr.__module__ == 'datasets.features.features' and
                    (attr_name.endswith('Type') or 'Array' in attr_name or 'Value' in attr_name or 'Class' in attr_name)):
                    _FEATURE_TYPES[attr_name] = attr

            # 手动添加一些重要的类型
            if hasattr(features, 'Sequence'):
                _FEATURE_TYPES['LargeList'] = features.Sequence

            # 将其添加到features模块
            features._FEATURE_TYPES = _FEATURE_TYPES
            print(f"🔧 [scripts] 已创建_FEATURE_TYPES ({len(_FEATURE_TYPES)}个类型)")

    except ImportError:
        pass

# 运行修复
fix_datasets_import()

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
