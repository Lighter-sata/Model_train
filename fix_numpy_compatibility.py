#!/usr/bin/env python3
"""
修复NumPy版本兼容性问题
处理NumPy 2.x与包的兼容性问题
"""

import subprocess
import sys
import os

def check_numpy_version():
    """检查NumPy版本"""
    try:
        import numpy as np
        version = np.__version__
        major_version = int(version.split('.')[0])
        print(f"当前NumPy版本: {version}")
        print(f"主版本号: {major_version}")

        if major_version >= 2:
            print("⚠️  检测到NumPy 2.x版本，可能导致兼容性问题")
            return True, version
        else:
            print("✅ NumPy版本兼容")
            return False, version
    except ImportError:
        print("❌ NumPy未安装")
        return False, None

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

def fix_numpy_compatibility():
    """修复NumPy兼容性问题"""
    print("🔧 修复NumPy兼容性问题")
    print("=" * 50)

    # 检查当前NumPy版本
    is_numpy2, version = check_numpy_version()

    if not is_numpy2:
        print("✅ NumPy版本无需修复")
        return True

    print("\n📦 NumPy 2.x检测到，开始修复...")

    # 方案1: 降级NumPy到1.x版本
    print("\n🔄 方案1: 降级NumPy到1.x版本...")
    success = run_command("pip install 'numpy<2.0.0' --force-reinstall --quiet", "降级NumPy到1.x")

    if success:
        # 验证修复
        print("\n🔍 验证修复...")
        try:
            import numpy as np
            new_version = np.__version__
            print(f"修复后NumPy版本: {new_version}")

            # 测试相关包
            try:
                import pandas as pd
                print(f"✅ pandas导入成功: {pd.__version__}")
            except ImportError as e:
                print(f"⚠️  pandas导入失败: {e}")

            try:
                import pyarrow as pa
                print(f"✅ pyarrow导入成功: {pa.__version__}")
            except ImportError as e:
                print(f"⚠️  pyarrow导入失败: {e}")

            try:
                import datasets
                print(f"✅ datasets导入成功: {datasets.__version__}")
            except ImportError as e:
                print(f"⚠️  datasets导入失败: {e}")

            print("✅ NumPy兼容性修复完成！")
            return True

        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False
    else:
        print("❌ NumPy降级失败")

    # 方案2: 尝试升级相关包到支持NumPy 2.x的版本
    print("\n🔄 方案2: 升级包到支持NumPy 2.x的版本...")
    packages_to_upgrade = [
        "pandas>=2.0.0",
        "pyarrow>=12.0.0",
        "scipy>=1.11.0",
        "scikit-learn>=1.3.0"
    ]

    for package in packages_to_upgrade:
        run_command(f"pip install '{package}' --quiet", f"升级{package}")

    # 再次验证
    print("\n🔍 再次验证...")
    try:
        import pandas as pd
        import pyarrow as pa
        import datasets
        print("✅ 包升级方案成功")
        return True
    except ImportError as e:
        print(f"❌ 包升级方案也失败: {e}")

    # 方案3: 最后尝试强制降级所有相关包
    print("\n🔄 方案3: 强制降级所有相关包...")
    force_downgrade = [
        "numpy==1.24.3",
        "pandas==1.5.3",
        "pyarrow==11.0.0",
        "datasets==2.14.0"
    ]

    for package in force_downgrade:
        run_command(f"pip install '{package}' --force-reinstall --quiet", f"强制安装{package}")

    # 最终验证
    print("\n🔍 最终验证...")
    try:
        import numpy as np
        import pandas as pd
        import pyarrow as pa
        import datasets

        print("✅ 强制降级方案成功！")
        print(f"  NumPy: {np.__version__}")
        print(f"  Pandas: {pd.__version__}")
        print(f"  PyArrow: {pa.__version__}")
        print(f"  Datasets: {datasets.__version__}")
        return True

    except ImportError as e:
        print(f"❌ 所有修复方案都失败: {e}")
        print("\n💡 手动解决建议:")
        print("1. 完全重置环境: pip uninstall numpy pandas pyarrow datasets")
        print("2. 重新安装: pip install 'numpy<2' pandas pyarrow datasets")
        print("3. 或联系平台管理员升级包版本")
        return False

def main():
    """主函数"""
    print("🐰 NumPy兼容性修复工具")
    print("=" * 50)

    success = fix_numpy_compatibility()

    if success:
        print("\n🎉 NumPy兼容性问题已修复！")
        print("现在可以正常运行训练脚本了。")
    else:
        print("\n❌ NumPy兼容性修复失败")
        print("请尝试手动解决或联系技术支持。")

    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
