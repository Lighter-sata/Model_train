"""
Python启动时自动运行的补丁
修复pyarrow兼容性问题
"""

try:
    import pyarrow as pa
    if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
        pa.PyExtensionType = pa.ExtensionType
        print("🔧 [sitecustomize] 已应用pyarrow兼容性补丁")
except ImportError:
    pass
