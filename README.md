# 金融文本相似度分类竞赛 - 优化方案

## 🎯 目标

将模型准确率从基线**0.764**提升至**0.85+**，通过综合优化策略实现显著性能提升。

## 📁 项目结构

```
model_training/
├── main.py                     # 主部署脚本
├── requirements.txt            # 依赖列表
├── scripts/                    # 核心脚本
│   ├── __init__.py            # 脚本包初始化
│   ├── data_processor.py      # 数据下载和分析
│   ├── model_trainer.py       # 模型训练和推理
│   ├── evaluate.py            # 性能评估
│   └── utils.py               # 工具函数
├── data/                      # 数据文件
├── models/                    # 模型输出
├── results/                   # 分析结果
└── docs/                      # 文档
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 方式1: 自动安装脚本（推荐）
python install_deps.py

# 方式2: 手动安装
pip install -r requirements.txt

# 魔搭平台特殊处理
python fix_modelscope_deps.py

# 验证安装
python test_setup.py
```

#### 魔搭平台注意事项
如果在魔搭平台遇到依赖冲突：
```bash
# 自动修复脚本
python fix_modelscope_deps.py

# 或跳过环境检查直接运行
python main.py --skip-env-check --step all
```

### 2. 一键运行（推荐）
```bash
# 完整流程：数据处理 -> 训练 -> 推理 -> 评估
python main.py --step all

# 如果环境检查有问题，可以跳过
python main.py --skip-env-check --step all

# 或者分步执行
python main.py --step analysis    # 数据分析
python main.py --step train       # 模型训练
python main.py --step inference   # 模型推理
python main.py --step evaluate    # 性能评估
```

### 3. 手动执行
```bash
# 数据处理
python scripts/data_processor.py all

# 模型训练
python scripts/model_trainer.py train

# 模型推理
python scripts/model_trainer.py inference

# 性能评估
python scripts/evaluate.py
```

## 📊 预期性能

| 配置 | 准确率 | 预期排名 | 训练时间 |
|------|--------|----------|----------|
| 基线 | 0.764 | - | - |
| 优化版 | 0.85+ | 前30名 | ~90分钟 |
| 高级优化 | 0.90+ | 前20名 | ~120分钟 |

## 🎯 核心优化策略

### Prompt优化
- 更清晰的金融语境指导
- 明确的输出格式要求
- 专业的任务描述

### 超参数调优
- 学习率：1.8e-4（平衡收敛和稳定性）
- LoRA配置：rank=16, alpha=32
- 训练轮数：5轮（早停机制）
- 批次大小：有效batch_size=16

### 推理优化
- 智能输出后处理
- 异常值处理和清洗
- 确定性推理（temperature=0）

### 训练策略
- 验证集评估和早停
- 余弦学习率调度
- 梯度累积和检查点

## 🏆 竞赛提交

训练完成后，按以下步骤提交：

```bash
# 转换结果格式
cp results/enhanced_result.jsonl results/result.json

# 提交result.json到竞赛页面
```

## 📋 详细说明

### 数据集信息
- 训练集：32,000条样本
- 测试集：3,000条样本
- 类别分布：相似(1): 41.4%, 不相似(0): 58.6%

### 模型配置
- 基础模型：Qwen/Qwen3-4B-Instruct-2507
- 微调方法：LoRA
- 训练参数：详细配置见`scripts/model_trainer.py`

### 评估指标
- 准确率 (Accuracy)
- 精确率/召回率/F1 (Precision/Recall/F1)
- 混淆矩阵分析

## 🔧 故障排除

### 常见问题
1. **数据集下载失败**：
   ```bash
   # 使用备用数据下载
   python scripts/data_processor.py download
   ```

2. **显存不足**：
   - 减小`per_device_train_batch_size`
   - 增加`gradient_accumulation_steps`

3. **依赖问题**：
   ```bash
   pip install --upgrade torch transformers
   ```

### 调试技巧
- 查看训练日志：`tail -f logs/train.log`
- 检查GPU使用：`nvidia-smi`
- 验证安装：`python -c "import torch; print('CUDA:', torch.cuda.is_available())"`

## 📈 性能监控

### 训练监控
```bash
# 查看实时训练进度
tail -f logs/train.log

# 监控GPU使用
watch -n 1 nvidia-smi
```

### 评估结果
训练完成后，评估结果保存在`results/evaluation_results/`目录中：
- `evaluation_report.json` - 详细评估报告
- `confusion_matrix.png` - 混淆矩阵可视化
- `error_analysis.png` - 错误分析图表

## 🎉 开始竞赛！

**目标：90分钟内达到0.85+准确率，冲刺前30名！**

### 使用建议
1. **初次运行**：使用`python main.py --step all`一键执行
2. **调试优化**：分步执行，观察每步结果
3. **性能调优**：根据评估结果调整超参数
4. **竞赛提交**：确保使用最佳模型进行推理

---

**祝竞赛成功！🚀**
