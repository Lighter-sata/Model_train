#!/usr/bin/env python3
"""
手动修复PyArrow兼容性问题的脚本
直接在当前Python进程中应用补丁并重新安装依赖
"""

import subprocess
import sys
import os

def apply_patch():
    """应用pyarrow补丁"""
    try:
        import pyarrow as pa
        import pyarrow.lib as palib

        patched = False

        # 在pyarrow顶级模块上应用补丁
        if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
            pa.PyExtensionType = pa.ExtensionType
            print("✅ 已应用pyarrow顶级模块补丁")
            patched = True

        # 在pyarrow.lib模块上应用补丁
        if not hasattr(palib, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
            palib.PyExtensionType = pa.ExtensionType
            print("✅ 已应用pyarrow.lib模块补丁")
            patched = True

        # 额外确保ExtensionType在lib中也可用
        if hasattr(pa, 'ExtensionType') and not hasattr(palib, 'ExtensionType'):
            palib.ExtensionType = pa.ExtensionType
            print("✅ 已复制ExtensionType到pyarrow.lib")
            patched = True

        if patched:
            return True
        else:
            print("✅ pyarrow已兼容，无需补丁")
            return True

    except ImportError as e:
        print(f"❌ 无法导入pyarrow: {e}")
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

def main():
    """主函数"""
    print("🔧 手动修复PyArrow兼容性问题")
    print("=" * 50)

    # 第一步：应用补丁
    print("\n1. 应用兼容性补丁...")
    if not apply_patch():
        print("❌ 补丁应用失败")
        return False

    # 第二步：卸载冲突包
    print("\n2. 清理冲突包...")
    run_command("pip uninstall -y datasets pyarrow", "卸载datasets和pyarrow")

    # 第三步：安装兼容版本
    print("\n3. 安装兼容版本...")
    success = True
    success &= run_command("pip install 'pyarrow>=8.0.0,<12.0.0'", "安装兼容的pyarrow")
    success &= run_command("pip install 'datasets==2.14.0'", "安装datasets 2.14.0")

    # 第四步：验证安装
    print("\n4. 验证安装...")
    try:
        import datasets
        print(f"✅ datasets {datasets.__version__} 导入成功")

        from datasets import load_dataset
        print("✅ datasets功能正常")

        return True

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 修复完成！现在可以运行训练脚本了。")
        print("运行: python main.py --step all")
    else:
        print("\n❌ 修复失败，请尝试其他方法。")

    sys.exit(0 if success else 1)
