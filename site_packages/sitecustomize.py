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

except Exception as e:
    print(f"🔧 [sitecustomize] datasets预修复失败: {e}")

print("🔧 [sitecustomize] 预修复完成")
