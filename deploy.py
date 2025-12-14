#!/usr/bin/env python3
"""
金融文本相似度分类竞赛 - 快速部署指南
"""

import os
import sys

def show_deployment_guide():
    """显示部署指南"""
    print("=" * 60)
    print("🐰 金融文本相似度分类竞赛 - 部署指南")
    print("=" * 60)
    print()
    print("📋 快速开始:")
    print("1. 安装依赖:")
    print("   pip install -r requirements.txt")
    print()
    print("2. 运行完整流程:")
    print("   python main.py --step all")
    print()
    print("3. 或分步执行:")
    print("   python main.py --step analysis    # 数据分析")
    print("   python main.py --step train       # 模型训练")
    print("   python main.py --step inference   # 模型推理")
    print("   python main.py --step evaluate    # 性能评估")
    print()
    print("📁 项目结构:")
    print("├── main.py              # 主脚本")
    print("├── scripts/             # 核心算法")
    print("├── config/              # 配置文件")
    print("├── data/                # 数据文件")
    print("├── models/              # 模型输出")
    print("├── results/             # 结果输出")
    print("└── logs/                # 日志文件")
    print()
    print("🎯 目标: 将准确率从0.764提升至0.85+")
    print("=" * 60)

def check_environment():
    """检查基本环境"""
    print("\n🔍 环境检查:")

    # Python版本
    version = sys.version_info
    print(f"  Python: {version.major}.{version.minor}.{version.micro}")

    # 检查关键包
    packages = ['torch', 'transformers', 'datasets']
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (需要安装)")

    print("\n💡 如遇依赖问题，请运行: pip install -r requirements.txt")

if __name__ == '__main__':
    show_deployment_guide()
    check_environment()