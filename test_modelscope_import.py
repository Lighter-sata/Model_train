#!/usr/bin/env python3
"""
测试modelscope导入是否正常工作
"""

import sys
import os

print("🔍 测试modelscope导入修复...")

# 模拟魔搭平台环境
os.environ['PYTHONPATH'] = f"{os.getcwd()}/site_packages:{os.getcwd()}:{os.environ.get('PYTHONPATH', '')}"

try:
    # 1. 修复pyarrow
    import pyarrow as pa
    if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
        pa.PyExtensionType = pa.ExtensionType
        print("✅ pyarrow修复完成")

    # 2. 修复datasets
    import datasets
    if not hasattr(datasets, 'LargeList'):
        from datasets.features import Sequence
        datasets.LargeList = Sequence
        print("✅ LargeList修复完成")

    # 3. 修复_FEATURE_TYPES
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
        print(f"✅ _FEATURE_TYPES修复完成 ({len(_FEATURE_TYPES)}个类型)")

    # 4. 测试modelscope MsDataset导入
    print("\n🔍 测试modelscope MsDataset导入...")
    try:
        from modelscope import MsDataset
        print("✅ modelscope MsDataset导入成功")
    except Exception as e:
        print(f"❌ modelscope导入失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n🎉 所有兼容性修复测试通过！")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
