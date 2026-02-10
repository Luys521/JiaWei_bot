# 飞书AI机器人 - 项目结构文档

## 目录结构

```
feishu_ai_bot/
├── src/                              # 源代码目录
│   └── feishu_ai_bot/               # 主包目录
│       ├── __init__.py              # 包初始化
│       ├── _version.py              # 版本信息
│       ├── config.py                # 配置管理（使用 dataclass）
│       ├── server.py                # Flask 主服务（重构后）
│       ├── cli.py                   # 命令行接口
│       ├── bot/                     # 飞书机器人模块
│       │   ├── __init__.py
│       │   ├── feishu.py           # FeishuBot 类
│       │   └── webhook.py          # Webhook 处理器
│       ├── ai/                      # AI 处理模块
│       │   ├── __init__.py
│       │   ├── processor.py        # AIProcessor
│       │   └── providers.py        # AI 提供商接口
│       ├── openclaw/               # OpenClaw 集成
│       │   ├── __init__.py
│       │   └── bridge.py           # OpenClawBridge
│       ├── tasks/                  # 任务处理
│       │   ├── __init__.py
│       │   └── processor.py        # TaskProcessor
│       ├── cards/                  # 卡片构建
│       │   ├── __init__.py
│       │   └── builder.py          # CardBuilder
│       ├── security/               # 安全模块
│       │   ├── __init__.py
│       │   └── validator.py        # SecurityValidator
│       └── monitoring/             # 监控模块
│           ├── __init__.py
│           └── stats.py            # StatsCollector
│
├── tests/                           # 测试目录
│   ├── __init__.py
│   ├── conftest.py                 # pytest fixtures
│   ├── unit/                       # 单元测试
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_openclaw_bridge.py
│   │   └── test_feishu_bot.py
│   ├── integration/                # 集成测试
│   │   ├── __init__.py
│   │   └── test_webhook.py
│   └── e2e/                        # 端到端测试
│       └── __init__.py
│
├── docs/                           # 文档
│   ├── README.md
│   ├── api.md
│   ├── architecture.md
│   └── deployment.md
│
├── configs/                        # 配置模板
│   ├── .env.example
│   └── openclaw.json.example
│
├── scripts/                        # 运维脚本
│   ├── deploy.sh
│   ├── start.sh
│   └── setup_openclaw.sh
│
├── .github/                        # GitHub 配置
│   └── workflows/
│       └── ci.yml                  # CI/CD 工作流
│
├── pyproject.toml                  # 现代 Python 项目配置
├── setup.py                        # 向后兼容的安装配置
├── requirements.txt                # 生产依赖
├── requirements-dev.txt            # 开发依赖
├── Makefile                        # 常用命令
├── pytest.ini                      # 测试配置
├── .flake8                         # 代码风格配置
└── .gitignore                      # Git 忽略文件
```

## 主要改进

### 1. 使用 dataclass 管理配置

旧代码使用全局变量和 `*`: 导入配置，新代码使用类型化的 dataclass：

```python
# 旧代码
from config import *
FEISHU_APP_ID

# 新代码
from feishu_ai_bot.config import load_config
config = load_config()
config.feishu.app_id
```

### 2. 显式导入替代通配符导入

```python
# 旧代码
from config import *

# 新代码
from feishu_ai_bot.config import load_config, AppConfig
```

### 3. 包化结构

- 所有代码移到 `src/feishu_ai_bot/` 目录
- 使用 `pyproject.toml` 定义包元数据
- 可通过 `pip install -e .` 安装为可编辑模式

### 4. 代码质量工具

- **black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码风格检查
- **mypy**: 类型检查
- **pytest**: 测试框架

### 5. CI/CD

GitHub Actions 工作流自动化：
- 代码格式检查
- 类型检查
- 单元测试
- 覆盖率报告
- 自动构建

## 使用方式

### 开发环境设置

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装开发依赖
make install-dev

# 3. 安装 pre-commit hooks
pre-commit install
```

### 常用命令

```bash
# 运行测试
make test

# 代码格式化
make format

# 类型检查
make type-check

# 完整检查（CI）
make ci

# 启动服务
make run
```

## 迁移说明

从旧结构迁移到新结构：

1. 代码移动到 `src/feishu_ai_bot/`
2. 导入语句从 `from config import X` 改为 `from feishu_ai_bot.config import X`
3. 配置访问从全局变量改为 `config.xxx`
4. 添加 `__init__.py` 到每个模块

## 向后兼容

旧的 `deploy/` 目录暂时保留，以便平滑迁移。
建议迁移完成后删除。
