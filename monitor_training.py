#!/usr/bin/env python3
"""
训练过程监控脚本
提供多种监控训练状态的方法
"""

import os
import time
import subprocess
import argparse
from pathlib import Path

def monitor_logs(log_dir="./output_qwen2_7b_optimized/logs", follow=True):
    """监控训练日志"""
    print("📋 监控训练日志...")
    print(f"日志目录: {log_dir}")
    print("-" * 50)

    if not os.path.exists(log_dir):
        print(f"⚠️ 日志目录不存在: {log_dir}")
        print("💡 请先开始训练，日志会自动创建")
        return

    if follow:
        # 实时监控日志
        try:
            cmd = f"tail -f {log_dir}/*.log 2>/dev/null || echo '暂无日志文件'"
            print("🔄 实时监控模式 (Ctrl+C 退出)...")
            os.system(cmd)
        except KeyboardInterrupt:
            print("\n⏹️ 停止监控")
    else:
        # 显示最近的日志
        try:
            result = subprocess.run(f"find {log_dir} -name '*.log' -exec ls -la {{}} \\;",
                                  shell=True, capture_output=True, text=True)
            print("日志文件列表:")
            print(result.stdout)

            # 显示最新的日志内容
            result = subprocess.run(f"find {log_dir} -name '*.log' -exec tail -20 {{}} \\;",
                                  shell=True, capture_output=True, text=True)
            print("\n最新日志内容:")
            print(result.stdout)
        except Exception as e:
            print(f"读取日志失败: {e}")

def monitor_gpu():
    """监控GPU状态"""
    print("🎮 监控GPU状态...")
    print("-" * 50)

    try:
        # 检查nvidia-smi是否可用
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            print("NVIDIA GPU信息:")
            os.system("nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv")
        else:
            print("⚠️ nvidia-smi不可用")
    except FileNotFoundError:
        print("⚠️ nvidia-smi命令不存在")

    # 显示进程GPU使用情况
    try:
        print("\n🔍 GPU进程信息:")
        os.system("nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv")
    except:
        pass

def monitor_progress(output_dir="./output_qwen2_7b_optimized"):
    """监控训练进度"""
    print("📊 监控训练进度...")
    print(f"输出目录: {output_dir}")
    print("-" * 50)

    if not os.path.exists(output_dir):
        print(f"⚠️ 输出目录不存在: {output_dir}")
        return

    # 检查checkpoint
    checkpoints = list(Path(output_dir).glob("checkpoint-*"))
    if checkpoints:
        checkpoints.sort(key=lambda x: int(x.name.split('-')[1]))
        print(f"📁 检查点数量: {len(checkpoints)}")
        print(f"🗂️ 最新检查点: {checkpoints[-1].name}")

        # 显示最新检查点的训练状态
        trainer_state = checkpoints[-1] / "trainer_state.json"
        if trainer_state.exists():
            print(f"📄 训练状态文件: {trainer_state}")
    else:
        print("📁 暂无检查点")

    # 检查训练指标
    metrics_file = Path(output_dir) / "metrics.json"
    if metrics_file.exists():
        print("📈 训练指标文件存在")
        try:
            import json
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
            print(f"📊 最新指标: {list(metrics.keys())[-1] if metrics else '无'}")
        except:
            print("📊 无法读取指标文件")
    else:
        print("📊 暂无指标文件")

def monitor_resources(interval=5):
    """监控系统资源使用情况"""
    print(f"🖥️ 监控系统资源 (每{interval}秒更新)...")
    print("-" * 50)
    print("💡 按 Ctrl+C 停止监控")

    try:
        while True:
            print(f"\n🕐 {time.strftime('%H:%M:%S')}")

            # GPU信息
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                     "--format=csv,noheader,nounits"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for i, line in enumerate(lines):
                        mem_used, mem_total, gpu_util = line.split(', ')
                        print(f"🎮 GPU{i}: {mem_used}MB/{mem_total}MB ({gpu_util}%)")
            except:
                pass

            # CPU和内存
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                print(f"🖥️ CPU: {cpu_percent}%")
                print(f"💾 内存: {memory.percent}% ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)")
            except ImportError:
                print("⚠️ 安装 psutil 可获得更详细的系统监控: pip install psutil")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n⏹️ 停止资源监控")

def show_training_tips():
    """显示训练监控提示"""
    print("💡 训练监控提示:")
    print("=" * 50)
    print("1. 📋 日志监控:")
    print("   python monitor_training.py --logs")
    print("")
    print("2. 🎮 GPU监控:")
    print("   python monitor_training.py --gpu")
    print("")
    print("3. 📊 进度监控:")
    print("   python monitor_training.py --progress")
    print("")
    print("4. 🖥️ 资源监控:")
    print("   python monitor_training.py --resources")
    print("")
    print("5. 🔄 完整监控:")
    print("   python monitor_training.py --all")
    print("")
    print("🎯 训练正常指标:")
    print("   • GPU利用率: 80-100%")
    print("   • 内存使用: <22GB")
    print("   • Loss下降: 逐渐减少")
    print("   • 准确率提升: 稳步上升")
    print("")
    print("🚨 异常警告:")
    print("   • GPU利用率<50%: 可能配置不当")
    print("   • 内存不足: 可能需要调整batch_size")
    print("   • Loss不下降: 可能学习率过大")
    print("   • 准确率不升: 可能模型或数据问题")

def main():
    parser = argparse.ArgumentParser(description='训练过程监控工具')
    parser.add_argument('--logs', action='store_true', help='监控训练日志')
    parser.add_argument('--gpu', action='store_true', help='监控GPU状态')
    parser.add_argument('--progress', action='store_true', help='监控训练进度')
    parser.add_argument('--resources', action='store_true', help='监控系统资源')
    parser.add_argument('--all', action='store_true', help='完整监控')
    parser.add_argument('--tips', action='store_true', help='显示监控提示')

    args = parser.parse_args()

    if args.tips or len([arg for arg in vars(args).values() if arg]) == 0:
        show_training_tips()
        return

    if args.all:
        # 完整监控模式
        print("🚀 启动完整监控模式...")
        try:
            # 并行监控GPU和资源
            import threading

            def monitor_gpu_loop():
                while True:
                    monitor_gpu()
                    time.sleep(10)

            def monitor_resources_loop():
                monitor_resources(10)

            gpu_thread = threading.Thread(target=monitor_gpu_loop, daemon=True)
            resources_thread = threading.Thread(target=monitor_resources_loop, daemon=True)

            gpu_thread.start()
            resources_thread.start()

            # 主线程监控日志
            monitor_logs()

        except KeyboardInterrupt:
            print("\n⏹️ 停止完整监控")

    else:
        # 单独监控模式
        if args.logs:
            monitor_logs()
        if args.gpu:
            monitor_gpu()
        if args.progress:
            monitor_progress()
        if args.resources:
            monitor_resources()

if __name__ == '__main__':
    main()
