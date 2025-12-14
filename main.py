#!/usr/bin/env python3
"""
金融文本相似度分类竞赛 - 主部署脚本
一键执行完整训练和推理流程
"""

# ===========================================
# 紧急修复：datasets和pyarrow兼容性问题
# 在任何其他导入之前执行
# ===========================================

print("🔧 [main] 开始紧急修复datasets兼容性...")

try:
    # 1. 修复pyarrow问题
    import pyarrow as pa
    print(f"🔧 [main] pyarrow版本: {pa.__version__}")

    if not hasattr(pa, 'PyExtensionType') and hasattr(pa, 'ExtensionType'):
        pa.PyExtensionType = pa.ExtensionType
        print("🔧 [main] 已修复pyarrow.PyExtensionType")

    if hasattr(pa, 'lib') and not hasattr(pa.lib, 'PyExtensionType') and hasattr(pa.lib, 'ExtensionType'):
        pa.lib.PyExtensionType = pa.lib.ExtensionType
        print("🔧 [main] 已修复pyarrow.lib.PyExtensionType")

except Exception as e:
    print(f"🔧 [main] pyarrow修复失败: {e}")

try:
    # 2. 修复datasets LargeList问题
    import datasets
    print(f"🔧 [main] datasets版本: {datasets.__version__}")

    if not hasattr(datasets, 'LargeList'):
        print("🔧 [main] LargeList不存在，开始修复...")

        # 尝试从features导入
        try:
            from datasets.features import Sequence
            datasets.LargeList = Sequence
            print("🔧 [main] 已修复datasets LargeList (使用Sequence)")
        except ImportError as e:
            print(f"🔧 [main] 从features导入失败: {e}")
            # 创建完整的兼容类
            class LargeList:
                """Full LargeList compatibility class for datasets"""
                def __init__(self, dtype, length=None):
                    self.dtype = dtype
                    self.length = length

                def __repr__(self):
                    return f"LargeList(dtype={self.dtype}, length={self.length})"

            datasets.LargeList = LargeList
            print("🔧 [main] 已创建datasets LargeList兼容类")

    # 验证修复
    if hasattr(datasets, 'LargeList'):
        print("✅ [main] LargeList修复成功")
    else:
        print("❌ [main] LargeList修复失败")

except Exception as e:
    print(f"🔧 [main] datasets修复失败: {e}")

print("🔧 [main] 紧急修复完成，开始正常导入...\n")

# ===========================================
# 正常导入开始
# ===========================================

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 在导入可能依赖datasets的库之前，先修复datasets兼容性问题
def fix_datasets_import():
    """修复datasets导入问题"""
    try:
        import datasets
        if not hasattr(datasets, 'LargeList'):
            # 尝试从features导入
            try:
                from datasets.features import Sequence
                datasets.LargeList = Sequence
                print("🔧 已自动修复datasets LargeList导入问题")
            except ImportError:
                # 创建基础兼容类
                class LargeList:
                    pass
                datasets.LargeList = LargeList
                print("🔧 已创建datasets LargeList兼容类")
    except ImportError:
        pass

# 运行修复
fix_datasets_import()

def show_recovery_options(failed_step):
    """显示错误恢复选项"""
    print("\n" + "="*60)
    print(f"🔧 {failed_step} 失败 - 恢复选项")
    print("="*60)

    steps = {
        'analysis': ['数据下载问题', 'python scripts/data_processor.py download', 'python scripts/data_processor.py analyze'],
        'train': ['依赖或模型问题', 'python fix_datasets_compatibility.py', 'python main.py --step train'],
        'inference': ['模型文件问题', 'ls -la models/', 'python main.py --step inference'],
        'evaluate': ['结果文件问题', 'ls -la results/', 'python main.py --step evaluate']
    }

    if failed_step in steps:
        issue, check_cmd, retry_cmd = steps[failed_step]
        print(f"可能问题: {issue}")
        print(f"检查命令: {check_cmd}")
        print(f"重试命令: {retry_cmd}")

    print("\n通用解决方法:")
    print("1. 📦 检查依赖: python test_setup.py")
    print("2. 🔧 修复PyArrow: python fix_pyarrow_manual.py")
    print("3. 📊 修复datasets: python fix_datasets_compatibility.py")
    print("4. 📝 查看日志: tail -f logs/train.log")
    print("5. ⏭️  跳过此步骤: python main.py --step all --skip-step " + failed_step)
    print("="*60)

def show_command_error(cmd, error):
    """显示命令执行错误详情"""
    print("\n" + "="*60)
    print("🔍 错误详情")
    print("="*60)
    print(f"命令: {cmd}")
    print(f"退出码: {error.returncode}")

    if error.stdout and error.stdout.strip():
        print(f"\n📝 标准输出:")
        # 只显示最后几行，避免输出太长
        stdout_lines = error.stdout.strip().split('\n')
        if len(stdout_lines) > 20:
            print("... (输出过长，只显示最后20行)")
            stdout_lines = stdout_lines[-20:]
        for line in stdout_lines:
            print(f"  {line}")

    if error.stderr and error.stderr.strip():
        print(f"\n❌ 错误输出:")
        # 只显示最后几行错误信息
        stderr_lines = error.stderr.strip().split('\n')
        if len(stderr_lines) > 20:
            print("... (错误输出过长，只显示最后20行)")
            stderr_lines = stderr_lines[-20:]
        for line in stderr_lines:
            print(f"  {line}")

    print("="*60)
    print("💡 解决建议:")
    print("1. 检查依赖: python test_setup.py")
    print("2. 修复PyArrow: python fix_pyarrow_manual.py")
    print("3. 修复datasets: python fix_datasets_compatibility.py")
    print("4. 查看日志: tail -f logs/train.log")
    print("="*60)

def run_command(cmd, desc=""):
    """运行命令并显示状态"""
    print(f"🔧 {desc}")
    try:
        # 检测运行环境
        if os.path.exists('/mnt/workspace'):
            # 魔搭平台环境 - 使用当前目录作为工作目录，并确保site_packages在PYTHONPATH中
            env = os.environ.copy()
            current_dir = os.getcwd()
            site_packages_path = os.path.join(current_dir, 'site_packages')
            existing_pythonpath = env.get('PYTHONPATH', '')
            if existing_pythonpath:
                env['PYTHONPATH'] = f"{site_packages_path}:{current_dir}:{existing_pythonpath}"
            else:
                env['PYTHONPATH'] = f"{site_packages_path}:{current_dir}"
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, env=env, cwd=current_dir)
        else:
            # 本地环境
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败")
        show_command_error(cmd, e)
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
                show_recovery_options("analysis")
                return

        if args.step in ['all', 'train']:
            print("\n🚀 执行: 模型训练")
            if not run_training():
                print("\n❌ 模型训练失败！停止执行。")
                show_recovery_options("train")
                return

        if args.step in ['all', 'inference']:
            print("\n🧠 执行: 模型推理")
            if not run_inference():
                print("\n❌ 模型推理失败！停止执行。")
                show_recovery_options("inference")
                return

        if args.step in ['all', 'evaluate']:
            print("\n📊 执行: 性能评估")
            if not run_evaluation():
                print("\n❌ 性能评估失败！停止执行。")
                show_recovery_options("evaluate")
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
