.PHONY: help install install-dev test test-cov lint format type-check clean docker-build docker-run deploy

# 默认目标
help:
	@echo "飞书AI机器人 - 可用命令:"
	@echo ""
	@echo "  make install      - 安装生产依赖"
	@echo "  make install-dev  - 安装开发依赖"
	@echo "  make test         - 运行测试"
	@echo "  make test-cov     - 运行测试并生成覆盖率报告"
	@echo "  make lint         - 运行代码检查"
	@echo "  make format       - 格式化代码"
	@echo "  make type-check   - 运行类型检查"
	@echo "  make clean        - 清理临时文件"
	@echo "  make run          - 启动开发服务器"
	@echo "  make deploy       - 部署到生产环境"
	@echo ""

# 安装
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

# 测试
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src/feishu_ai_bot --cov-report=term-missing --cov-report=html

test-unit:
	pytest tests/unit -v -m unit

test-integration:
	pytest tests/integration -v -m integration

# 代码质量
lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/feishu_ai_bot

# 清理
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# 运行
run:
	python -m feishu_ai_bot.server

run-prod:
	gunicorn -w 4 -b 0.0.0.0:8081 feishu_ai_bot.server:app

# 部署
deploy:
	bash scripts/deploy.sh

# Docker
docker-build:
	docker build -t feishu-ai-bot:latest .

docker-run:
	docker run -d --name feishu-bot -p 8081:8081 --env-file .env feishu-ai-bot:latest

docker-stop:
	docker stop feishu-bot
	docker rm feishu-bot

# 开发工具
shell:
	python -c "import IPython; IPython.embed()"

logs:
	tail -f logs/bot.log

# CI/CD
ci: lint type-check test

all: clean install-dev format lint type-check test-cov
