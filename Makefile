# 金融文本相似度分类竞赛 - 部署工具

.PHONY: help deploy install test train clean

# 默认目标
help:
	@echo "🐰 金融文本相似度分类竞赛 - 部署工具"
	@echo ""
	@echo "可用命令:"
	@echo "  make deploy    - 一键部署（推荐）"
	@echo "  make install   - 安装依赖"
	@echo "  make test      - 验证环境"
	@echo "  make train     - 执行训练"
	@echo "  make clean     - 清理临时文件"
	@echo "  make help      - 显示此帮助"

# 一键部署
deploy:
	@echo "🚀 开始一键部署..."
	python deploy.py

# 安装依赖
install:
	@echo "📦 安装项目依赖..."
	python install_deps.py

# 环境验证
test:
	@echo "🔍 验证环境配置..."
	python test_setup.py

# 执行训练
train:
	@echo "🚀 执行完整训练流程..."
	python main.py --step all

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	rm -rf __pycache__/
	rm -rf scripts/__pycache__/
	rm -rf *.pyc
	rm -rf .cache/
	@echo "✅ 清理完成"

# 查看状态
status:
	@echo "📊 项目状态检查..."
	@echo "Python版本: $$(python --version)"
	@echo "CUDA可用: $$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "检查失败")"
	@echo ""
	@echo "文件状态:"
	@ls -la data/ 2>/dev/null | head -3 || echo "  data/ 目录不存在"
	@ls -la models/ 2>/dev/null | head -3 || echo "  models/ 目录不存在"
	@ls -la results/ 2>/dev/null | head -3 || echo "  results/ 目录不存在"
