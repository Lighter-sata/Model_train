#!/usr/bin/env python3
"""
使用conda解决NumPy兼容性问题
为关键包创建隔离环境
"""

import subprocess
import sys
import os

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

def check_conda():
    """检查conda是否可用"""
    try:
        result = subprocess.run(["conda", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ conda可用: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("❌ conda不可用")
    return False

def create_numpy_env():
    """创建NumPy兼容环境"""
    env_name = "numpy_compat"

    print(f"🔄 创建conda环境: {env_name}")

    # 删除已存在的环境
    run_command(f"conda env remove -n {env_name} -y --quiet", "删除旧环境（如果存在）")

    # 创建新环境
    success = run_command(f"conda create -n {env_name} python=3.10 numpy=1.24 pandas pyarrow datasets -y --quiet", "创建NumPy 1.x环境")

    if success:
        print(f"✅ 环境 {env_name} 创建成功")
        return env_name

    return None

def install_packages_in_env(env_name):
    """在环境中安装额外的包"""
    packages = [
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

    print(f"📦 在环境 {env_name} 中安装额外包...")

    for package in packages:
        run_command(f"conda install -n {env_name} {package} -y --quiet", f"安装 {package}")

    # 安装modelscope（可能需要特殊处理）
    run_command(f"conda install -n {env_name} -c conda-forge modelscope -y --quiet", "安装 modelscope")

    return True

def create_wrapper_script(env_name):
    """创建包装脚本"""
    wrapper_script = f"""#!/bin/bash
# NumPy兼容性包装脚本
# 自动激活conda环境并运行Python脚本

# 激活conda环境
conda activate {env_name}

# 运行原始命令
exec "$@"
"""

    wrapper_path = "run_with_numpy_compat.sh"
    try:
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_script)

        # 给脚本执行权限
        os.chmod(wrapper_path, 0o755)
        print(f"✅ 包装脚本已创建: {wrapper_path}")
        return True

    except Exception as e:
        print(f"❌ 创建包装脚本失败: {e}")
        return False

def test_env(env_name):
    """测试环境"""
    print(f"🔍 测试环境 {env_name}...")

    test_cmd = f"conda run -n {env_name} python -c \"import numpy as np; import pandas as pd; import pyarrow as pa; print('NumPy:', np.__version__); print('Pandas:', pd.__version__); print('PyArrow:', pa.__version__)\""

    try:
        result = subprocess.run(test_cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ 环境测试成功:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 环境测试失败:")
        print(e.stderr)
        return False

def main():
    """主函数"""
    print("🐍 NumPy兼容性 - Conda环境解决方案")
    print("=" * 50)

    # 检查conda
    if not check_conda():
        print("❌ 需要conda来使用此解决方案")
        print("请安装Miniconda或Anaconda:")
        print("  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh")
        print("  bash Miniconda3-latest-Linux-x86_64.sh")
        return False

    # 创建环境
    env_name = create_numpy_env()
    if not env_name:
        print("❌ 环境创建失败")
        return False

    # 安装额外包
    install_packages_in_env(env_name)

    # 测试环境
    if test_env(env_name):
        # 创建包装脚本
        if create_wrapper_script(env_name):
            print("\n🎉 NumPy兼容性环境创建完成！")
            print("\n使用方法:")
            print(f"1. 激活环境: conda activate {env_name}")
            print("2. 或使用包装脚本: ./run_with_numpy_compat.sh python main.py --step all")
            print("3. 运行训练: python main.py --step all")
            return True

    print("❌ 环境创建失败，请检查conda安装")
    return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
