#!/usr/bin/env python3
"""
测试pyarrow补丁是否正确应用
"""

def test_pyarrow_patch():
    """测试pyarrow补丁"""
    print("🔍 测试pyarrow补丁状态")
    print("-" * 40)

    try:
        import pyarrow as pa
        import pyarrow.lib as palib

        print("✅ pyarrow导入成功"        print(f"  版本: {pa.__version__}")

        # 测试顶级模块
        if hasattr(pa, 'PyExtensionType'):
            print("✅ pyarrow.PyExtensionType 存在")
        else:
            print("❌ pyarrow.PyExtensionType 不存在")

        if hasattr(pa, 'ExtensionType'):
            print("✅ pyarrow.ExtensionType 存在")
        else:
            print("❌ pyarrow.ExtensionType 不存在")

        # 测试lib模块
        if hasattr(palib, 'PyExtensionType'):
            print("✅ pyarrow.lib.PyExtensionType 存在")
        else:
            print("❌ pyarrow.lib.PyExtensionType 不存在")

        if hasattr(palib, 'ExtensionType'):
            print("✅ pyarrow.lib.ExtensionType 存在")
        else:
            print("❌ pyarrow.lib.ExtensionType 不存在")

        # 检查是否指向同一个对象
        if hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
            if pa.PyExtensionType is pa.ExtensionType:
                print("✅ pyarrow.PyExtensionType 指向 ExtensionType")
            else:
                print("⚠️  pyarrow.PyExtensionType 与 ExtensionType 不同")

        if hasattr(palib, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
            if palib.PyExtensionType is pa.ExtensionType:
                print("✅ pyarrow.lib.PyExtensionType 指向 pyarrow.ExtensionType")
            else:
                print("⚠️  pyarrow.lib.PyExtensionType 与 pyarrow.ExtensionType 不同")

        return True

    except ImportError as e:
        print(f"❌ pyarrow导入失败: {e}")
        return False

def test_datasets_import():
    """测试datasets导入"""
    print("\n🔍 测试datasets导入")
    print("-" * 40)

    try:
        import datasets
        print(f"✅ datasets导入成功，版本: {datasets.__version__}")

        # 测试基本功能
        from datasets import load_dataset
        print("✅ datasets.load_dataset 可用")

        # 测试features模块（这是出错的地方）
        from datasets.features import Features
        print("✅ datasets.features.Features 可用")

        return True

    except Exception as e:
        print(f"❌ datasets导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🐰 PyArrow补丁测试工具")
    print("=" * 50)

    # 测试补丁
    patch_ok = test_pyarrow_patch()

    # 测试datasets
    datasets_ok = test_datasets_import()

    print("\n" + "=" * 50)
    if patch_ok and datasets_ok:
        print("🎉 所有测试通过！补丁工作正常。")
        return True
    else:
        print("❌ 测试失败，需要进一步修复。")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
