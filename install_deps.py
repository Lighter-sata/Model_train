#!/usr/bin/env python3
"""
依赖安装脚本
自动安装项目所需的依赖包
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
        print(f"❌ 失败: {e.stderr}")
        return False

def install_dependencies():
    """安装依赖"""

    print("🐰 金融文本相似度分类竞赛 - 依赖安装")
    print("=" * 60)

    # 检查pip版本
    print("📦 检查pip版本...")
    run_command("pip --version", "")

    # 升级pip
    print("\n⬆️  升级pip...")
    run_command("pip install --upgrade pip", "")

    # 安装核心依赖
    print("\n📦 安装核心依赖...")
    core_packages = [
        "torch>=2.0.0",
        "transformers<4.58",
        "ms-swift<3.10",
        "modelscope>=1.30.0"
    ]

    for package in core_packages:
        run_command(f"pip install '{package}' --quiet", f"安装{package}")

    # 安装datasets（特定版本）
    print("\n📦 安装datasets...")
    run_command("pip install 'datasets==2.14.0' --quiet", "安装datasets 2.14.0")

    # 安装其他依赖
    print("\n📦 安装数据处理依赖...")
    other_packages = [
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "jieba",
        "tqdm",
        "wordcloud",
        "plotly",
        "requests"
    ]

    for package in other_packages:
        run_command(f"pip install {package} --quiet", f"安装{package}")

    # 验证安装
    print("\n🔍 验证安装...")
    try:
        import torch
        print(f"✅ torch: {torch.__version__}")

        import transformers
        print(f"✅ transformers: {transformers.__version__}")

        import datasets
        print(f"✅ datasets: {datasets.__version__}")

        print("\n🎉 依赖安装完成！")
        print("现在可以运行: python main.py --step all")

    except ImportError as e:
        print(f"❌ 验证失败: {e}")
        print("请手动运行: pip install -r requirements.txt")

def main():
    """主函数"""

    if len(sys.argv) > 1 and sys.argv[1] == "--yes":
        # 自动安装模式
        install_dependencies()
    else:
        # 交互模式
        print("此脚本将安装项目所需的依赖包。")
        response = input("是否继续？(y/N): ").strip().lower()
        if response in ['y', 'yes']:
            install_dependencies()
        else:
            print("安装已取消。")

if __name__ == '__main__':
    main()
