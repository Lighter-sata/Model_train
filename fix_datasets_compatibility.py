#!/usr/bin/env python3
"""
修复datasets与modelscope的版本兼容性问题
处理LargeList导入错误
"""

import subprocess
import sys
import os

def apply_datasets_patch():
    """应用datasets兼容性补丁"""
    try:
        import datasets
        print(f"当前datasets版本: {datasets.__version__}")

        # 检查LargeList的可用性
        largelist_found = False

        # 方法1: 直接从datasets导入
        try:
            from datasets import LargeList
            print("✅ LargeList found in datasets")
            largelist_found = True
        except ImportError:
            print("❌ LargeList NOT found in datasets")

        # 方法2: 从datasets.features导入
        if not largelist_found:
            try:
                from datasets.features import LargeList
                print("✅ LargeList found in datasets.features")
                # 如果在features中，将其添加到datasets顶级模块
                if not hasattr(datasets, 'LargeList'):
                    datasets.LargeList = LargeList
                    print("✅ LargeList added to datasets module")
                largelist_found = True
            except ImportError:
                print("❌ LargeList NOT found in datasets.features")

        # 方法3: 检查是否有其他可能的名称
        if not largelist_found:
            possible_names = ['LargeList', 'Sequence', 'Array']
            for name in possible_names:
                if hasattr(datasets, name):
                    print(f"ℹ️  Found alternative: {name}")
                try:
                    from datasets.features import __dict__ as features_dict
                    if name in features_dict:
                        print(f"ℹ️  Found {name} in datasets.features")
                except:
                    pass

        return largelist_found

    except ImportError as e:
        print(f"❌ 无法导入datasets: {e}")
        return False

def run_command(cmd, desc=""):
    """运行命令"""
    print(f"🔧 {desc}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {e.stderr[:200]}...")
        return False

def fix_datasets_compatibility():
    """修复datasets兼容性问题"""
    print("🔧 修复datasets与modelscope兼容性")
    print("=" * 50)

    # 首先应用补丁
    patch_success = apply_datasets_patch()

    if patch_success:
        print("\n✅ datasets兼容性检查通过")
        return True

    print("\n🔄 尝试安装兼容版本...")

    # 尝试不同的datasets版本
    versions_to_try = [
        "2.14.0",  # 当前版本
        "2.15.0",  # 稍新版本
        "2.13.0",  # 稍旧版本
        "2.16.0",  # 更新的版本
    ]

    for version in versions_to_try:
        print(f"\n🔄 尝试datasets {version}...")
        success = run_command(f"pip install 'datasets=={version}' --force-reinstall --quiet", f"安装datasets {version}")

        if success:
            # 重新测试补丁
            if apply_datasets_patch():
                print(f"✅ datasets {version} 兼容！")
                return True

    # 如果都没成功，尝试更激进的方法
    print("\n🔄 尝试更激进的修复方法...")

    # 卸载并重新安装相关包
    run_command("pip uninstall -y datasets modelscope ms-swift", "卸载冲突包")
    run_command("pip install 'datasets>=2.14.0,<3.0.0' 'modelscope>=1.30.0' 'ms-swift<3.10'", "重新安装兼容版本")

    # 最后测试
    final_test = apply_datasets_patch()
    if final_test:
        print("✅ 激进修复成功！")
        return True

    print("❌ 所有修复方法都失败了")
    print("\n💡 建议手动解决:")
    print("1. 检查modelscope版本要求")
    print("2. 尝试: pip install 'datasets>=2.10.0,<2.17.0'")
    print("3. 或使用: --skip-env-check 参数跳过环境检查")

    return False

def test_modelscope_import():
    """测试modelscope导入"""
    print("\n🔍 测试modelscope导入...")
    try:
        from modelscope import MsDataset
        print("✅ modelscope.MsDataset 导入成功")
        return True
    except Exception as e:
        print(f"❌ modelscope导入失败: {e}")
        return False

def test_swift_import():
    """测试swift导入"""
    print("\n🔍 测试swift导入...")
    try:
        from swift.llm import TrainArguments
        print("✅ swift.llm 导入成功")
        return True
    except Exception as e:
        print(f"❌ swift导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🐰 Datasets兼容性修复工具")
    print("=" * 50)

    # 修复datasets兼容性
    datasets_ok = fix_datasets_compatibility()

    # 测试相关导入
    modelscope_ok = test_modelscope_import()
    swift_ok = test_swift_import()

    print("\n" + "=" * 50)
    if datasets_ok and modelscope_ok and swift_ok:
        print("🎉 所有兼容性问题已修复！")
        return True
    else:
        print("❌ 仍存在兼容性问题")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
