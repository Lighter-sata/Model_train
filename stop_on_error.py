#!/usr/bin/env python3
"""
训练监控和错误停止脚本
在训练或推理发生错误时自动停止并提供详细错误信息
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path

def monitor_training(command, log_file="logs/train.log"):
    """监控训练过程，遇到错误立即停止"""
    print("🔍 开始监控训练过程...")
    print(f"📝 日志文件: {log_file}")
    print("="*60)

    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)

    try:
        # 启动训练进程
        print(f"🚀 启动命令: {' '.join(command)}")

        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 实时监控输出
            error_detected = False
            error_lines = []

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break

                if output:
                    # 实时显示输出
                    print(output.strip())

                    # 写入日志
                    log.write(output)
                    log.flush()

                    # 检查是否包含错误关键词
                    error_keywords = [
                        'Error', 'Exception', 'Traceback', 'FAILED', '❌',
                        'ImportError', 'ModuleNotFoundError', 'AttributeError',
                        'SyntaxError', 'RuntimeError', 'OSError'
                    ]

                    if any(keyword.lower() in output.lower() for keyword in error_keywords):
                        error_detected = True
                        error_lines.append(output.strip())

                        # 如果检测到错误，继续收集信息但标记为错误
                        if len(error_lines) >= 5:  # 收集足够多的错误信息
                            break

            # 等待进程结束
            return_code = process.wait()

            if return_code != 0 or error_detected:
                show_training_error(command, return_code, error_lines, log_file)
                return False
            else:
                print("\n✅ 训练完成！")
                return True

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断训练")
        if 'process' in locals():
            process.terminate()
        return False
    except Exception as e:
        print(f"\n❌ 监控过程中发生异常: {e}")
        return False

def show_training_error(command, return_code, error_lines, log_file):
    """显示训练错误详情"""
    print("\n" + "!"*60)
    print("🚨 训练过程检测到错误！")
    print("!"*60)

    print(f"命令: {' '.join(command)}")
    print(f"退出码: {return_code}")

    if error_lines:
        print(f"\n检测到的错误信息:")
        for i, line in enumerate(error_lines[-10:], 1):  # 显示最后10行错误
            print(f"  {i}. {line}")

    print(f"\n📝 完整日志: {log_file}")
    print("查看命令: tail -f " + log_file)

    print("\n🔧 常见解决方法:")
    print("1. 检查依赖安装: python test_setup.py")
    print("2. 修复PyArrow问题: python fix_pyarrow_manual.py")
    print("3. 修复datasets兼容性: python fix_datasets_compatibility.py")
    print("4. 检查GPU内存: nvidia-smi")
    print("5. 查看系统资源: htop 或 top")

    print("\n💡 快速修复命令:")
    print("# 检查Python环境")
    print("python -c \"import torch; print('PyTorch:', torch.__version__)\"")
    print("# 检查CUDA")
    print("python -c \"import torch; print('CUDA available:', torch.cuda.is_available())\"")
    print("# 重新运行（修复后）")
    print(f"python {' '.join(command)}")

    print("!"*60)

def run_with_monitoring(step="all"):
    """使用监控运行训练"""
    python_cmd = [sys.executable, "main.py", "--step", step]

    # 根据步骤设置日志文件
    log_files = {
        "analysis": "logs/data.log",
        "train": "logs/train.log",
        "inference": "logs/inference.log",
        "evaluate": "logs/evaluate.log",
        "all": "logs/full_training.log"
    }

    log_file = log_files.get(step, "logs/training.log")

    print(f"🐰 金融文本相似度分类竞赛 - 监控模式")
    print("="*60)
    print(f"🎯 执行步骤: {step}")
    print(f"📝 日志文件: {log_file}")
    print("💡 遇到错误将自动停止并显示详细信息")
    print("="*60)

    success = monitor_training(python_cmd, log_file)

    if not success:
        print("\n❌ 训练失败，请根据上方错误信息进行修复")
        sys.exit(1)
    else:
        print("\n🎉 训练成功完成！")
        sys.exit(0)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python stop_on_error.py <step>")
        print("步骤: analysis, train, inference, evaluate, all")
        sys.exit(1)

    step = sys.argv[1]
    valid_steps = ['analysis', 'train', 'inference', 'evaluate', 'all']

    if step not in valid_steps:
        print(f"无效步骤: {step}")
        print(f"有效步骤: {', '.join(valid_steps)}")
        sys.exit(1)

    run_with_monitoring(step)

if __name__ == '__main__':
    main()
