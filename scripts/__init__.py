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

        # 修复exceptions模块
        if not hasattr(datasets, 'exceptions'):
            print("🔧 [scripts] exceptions模块不存在，开始修复...")
            import types
            exceptions_module = types.ModuleType('datasets.exceptions')

            exception_classes = [
                'DatasetNotFoundError', 'DatasetBuildError', 'DatasetGenerationError',
                'DatasetValidationError', 'NonMatchingChecksumError', 'DatasetInfoError',
                'DataFilesNotFoundError', 'EmptyDatasetError', 'ManualDownloadError',
                'DatasetNotImplementedError', 'DatasetOnlineError', 'DatasetOfflineError',
                'StreamingError', 'CorruptedFileError', 'SplitNotFoundError'
            ]

            for exc_name in exception_classes:
                exc_class = type(exc_name, (Exception,), {})
                setattr(exceptions_module, exc_name, exc_class)

            datasets.exceptions = exceptions_module
            import sys
            sys.modules['datasets.exceptions'] = exceptions_module
            print("🔧 [scripts] 已创建exceptions模块")

        # 修复HubDatasetModuleFactoryWithParquetExport
        from datasets import load
        if not hasattr(load, 'HubDatasetModuleFactoryWithParquetExport'):
            print("🔧 [scripts] HubDatasetModuleFactoryWithParquetExport不存在，开始修复...")
            from datasets.load import HubDatasetModuleFactoryWithoutScript

            class HubDatasetModuleFactoryWithParquetExport(HubDatasetModuleFactoryWithoutScript):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.supports_parquet_export = True

            load.HubDatasetModuleFactoryWithParquetExport = HubDatasetModuleFactoryWithParquetExport
            print("🔧 [scripts] 已创建HubDatasetModuleFactoryWithParquetExport兼容类")

        # 修复_get_importable_file_path
        if not hasattr(load, '_get_importable_file_path'):
            print("🔧 [scripts] _get_importable_file_path不存在，开始修复...")

            def _get_importable_file_path(dataset_name, filename, use_auth_token=None):
                return f'{dataset_name}/{filename}'

            load._get_importable_file_path = _get_importable_file_path
            print("🔧 [scripts] 已创建_get_importable_file_path兼容函数")

        # 修复resolve_trust_remote_code
        if not hasattr(load, 'resolve_trust_remote_code'):
            print("🔧 [scripts] resolve_trust_remote_code不存在，开始修复...")

            def resolve_trust_remote_code(trust_remote_code, repo_id=None):
                return trust_remote_code

            load.resolve_trust_remote_code = resolve_trust_remote_code
            print("🔧 [scripts] 已创建resolve_trust_remote_code兼容函数")

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
