#!/usr/bin/env python3
"""
金融文本相似度分类竞赛 - 一键部署脚本
自动检测环境，安装依赖，执行完整训练流程
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path

def print_banner():
    """打印欢迎信息"""
    print("=" * 70)
    print("🐰 金融文本相似度分类竞赛 - 一键部署工具")
    print("=" * 70)
    print("📊 目标: 将基线准确率 0.764 提升至 0.85+")
    print("🎯 预期: 90分钟内完成训练，前30名")
    print("=" * 70)

def detect_platform():
    """检测运行平台"""
    if os.path.exists('/mnt/workspace'):
        return 'modelscope'
    elif platform.system() == 'Linux':
        return 'linux'
    elif platform.system() == 'Darwin':
        return 'macos'
    elif platform.system() == 'Windows':
        return 'windows'
    else:
        return 'unknown'

def check_system_requirements():
    """检查系统要求"""
    print("\n🔍 检查系统要求...")

    # 检查Python版本
    python_version = sys.version_info
    version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    print(f"  Python版本: {version_str}")

    if python_version < (3, 8):
        print("❌ 需要 Python 3.8+")
        return False
    elif python_version < (3, 10):
        print("⚠️  推荐使用 Python 3.10+ 以获得最佳性能")
    else:
        print("✅ Python版本符合要求")

    # 检查内存（简单检查）
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        print(f"  系统内存: {memory_gb:.1f} GB")
        if memory_gb < 16:
            print("⚠️  系统内存较小，可能影响训练性能")
        else:
            print("✅ 系统内存充足")
    except ImportError:
        print("  内存检查: 跳过（未安装psutil）")

    return True

def check_gpu():
    """检查GPU可用性"""
    print("\n🎮 检查GPU...")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
            print(f"✅ GPU可用: {gpu_count}个设备")
            print(f"  设备名称: {gpu_name}")

            # 检查GPU内存
            if gpu_count > 0:
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                print(f"  GPU内存: {gpu_memory:.1f} GB")
                if gpu_memory < 8:
                    print("⚠️  GPU内存较小，建议使用较小的batch_size")
        else:
            print("❌ 未检测到GPU，将使用CPU训练（非常慢）")
            return False
    except ImportError:
        print("❌ 无法检查GPU（torch未安装）")
        return False

    return True

def install_dependencies():
    """安装依赖"""
    print("\n📦 安装依赖...")

    platform_name = detect_platform()

    try:
        if platform_name == 'modelscope':
            print("  检测到魔搭平台，使用专用安装脚本...")
            result = subprocess.run([sys.executable, 'fix_modelscope_deps.py'],
                                  capture_output=True, text=True, check=True)
        else:
            print("  使用标准安装脚本...")
            result = subprocess.run([sys.executable, 'install_deps.py'],
                                  capture_output=True, text=True, check=True)

        print("✅ 依赖安装完成")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e.stderr}")

        # 备用方案：尝试快速修复
        print("\n🔧 尝试备用修复方案...")
        try:
            print("  运行快速兼容性补丁...")
            result = subprocess.run([sys.executable, 'quick_pyarrow_fix.py'],
                                  capture_output=True, text=True, check=True)
            print("✅ 兼容性补丁应用成功")

            # 重新尝试安装依赖
            if platform_name == 'modelscope':
                result = subprocess.run([sys.executable, 'fix_modelscope_deps.py'],
                                      capture_output=True, text=True, check=True)
            else:
                result = subprocess.run([sys.executable, 'install_deps.py'],
                                      capture_output=True, text=True, check=True)

            print("✅ 依赖安装完成（使用备用方案）")
            return True

        except subprocess.CalledProcessError as e2:
            print(f"❌ 备用方案也失败: {e2.stderr}")
            return False

def run_setup_verification():
    """运行环境验证"""
    print("\n🔍 验证安装...")
    try:
        result = subprocess.run([sys.executable, 'test_setup.py'],
                              capture_output=True, text=True, check=True)
        print("✅ 环境验证通过")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 环境验证失败: {e.stderr}")
        return False

def run_full_pipeline():
    """运行完整训练流程"""
    print("\n🚀 开始完整训练流程...")
    print("预计耗时: 90分钟")
    print("-" * 50)

    try:
        # 执行完整流程
        result = subprocess.run([sys.executable, 'main.py', '--step', 'all'],
                              check=True)
        print("\n🎉 训练流程完成！")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 训练流程失败: {e}")
        return False

def show_results():
    """显示结果"""
    print("\n📊 训练结果:")

    # 检查模型文件
    model_dir = Path("models")
    if model_dir.exists() and any(model_dir.rglob("*")):
        print("✅ 模型文件已生成")
        model_files = list(model_dir.rglob("*"))
        print(f"  找到 {len(model_files)} 个模型文件")
    else:
        print("❌ 未找到模型文件")

    # 检查结果文件
    result_file = Path("results/enhanced_result.jsonl")
    if result_file.exists():
        print("✅ 预测结果已生成")
        print(f"  结果文件: {result_file}")
    else:
        print("❌ 未找到预测结果文件")

    # 检查评估报告
    eval_dir = Path("results/evaluation_results")
    if eval_dir.exists():
        print("✅ 评估报告已生成")
        eval_files = list(eval_dir.glob("*"))
        if eval_files:
            print(f"  评估文件: {len(eval_files)} 个")
    else:
        print("❌ 未找到评估报告")

def show_next_steps():
    """显示后续步骤"""
    print("\n🎯 下一步操作:")
    print("1. 检查训练结果: 查看 results/evaluation_results/ 目录")
    print("2. 准备竞赛提交:")
    print("   cp results/enhanced_result.jsonl results/result.json")
    print("3. 提交 result.json 到竞赛页面")
    print("\n📈 性能目标:")
    print("- 准确率: 0.85+ (目标前30名)")
    print("- 训练时间: ~90分钟")
    print("- GPU内存: 8GB+ 推荐")

def main():
    """主函数"""
    print_banner()

    # 步骤计数器
    step = 1
    total_steps = 6

    # 1. 系统要求检查
    print(f"\n[{step}/{total_steps}] 系统要求检查")
    if not check_system_requirements():
        print("❌ 系统不符合要求，请升级系统配置")
        return
    step += 1

    # 2. GPU检查
    print(f"\n[{step}/{total_steps}] GPU可用性检查")
    gpu_available = check_gpu()
    if not gpu_available:
        print("⚠️  未检测到GPU，训练将非常慢")
        response = input("是否继续？(y/N): ")
        if response.lower() != 'y':
            return
    step += 1

    # 3. 依赖安装
    print(f"\n[{step}/{total_steps}] 依赖安装")
    if not install_dependencies():
        print("❌ 依赖安装失败，请手动解决依赖问题")
        return
    step += 1

    # 4. 环境验证
    print(f"\n[{step}/{total_steps}] 环境验证")
    if not run_setup_verification():
        print("❌ 环境验证失败，请检查依赖安装")
        return
    step += 1

    # 5. 执行训练
    print(f"\n[{step}/{total_steps}] 执行训练流程")
    if not run_full_pipeline():
        print("❌ 训练流程失败，请检查日志文件")
        return
    step += 1

    # 6. 显示结果
    print(f"\n[{step}/{total_steps}] 显示结果")
    show_results()
    show_next_steps()

    print("\n" + "="*70)
    print("🎉 一键部署完成！祝竞赛顺利！")
    print("="*70)

if __name__ == '__main__':
    main()
