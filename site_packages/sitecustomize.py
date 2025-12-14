"""
Python启动时自动运行的补丁
修复datasets兼容性问题
在任何其他导入之前执行
"""

print("🔧 [sitecustomize] 开始修复datasets兼容性...")

# 1. 在sys导入后立即修复pyarrow
import sys

# 直接在pyarrow模块级别修复
try:
    # 尝试预先修复pyarrow
    import importlib.util
    pa_spec = importlib.util.find_spec('pyarrow')
    if pa_spec:
        print("🔧 [sitecustomize] 找到pyarrow模块")

        # 手动加载并修复pyarrow
        pa = importlib.util.module_from_spec(pa_spec)
        pa_spec.loader.exec_module(pa)

        # 修复PyExtensionType
        if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
            pa.PyExtensionType = pa.ExtensionType
            print("🔧 [sitecustomize] 已修复pyarrow.PyExtensionType")

        if hasattr(pa, 'lib') and not hasattr(pa.lib, 'PyExtensionType') and hasattr(pa.lib, 'ExtensionType'):
            pa.lib.PyExtensionType = pa.lib.ExtensionType
            print("🔧 [sitecustomize] 已修复pyarrow.lib.PyExtensionType")

        # 将修复后的pyarrow添加到sys.modules
        sys.modules['pyarrow'] = pa

except Exception as e:
    print(f"🔧 [sitecustomize] pyarrow预修复失败: {e}")

# 2. 修复datasets
try:
    # 手动创建datasets.LargeList
    import importlib.util
    ds_spec = importlib.util.find_spec('datasets')
    if ds_spec:
        print("🔧 [sitecustomize] 找到datasets模块")

        # 预先设置LargeList
        ds = importlib.util.module_from_spec(ds_spec)

        # 创建LargeList类
        class LargeList:
            """Full LargeList compatibility class for datasets"""
            def __init__(self, dtype, length=None):
                self.dtype = dtype
                self.length = length

            def __repr__(self):
                return f"LargeList(dtype={self.dtype}, length={self.length})"

        ds.LargeList = LargeList
        print("🔧 [sitecustomize] 已预设datasets.LargeList")

        # 添加到sys.modules
        sys.modules['datasets'] = ds

        # 预设_FEATURE_TYPES
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
            print("🔧 [sitecustomize] 已预设_FEATURE_TYPES")

        # 预设exceptions模块
        if not hasattr(ds, 'exceptions'):
            import types
            exceptions_module = types.ModuleType('datasets.exceptions')

            # 定义常用的异常类
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

            ds.exceptions = exceptions_module
            sys.modules['datasets.exceptions'] = exceptions_module
            print("🔧 [sitecustomize] 已预设exceptions模块")

            # 预设HubDatasetModuleFactoryWithParquetExport
            from datasets import load
            if not hasattr(load, 'HubDatasetModuleFactoryWithParquetExport'):
                from datasets.load import HubDatasetModuleFactoryWithoutScript

                class HubDatasetModuleFactoryWithParquetExport(HubDatasetModuleFactoryWithoutScript):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.supports_parquet_export = True

                load.HubDatasetModuleFactoryWithParquetExport = HubDatasetModuleFactoryWithParquetExport
                print("🔧 [sitecustomize] 已预设HubDatasetModuleFactoryWithParquetExport")

                # 预设_get_importable_file_path
                if not hasattr(load, '_get_importable_file_path'):
                    def _get_importable_file_path(dataset_name, filename, use_auth_token=None):
                        return f'{dataset_name}/{filename}'

                    load._get_importable_file_path = _get_importable_file_path
                    print("🔧 [sitecustomize] 已预设_get_importable_file_path")

                    # 预设resolve_trust_remote_code
                    if not hasattr(load, 'resolve_trust_remote_code'):
                        def resolve_trust_remote_code(trust_remote_code, repo_id=None):
                            return trust_remote_code

                        load.resolve_trust_remote_code = resolve_trust_remote_code
                        print("🔧 [sitecustomize] 已预设resolve_trust_remote_code")

except Exception as e:
    print(f"🔧 [sitecustomize] datasets预修复失败: {e}")

print("🔧 [sitecustomize] 预修复完成")
