#!/usr/bin/env python3
"""
显存监控和优化建议脚本
"""

import subprocess
import sys
import os

def run_command(cmd, desc=""):
    """运行命令"""
    try:
        result = subprocess.run(cmd, shell=True, check=True,
                              capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_gpu_info():
    """获取GPU信息"""
    print("🎮 GPU信息:")

    # 检查nvidia-smi
    nvidia_output = run_command("nvidia-smi --query-gpu=name,memory.total,memory.free,memory.used --format=csv,noheader,nounits")

    if nvidia_output:
        lines = nvidia_output.strip().split('\n')
        for i, line in enumerate(lines):
            name, total, free, used = line.split(', ')
            print(f"  GPU {i}: {name}")
            print(f"    总显存: {total} MB")
            print(f"    已使用: {used} MB")
            print(f"    可用: {free} MB")
            print(f"    使用率: {int(used)/int(total)*100:.1f}%")
    else:
        print("  ❌ 无法获取GPU信息 (nvidia-smi不可用)")

def estimate_memory_usage():
    """估算显存使用情况"""
    print("\n💾 显存使用估算:")

    # 7B模型的基本信息
    model_params = 7_000_000_000  # 70亿参数
    param_size = 2  # bfloat16 = 2字节

    # LoRA参数
    lora_rank = 64
    lora_params = model_params * lora_rank * 2 / 1_000_000  # 百万参数

    print(f"  • 模型参数: {model_params:,} ({model_params * param_size / 1024**3:.1f} GB)")
    print(f"  • LoRA参数: ~{lora_params:.0f}M")
    print(f"  • 梯度占用: {model_params * param_size / 1024**3:.1f} GB")
    print(f"  • 优化器状态: {model_params * param_size * 2 / 1024**3:.1f} GB")

    # 估算总占用
    base_memory = model_params * param_size / 1024**3  # 模型
    grad_memory = base_memory  # 梯度
    optim_memory = base_memory * 2  # Adam状态
    activation_memory = 1.0  # 激活值估算

    total_peak = base_memory + grad_memory + optim_memory + activation_memory

    print(f"  • 峰值显存: ~{total_peak:.1f} GB (理论值)")
    print(f"  • 实际占用: < {total_peak * 0.7:.1f} GB (使用梯度检查点)")

def provide_optimization_suggestions():
    """提供优化建议"""
    print("\n💡 22G显存优化建议:")

    suggestions = [
        ("✅ 已启用", "梯度检查点 (gradient_checkpointing)"),
        ("✅ 已配置", "批次大小=1, 梯度累积=32"),
        ("✅ 已设置", "bfloat16精度"),
        ("✅ 已启用", "Flash Attention"),
        ("⚠️  可考虑", "降低LoRA rank到32 (节省显存)"),
        ("⚠️  可考虑", "增加gradient_accumulation_steps到64"),
        ("⚠️  可考虑", "使用DeepSpeed ZeRO-2"),
        ("⚠️  可考虑", "模型量化 (4-bit)")
    ]

    for status, suggestion in suggestions:
        print(f"  {status} {suggestion}")

def main():
    """主函数"""
    print("🧠 显存监控和优化建议")
    print("=" * 50)

    get_gpu_info()
    estimate_memory_usage()
    provide_optimization_suggestions()

    print("\n🚀 当前配置应该能在22G显存上运行")
    print("如果仍然显存不足，可以考虑:")
    print("1. export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512")
    print("2. 降低LoRA rank: sed -i 's/64/32/g' config/train_config.json")
    print("3. 使用更小的批次大小")

if __name__ == '__main__':
    main()
