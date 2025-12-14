#!/usr/bin/env python3
"""
魔搭平台依赖修复脚本
专门用于修复魔搭平台上的版本兼容性问题
"""

import subprocess
import sys

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

def fix_modelscope_dependencies():
    """修复魔搭平台的依赖问题"""

    print("🐰 魔搭平台 - 依赖修复脚本")
    print("=" * 60)

    print("📋 魔搭平台环境信息:")
    print(f"  Python版本: {sys.version}")

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
    except ImportError:
        print("  pyarrow: 未安装")

    # 方案1: 降级datasets到兼容版本
    print("\n🔧 方案1: 修复datasets版本...")
    success = run_command("pip install 'datasets==2.14.0' --force-reinstall --quiet", "降级datasets到2.14.0")

    if not success:
        # 方案2: 升级pyarrow
        print("\n🔧 方案2: 升级pyarrow...")
        run_command("pip install --upgrade pyarrow --quiet", "升级pyarrow")

        # 重新尝试安装datasets
        print("\n🔧 重新安装datasets...")
        run_command("pip install 'datasets>=2.14.0,<3.0.0' --quiet", "安装兼容版本的datasets")

    # 方案3: 清理并重新安装
    print("\n🔧 方案3: 清理并重新安装...")
    run_command("pip uninstall -y datasets pyarrow", "卸载冲突包")
    run_command("pip install pyarrow --quiet", "重新安装pyarrow")
    run_command("pip install 'datasets==2.14.0' --quiet", "安装datasets 2.14.0")

    # 验证修复
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
        fix_modelscope_dependencies()
    else:
        main()
