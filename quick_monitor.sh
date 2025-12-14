#!/bin/bash
# 快速训练监控脚本

echo "🚀 快速训练状态检查"
echo "===================="

# 检查GPU状态
echo "🎮 GPU状态:"
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv || echo "nvidia-smi不可用"

echo ""
echo "📊 训练进度:"

# 检查输出目录
OUTPUT_DIR="./output_qwen2_7b_optimized"
if [ -d "$OUTPUT_DIR" ]; then
    echo "输出目录: $OUTPUT_DIR"

    # 检查检查点
    CHECKPOINTS=$(ls -d $OUTPUT_DIR/checkpoint-* 2>/dev/null | wc -l)
    echo "检查点数量: $CHECKPOINTS"

    if [ $CHECKPOINTS -gt 0 ]; then
        LATEST_CP=$(ls -d $OUTPUT_DIR/checkpoint-* | sort -V | tail -1)
        echo "最新检查点: $(basename $LATEST_CP)"
    fi

    # 检查日志
    LOG_DIR="$OUTPUT_DIR/logs"
    if [ -d "$LOG_DIR" ]; then
        LOG_FILES=$(ls $LOG_DIR/*.log 2>/dev/null | wc -l)
        echo "日志文件数: $LOG_FILES"

        if [ $LOG_FILES -gt 0 ]; then
            echo "最新日志:"
            tail -5 $LOG_DIR/*.log | head -10
        fi
    fi
else
    echo "⚠️ 输出目录不存在，请先开始训练"
fi

echo ""
echo "💡 监控命令:"
echo "  python monitor_training.py --logs      # 实时日志"
echo "  python monitor_training.py --gpu       # GPU状态"
echo "  python monitor_training.py --progress  # 训练进度"
echo "  python monitor_training.py --all       # 完整监控"
