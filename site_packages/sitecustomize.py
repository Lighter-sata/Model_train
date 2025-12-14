"""
Python启动时自动运行的补丁
修复datasets兼容性问题
"""

import sys

try:
    import datasets
    import pyarrow as pa

    # 修复PyArrow兼容性
    if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
        pa.PyExtensionType = pa.ExtensionType
        print("🔧 [sitecustomize] 已应用pyarrow兼容性补丁")

    # 修复datasets LargeList问题
    if not hasattr(datasets, 'LargeList'):
        try:
            from datasets.features import Sequence
            datasets.LargeList = Sequence
            print("🔧 [sitecustomize] 已修复datasets LargeList (使用Sequence)")
        except ImportError:
            class LargeList:
                """Basic LargeList compatibility class"""
                pass
            datasets.LargeList = LargeList
            print("🔧 [sitecustomize] 已创建datasets LargeList兼容类")

except ImportError as e:
    print(f"🔧 [sitecustomize] 导入失败: {e}")
    pass

print("🔧 [sitecustomize] datasets兼容性修复完成")
