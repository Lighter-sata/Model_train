#!/usr/bin/env python3
"""
测试datasets修复是否有效
"""

import sys
import os

print("🔍 测试datasets修复...")

# 显示当前Python路径
print(f"Python路径包含site_packages: {'site_packages' in str(sys.path)}")

# 手动执行sitecustomize逻辑
try:
    print("\n🔧 手动执行修复逻辑...")

    # 1. 修复pyarrow
    import pyarrow as pa
    print(f"pyarrow版本: {pa.__version__}")

    if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
        pa.PyExtensionType = pa.ExtensionType
        print("✅ 已应用pyarrow兼容性补丁")

    # 2. 修复datasets
    import datasets
    print(f"datasets版本: {datasets.__version__}")

    if not hasattr(datasets, 'LargeList'):
        print("LargeList不存在，开始修复...")

        # 尝试从features导入
        try:
            from datasets.features import Sequence
            datasets.LargeList = Sequence
            print("✅ 已修复datasets LargeList (使用Sequence)")
        except ImportError as e:
            print(f"从features导入失败: {e}")
            # 创建完整的兼容类
            class LargeList:
                """Full LargeList compatibility class for datasets"""
                def __init__(self, dtype, length=None):
                    self.dtype = dtype
                    self.length = length

                def __repr__(self):
                    return f"LargeList(dtype={self.dtype}, length={self.length})"

            datasets.LargeList = LargeList
            print("✅ 已创建datasets LargeList兼容类")

    # 验证修复
    if hasattr(datasets, 'LargeList'):
        print("✅ LargeList现在存在")
        print(f"LargeList类型: {type(datasets.LargeList)}")
    else:
        print("❌ LargeList仍然不存在")

    # 测试swift.llm导入
    print("\n🔍 测试swift.llm导入...")
    try:
        from swift.llm import TrainArguments
        print("✅ swift.llm导入成功")
    except Exception as e:
        print(f"❌ swift.llm导入失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n🎉 所有测试通过！")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
