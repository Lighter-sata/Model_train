#!/usr/bin/env python3
"""
魔搭平台依赖修复脚本
专门用于修复魔搭平台上的版本兼容性问题
"""

import subprocess
import sys

# 在导入任何可能依赖pyarrow的库之前，先应用补丁
try:
    import pyarrow as pa
    if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
        pa.PyExtensionType = pa.ExtensionType
        print("🔧 已自动应用pyarrow兼容性补丁")
except ImportError:
    pass

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

def fix_modelscope_dependencies():
    """修复魔搭平台的依赖问题"""

    print("🐰 魔搭平台 - 依赖修复脚本")
    print("=" * 60)

    print("📋 魔搭平台环境信息:")
    print(f"  Python版本: {sys.version}")

    # 首先应用补丁！
    print("\n🔧 第一步: 应用兼容性补丁...")
    patch_success = apply_pyarrow_patch()

    # 检查当前安装的包
    print("\n📦 检查当前安装...")
    try:
        import datasets
        print(f"  datasets: {datasets.__version__}")
    except ImportError:
        print("  datasets: 未安装")

    try:
        import pyarrow
        print(f"  pyarrow: {pyarrow.__version__}")
        # 检查PyExtensionType是否存在
        if hasattr(pyarrow, 'PyExtensionType'):
            print("  pyarrow PyExtensionType: ✅ 可用")
        else:
            print("  pyarrow PyExtensionType: ❌ 不可用 (版本兼容性问题)")
    except ImportError:
        print("  pyarrow: 未安装")

    # 方案1: 安装兼容版本的pyarrow
    print("\n🔧 方案1: 安装兼容版本的pyarrow...")
    success = run_command("pip install 'pyarrow>=11.0.0,<15.0.0' --force-reinstall --quiet", "安装兼容版本的pyarrow")

    # 方案2: 重新安装datasets
    if success:
        print("\n🔧 方案2: 重新安装datasets...")
        success = run_command("pip install 'datasets==2.14.0' --force-reinstall --quiet", "重新安装datasets 2.14.0")

    # 方案3: 如果仍有问题，尝试降级pyarrow到更旧版本
    if not success:
        print("\n🔧 方案3: 尝试降级pyarrow...")
        run_command("pip install 'pyarrow>=8.0.0,<12.0.0' --force-reinstall --quiet", "降级pyarrow到兼容版本")

        print("\n🔧 重新安装datasets...")
        run_command("pip install 'datasets==2.14.0' --force-reinstall --quiet", "重新安装datasets")

    # 方案4: 最后的清理重装方案
    print("\n🔧 方案4: 最后的清理重装方案...")
    run_command("pip uninstall -y datasets pyarrow", "卸载冲突包")
    run_command("pip install 'pyarrow>=8.0.0,<12.0.0' --quiet", "安装兼容的pyarrow版本")
    run_command("pip install 'datasets==2.14.0' --quiet", "安装datasets 2.14.0")

    # 方案5: 创建兼容性补丁
    print("\n🔧 方案5: 创建兼容性补丁...")
    try:
        # 检查是否需要打补丁
        import pyarrow as pa
        if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
            # 创建别名以实现兼容性
            pa.PyExtensionType = pa.ExtensionType
            print("✅ 已创建PyExtensionType兼容性补丁")

        # 重新尝试导入
        import datasets
        print(f"✅ datasets {datasets.__version__} 导入成功")

        # 测试基本功能
        from datasets import load_dataset
        print("✅ datasets基本功能正常")

        return True

    except Exception as e:
        print(f"❌ 补丁方案也失败: {e}")

    # 最终备用方案
    print("\n🔍 验证修复...")
    try:
        import datasets
        print(f"✅ datasets {datasets.__version__} 导入成功")

        # 测试基本功能
        from datasets import load_dataset
        print("✅ datasets基本功能正常")

        return True

    except Exception as e:
        print(f"❌ 修复失败: {e}")
        print("\n💡 备用方案:")
        print("1. 在代码中使用 --skip-env-check 参数")
        print("2. python main.py --skip-env-check --step analysis")
        print("3. 或者直接运行: python scripts/data_processor.py download")
        print("4. 手动安装: pip install 'pyarrow>=8.0.0,<12.0.0' 'datasets==2.14.0'")

        return False

def main():
    """主函数"""

    print("此脚本将修复魔搭平台上的依赖兼容性问题。")
    response = input("是否继续？(y/N): ").strip().lower()

    if response in ['y', 'yes']:
        success = fix_modelscope_dependencies()

        if success:
            print("\n🎉 依赖修复完成！现在可以运行测试:")
            print("python test_setup.py")
        else:
            print("\n❌ 自动修复失败，请尝试手动修复。")
    else:
        print("修复已取消。")

if __name__ == '__main__':
    # 检查是否在魔搭平台
    import os
    if os.path.exists('/mnt/workspace'):
        print("检测到魔搭平台环境，自动开始修复...")
        # 在魔搭平台，首先应用补丁
        patch_result = apply_pyarrow_patch()
        if patch_result:
            fix_modelscope_dependencies()
        else:
            print("❌ 补丁应用失败，退出")
    else:
        main()
