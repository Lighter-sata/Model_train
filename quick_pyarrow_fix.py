#!/usr/bin/env python3
"""
快速修复pyarrow兼容性问题
在datasets导入前运行此脚本
"""

import sys
import os

def apply_pyarrow_patch():
    """应用pyarrow兼容性补丁"""
    try:
        import pyarrow as pa

        # 检查是否需要补丁
        if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
            # 在较新版本的pyarrow中，PyExtensionType已被重命名为ExtensionType
            pa.PyExtensionType = pa.ExtensionType
            print("✅ 已应用pyarrow兼容性补丁 (PyExtensionType -> ExtensionType)")
            return True
        elif hasattr(pa, 'PyExtensionType'):
            print("✅ pyarrow版本兼容，无需补丁")
            return True
        else:
            print("❌ pyarrow缺少必要的ExtensionType类")
            return False

    except ImportError:
        print("❌ 无法导入pyarrow")
        return False

def test_datasets_import():
    """测试datasets导入"""
    try:
        import datasets
        print(f"✅ datasets {datasets.__version__} 导入成功")

        # 测试基本功能
        from datasets import load_dataset
        print("✅ datasets基本功能正常")
        return True

    except Exception as e:
        print(f"❌ datasets导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 快速修复pyarrow兼容性问题")
    print("-" * 40)

    # 应用补丁
    patch_success = apply_pyarrow_patch()

    if patch_success:
        # 测试导入
        import_success = test_datasets_import()

        if import_success:
            print("\n🎉 修复成功！现在可以正常使用datasets了。")
            return True
        else:
            print("\n❌ 补丁无效，可能需要手动修复。")
            return False
    else:
        print("\n❌ 无法应用补丁。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
