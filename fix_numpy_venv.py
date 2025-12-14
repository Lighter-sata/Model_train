#!/usr/bin/env python3
"""
使用venv创建NumPy兼容性虚拟环境
"""

import subprocess
import sys
import os
import venv
import shutil

def run_command(cmd, desc="", cwd=None):
    """运行命令"""
    print(f"🔧 {desc}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        print("✅ 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {e.stderr[:200]}...")
        return False

def create_numpy_venv():
    """创建NumPy兼容性虚拟环境"""
    venv_path = "numpy_venv"

    print(f"🔄 创建NumPy兼容性虚拟环境: {venv_path}")

    # 删除已存在的环境
    if os.path.exists(venv_path):
        print(f"  删除旧环境: {venv_path}")
        shutil.rmtree(venv_path)

    # 创建新的虚拟环境
    try:
        venv.create(venv_path, with_pip=True)
        print("✅ 虚拟环境创建成功")
        return venv_path
    except Exception as e:
        print(f"❌ 虚拟环境创建失败: {e}")
        return None

def install_packages_in_venv(venv_path):
    """在虚拟环境中安装包"""
    pip_path = os.path.join(venv_path, "bin", "pip")

    if not os.path.exists(pip_path):
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")  # Windows

    if not os.path.exists(pip_path):
        print("❌ 找不到pip可执行文件")
        return False

    print("📦 在虚拟环境中安装包...")

    # 升级pip
    run_command(f"{pip_path} install --upgrade pip --quiet", "升级pip")

    # 安装NumPy 1.x
    success = run_command(f"{pip_path} install 'numpy==1.24.3' --force-reinstall --quiet", "安装NumPy 1.24.3")

    if not success:
        print("  尝试其他NumPy版本...")
        for version in ["1.24.4", "1.24.2"]:
            if run_command(f"{pip_path} install 'numpy=={version}' --force-reinstall --quiet", f"安装NumPy {version}"):
                success = True
                break

    if not success:
        print("❌ NumPy安装失败")
        return False

    # 安装其他兼容包
    packages = [
        "pandas==1.5.3",
        "pyarrow==11.0.0",
        "datasets==2.14.0",
        "torch",
        "transformers",
        "accelerate",
        "ms-swift",
        "matplotlib",
        "seaborn",
        "jieba",
        "tqdm",
        "wordcloud",
        "requests"
    ]

    for package in packages:
        run_command(f"{pip_path} install '{package}' --quiet", f"安装{package}")

    return True

def create_activation_script(venv_path):
    """创建环境激活脚本"""
    script_content = f"""#!/bin/bash
# NumPy兼容性虚拟环境激活脚本

echo "🐍 激活NumPy兼容性虚拟环境"
source {venv_path}/bin/activate

echo "✅ 环境已激活，NumPy版本: $(python -c 'import numpy as np; print(np.__version__)')"
echo "现在可以运行: python main.py --step all"
echo "或运行: python stop_on_error.py all"

# 保持shell激活状态
exec bash
"""

    script_path = "activate_numpy_venv.sh"
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)
        print(f"✅ 激活脚本已创建: {script_path}")
        return True
    except Exception as e:
        print(f"❌ 创建激活脚本失败: {e}")
        return False

def create_wrapper_script(venv_path):
    """创建包装脚本"""
    script_content = f"""#!/bin/bash
# NumPy兼容性包装脚本
# 自动激活虚拟环境并运行Python脚本

# 激活虚拟环境
source {venv_path}/bin/activate

# 运行原始命令
exec "$@"
"""

    script_path = "run_with_numpy_venv.sh"
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)
        print(f"✅ 包装脚本已创建: {script_path}")
        return True
    except Exception as e:
        print(f"❌ 创建包装脚本失败: {e}")
        return False

def test_venv(venv_path):
    """测试虚拟环境"""
    python_path = os.path.join(venv_path, "bin", "python")

    if not os.path.exists(python_path):
        python_path = os.path.join(venv_path, "Scripts", "python.exe")  # Windows

    test_cmd = f"{python_path} -c \"import numpy as np; import pandas as pd; import pyarrow as pa; import datasets; print('NumPy:', np.__version__); print('Pandas:', pd.__version__); print('PyArrow:', pa.__version__); print('Datasets:', datasets.__version__)\""

    print("🔍 测试虚拟环境...")
    try:
        result = subprocess.run(test_cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ 虚拟环境测试成功:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 虚拟环境测试失败:")
        print(e.stderr)
        return False

def main():
    """主函数"""
    print("🐍 NumPy兼容性 - 虚拟环境解决方案")
    print("=" * 50)

    # 创建虚拟环境
    venv_path = create_numpy_venv()
    if not venv_path:
        return False

    # 安装包
    if not install_packages_in_venv(venv_path):
        print("❌ 包安装失败")
        return False

    # 测试环境
    if test_venv(venv_path):
        # 创建脚本
        create_activation_script(venv_path)
        create_wrapper_script(venv_path)

        print("\n🎉 NumPy兼容性虚拟环境创建完成！")
        print("\n使用方法:")
        print("1. 激活环境并进入shell: ./activate_numpy_venv.sh")
        print("2. 或使用包装脚本: ./run_with_numpy_venv.sh python main.py --step all")
        print("3. 或直接运行: source numpy_venv/bin/activate && python main.py --step all")

        return True

    print("❌ 虚拟环境创建失败")
    return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
