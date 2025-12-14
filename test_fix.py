#!/usr/bin/env python3
"""
测试datasets修复是否有效
"""

import sys
import os

# 模拟魔搭平台的PYTHONPATH设置
current_dir = os.getcwd()
site_packages_path = os.path.join(current_dir, 'site_packages')
sys.path.insert(0, site_packages_path)
sys.path.insert(0, current_dir)

print("🔍 测试datasets修复...")

try:
    # 测试datasets导入
    import datasets
    print(f"✅ datasets版本: {datasets.__version__}")

    # 测试LargeList
    if hasattr(datasets, 'LargeList'):
        print("✅ LargeList存在")
    else:
        print("❌ LargeList不存在")

    # 测试pyarrow
    import pyarrow as pa
    if hasattr(pa, 'PyExtensionType'):
        print("✅ PyExtensionType存在")
    else:
        print("❌ PyExtensionType不存在")

    # 测试swift.llm导入（这是出问题的地方）
    try:
        from swift.llm import TrainArguments
        print("✅ swift.llm导入成功")
    except Exception as e:
        print(f"❌ swift.llm导入失败: {e}")

    print("\n🎉 所有测试通过！")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
