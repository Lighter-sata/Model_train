#!/usr/bin/env python3
"""
金融文本相似度分类竞赛 - 主部署脚本
一键执行完整训练和推理流程
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_command(cmd, desc=""):
    """运行命令并显示状态"""
    print(f"🔧 {desc}")
    try:
        # 检测运行环境
        if os.path.exists('/mnt/workspace'):
            # 魔搭平台环境 - 使用当前目录作为工作目录
            env = os.environ.copy()
            current_dir = os.getcwd()
            env['PYTHONPATH'] = current_dir
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, env=env, cwd=current_dir)
        else:
            # 本地环境
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {e.stderr}")
        return False

def check_environment():
    """检查运行环境"""
    print("🔍 检查环境...")

    # 检测运行环境
    in_modelscope = os.path.exists('/mnt/workspace')
    print(f"  运行环境: {'魔搭平台' if in_modelscope else '本地环境'}")

    # 检查Python版本
    python_version = sys.version_info
    print(f"  Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    # 检查必要的依赖
    required_modules = ['torch']
    recommended_modules = ['transformers', 'datasets']
    missing_required = []
    missing_recommended = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} (必需)")
            missing_required.append(module)

    for module in recommended_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            error_msg = str(e)[:50]
            if "PyExtensionType" in error_msg:
                error_msg = "版本兼容性问题，请运行: python fix_modelscope_deps.py"
            print(f"  ⚠️  {module} (推荐) - {error_msg}")
            missing_recommended.append(module)

    if missing_required:
        print(f"\n❌ 缺少必需依赖包: {', '.join(missing_required)}")
        if in_modelscope:
            print("请在魔搭平台运行: python fix_modelscope_deps.py")
        else:
            print("请运行: pip install -r requirements.txt")
        return False

    if missing_recommended:
        print(f"\n⚠️  缺少推荐依赖包: {', '.join(missing_recommended)}")
        print("某些功能可能无法正常工作")
        if in_modelscope:
            print("建议运行: python fix_modelscope_deps.py")

    # 检查GPU
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        gpu_count = torch.cuda.device_count() if gpu_available else 0
        print(f"  GPU: {'✅ 可用' if gpu_available else '❌ 不可用'} ({gpu_count}个)")
    except:
        print("  GPU: 检查失败")

    return True

def run_data_analysis():
    """运行数据分析"""
    print("\n" + "="*60)
    print("📊 第一步: 数据集处理")
    print("="*60)

    script_path = "scripts/data_processor.py"
    if os.path.exists(script_path):
        # 先下载数据
        success = run_command(f"python {script_path} download", "下载数据集")
        if success:
            # 再分析数据
            return run_command(f"python {script_path} analyze", "分析数据集")
        return False
    else:
        print("❌ 找不到数据处理脚本")
        return False

def run_training():
    """运行模型训练"""
    print("\n" + "="*60)
    print("🚀 第二步: 模型训练")
    print("="*60)

    script_path = "scripts/model_trainer.py"
    if os.path.exists(script_path):
        return run_command(f"python {script_path} train", "训练模型")
    else:
        print("❌ 找不到模型训练脚本")
        return False

def run_inference():
    """运行模型推理"""
    print("\n" + "="*60)
    print("🧠 第三步: 模型推理")
    print("="*60)

    script_path = "scripts/model_trainer.py"
    if os.path.exists(script_path):
        return run_command(f"python {script_path} inference", "运行推理")
    else:
        print("❌ 找不到模型推理脚本")
        return False

def run_evaluation():
    """运行性能评估"""
    print("\n" + "="*60)
    print("📊 第四步: 性能评估")
    print("="*60)

    script_path = "scripts/evaluate.py"
    if os.path.exists(script_path):
        return run_command(f"python {script_path}", "评估性能")
    else:
        print("❌ 找不到评估脚本")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="金融文本相似度分类竞赛 - 部署工具")
    parser.add_argument('--step', choices=['all', 'analysis', 'train', 'inference', 'evaluate'],
                       default='all', help='执行特定步骤 (默认: all)')
    parser.add_argument('--skip-env-check', action='store_true',
                       help='跳过环境检查')

    args = parser.parse_args()

    print("🐰 金融文本相似度分类竞赛 - 部署工具")
    print("=" * 60)

    # 检查环境
    if not args.skip_env_check:
        if not check_environment():
            print("\n❌ 环境检查失败，请修复依赖问题后重试")
            return

    # 执行相应步骤 - 遇到错误立即停止
    print(f"\n🚀 开始执行步骤: {args.step}")
    print("-" * 60)

    try:
        if args.step in ['all', 'analysis']:
            print("\n📊 执行: 数据分析")
            if not run_data_analysis():
                print("\n❌ 数据分析失败！停止执行。")
                print("请检查上面的错误信息并修复问题。")
                return

        if args.step in ['all', 'train']:
            print("\n🚀 执行: 模型训练")
            if not run_training():
                print("\n❌ 模型训练失败！停止执行。")
                print("请检查上面的错误信息并修复问题。")
                return

        if args.step in ['all', 'inference']:
            print("\n🧠 执行: 模型推理")
            if not run_inference():
                print("\n❌ 模型推理失败！停止执行。")
                print("请检查上面的错误信息并修复问题。")
                return

        if args.step in ['all', 'evaluate']:
            print("\n📊 执行: 性能评估")
            if not run_evaluation():
                print("\n❌ 性能评估失败！停止执行。")
                print("请检查上面的错误信息并修复问题。")
                return

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        return
    except Exception as e:
        print(f"\n❌ 执行过程中发生未预期的错误: {e}")
        print("请检查错误详情并修复问题。")
        return

    # 总结
    print("\n" + "="*60)
    if success:
        print("🎉 所有步骤执行完成！")
        print("\n📁 输出文件:")
        print("  • 模型: models/ 目录")
        print("  • 结果: results/ 目录")
        print("  • 日志: logs/ 目录")

        print("\n🏆 竞赛提交:")
        print("  1. 复制结果文件: cp results/enhanced_result.jsonl results/result.json")
        print("  2. 提交 result.json 到竞赛页面")
    else:
        print("❌ 执行过程中出现错误，请检查日志")
    print("="*60)

if __name__ == '__main__':
    main()
