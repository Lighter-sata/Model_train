"""
Python启动时自动运行的补丁
修复pyarrow兼容性问题
"""

try:
    import pyarrow as pa
    import pyarrow.lib as palib

    # 在pyarrow顶级模块上应用补丁
    if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
        pa.PyExtensionType = pa.ExtensionType
        print("🔧 [sitecustomize] 已应用pyarrow顶级模块补丁")

    # 在pyarrow.lib模块上应用补丁
    if not hasattr(palib, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
        palib.PyExtensionType = pa.ExtensionType
        print("🔧 [sitecustomize] 已应用pyarrow.lib模块补丁")

    # 额外确保ExtensionType在lib中也可用
    if hasattr(pa, 'ExtensionType') and not hasattr(palib, 'ExtensionType'):
        palib.ExtensionType = pa.ExtensionType
        print("🔧 [sitecustomize] 已复制ExtensionType到pyarrow.lib")

except ImportError as e:
    print(f"🔧 [sitecustomize] pyarrow导入失败: {e}")
    pass
