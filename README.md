# 金融文本相似度分类竞赛 - 优化方案

## 🎯 目标

将模型准确率从基线**0.764**提升至**0.85+**，通过综合优化策略实现显著性能提升。

## ⚡ 一键部署（推荐）

**只需一行命令，自动完成环境配置、依赖安装和完整训练流程！**

```bash
# 一键部署（包含环境检查、依赖安装、数据处理、训练、推理、评估）
python deploy.py
```

**部署流程：**
1. 🔍 自动检测系统环境和GPU
2. 📦 智能安装项目依赖
3. ✅ 验证安装环境
4. 🚀 执行完整训练流程（数据→训练→推理→评估）
5. 📊 显示训练结果和竞赛提交指导

**预计耗时：** 90分钟 | **预期准确率：** 0.85+

## 📁 项目结构

```
model_training/
├── deploy.py                  # 🆕 一键部署脚本
├── main.py                    # 主部署脚本
├── requirements.txt           # 依赖列表
├── config/                    # 🆕 配置文件目录
│   ├── train_config.json      # 训练配置
│   └── environment.json       # 环境配置
├── scripts/                   # 核心脚本
│   ├── __init__.py           # 脚本包初始化
│   ├── data_processor.py     # 数据下载和分析
│   ├── model_trainer.py      # 模型训练和推理
│   ├── evaluate.py           # 性能评估
│   └── utils.py              # 工具函数
├── data/                     # 数据文件
│   ├── train.jsonl           # 训练数据
│   └── test.jsonl            # 测试数据
├── models/                   # 模型输出目录
├── results/                  # 分析结果
│   ├── dataset_analysis/     # 数据集分析
│   ├── evaluation_results/   # 评估结果
│   └── enhanced_result.jsonl # 竞赛提交文件
├── logs/                     # 日志文件
└── docs/                     # 文档
```

## 🚀 快速开始

### 1. 一键部署（最简单）
```bash
# 自动检测环境，安装依赖，完整训练流程
python deploy.py
```

### 2. 标准部署流程
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

### 3. 执行训练流程
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

### 4. 手动执行各模块
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

## 💻 系统要求

### 最低配置
- **Python**: 3.8+
- **内存**: 16GB RAM
- **存储**: 50GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **Python**: 3.10+
- **内存**: 32GB RAM
- **GPU**: NVIDIA GPU with 8GB+ VRAM (推荐 RTX 3060/3070/3080 或 A100)
- **CUDA**: 11.8+ (如果使用GPU)

### 支持平台
- ✅ **魔搭平台** (ModelScope)
- ✅ **Linux** (Ubuntu 18.04+)
- ✅ **macOS** (10.15+)
- ✅ **Windows** (10/11 with WSL2)

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

### 自动提交准备
一键部署完成后，结果文件会自动生成在正确位置：

```bash
# 检查结果文件是否生成
ls -la results/

# 如果使用一键部署，文件已准备好
# 直接提交 results/enhanced_result.jsonl 即可
```

### 手动提交准备
如果使用分步执行，需要手动复制结果：

```bash
# 转换结果格式（如果需要）
cp results/enhanced_result.jsonl results/result.json

# 提交 result.json 到竞赛页面
```

### 提交检查清单
- ✅ 结果文件存在: `results/enhanced_result.jsonl`
- ✅ 文件格式正确: JSONL 格式，每行一个预测结果
- ✅ 预测数量正确: 3000条测试样本
- ✅ 输出格式正确: 每行只包含数字 0 或 1

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

### 🚨 一键部署失败？
如果 `python deploy.py` 失败：

1. **检查Python版本**：
   ```bash
   python --version  # 应为 3.8+
   ```

2. **手动执行各步骤**：
   ```bash
   # 1. 安装依赖
   python install_deps.py

   # 2. 验证环境
   python test_setup.py

   # 3. 执行训练
   python main.py --step all
   ```

3. **查看详细日志**：
   ```bash
   # 查看安装日志
   cat logs/deps.log

   # 查看环境日志
   cat logs/env.log

   # 查看训练日志
   tail -f logs/train.log
   ```

### 常见问题

1. **数据集下载失败**：
   ```bash
   # 使用备用数据下载
   python scripts/data_processor.py download
   ```

2. **GPU内存不足**：
   - 减小 `per_device_train_batch_size` (配置文件中)
   - 增加 `gradient_accumulation_steps`
   - 或使用CPU训练（很慢）

3. **依赖版本冲突**：
   ```bash
   # 升级关键依赖
   pip install --upgrade torch transformers

   # 或使用修复脚本
   python fix_modelscope_deps.py
   ```

4. **网络问题**：
   - 检查网络连接
   - 魔搭平台可能需要代理

### 调试技巧
- **实时监控**: `tail -f logs/train.log`
- **GPU监控**: `watch -n 1 nvidia-smi`
- **内存监控**: `htop` 或 `top`
- **环境验证**: `python -c "import torch; print('CUDA:', torch.cuda.is_available())"`

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

### 💡 使用建议

#### 🚀 新手推荐
```bash
# 第一选择：一键部署，最简单
python deploy.py

# 第二选择：标准流程
python main.py --step all
```

#### 🔧 开发者选项
1. **初次运行**：使用 `python deploy.py` 一键部署
2. **调试优化**：分步执行，观察每步结果
   ```bash
   python main.py --step analysis   # 先分析数据
   python main.py --step train      # 单独训练
   python main.py --step inference  # 测试推理
   python main.py --step evaluate   # 查看评估
   ```
3. **性能调优**：根据评估结果调整 `config/train_config.json`
4. **竞赛提交**：确保使用最佳模型进行推理

#### ⚡ 快速检查
```bash
# 检查GPU和环境
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# 查看训练进度
tail -f logs/train.log

# 检查结果
ls -la results/
```

---

**祝竞赛成功！🚀**
