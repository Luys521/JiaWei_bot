# 飞书AI机器人

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

基于 Flask 的智能助手，支持群聊 @触发 和 私聊 OpenClaw 集成。

## ✨ 功能特性

- 🤖 **群聊AI助手**: @机器人触发智能对话，自动分类简单/复杂任务
- 💬 **私聊OpenClaw**: 完整AI Agent能力，可操作服务器文件系统
- 🧵 **话题模式**: 复杂任务自动创建话题处理
- 🔌 **多AI提供商**: DeepSeek、MiniMax、OpenAI
- 📊 **监控统计**: 请求统计、健康检查接口
- 🔒 **安全防护**: 频率限制、IP白名单、事件验证

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/feishu-ai-bot.git
cd feishu-ai-bot

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装
pip install -e .
```

### 配置

```bash
# 复制环境变量模板
cp configs/.env.example .env

# 编辑配置
vim .env
```

**关键配置项**:
```env
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_BOT_OPEN_ID=ou_xxx
TARGET_CHAT_ID=oc_xxx
AI_API_KEY=sk-xxx
```

### 运行

```bash
# 开发模式
make run

# 生产模式
make run-prod

# 或使用Python模块
python -m feishu_ai_bot.server
```

## 📁 项目结构

```
feishu_ai_bot/
├── src/feishu_ai_bot/          # 源代码
│   ├── server.py               # Flask主服务
│   ├── config.py               # 配置管理(dataclass)
│   ├── cli.py                  # CLI入口
│   ├── bot/feishu.py           # 飞书API交互
│   ├── ai/processor.py         # AI任务处理
│   ├── openclaw/bridge.py      # OpenClaw桥接
│   ├── tasks/processor.py      # 任务分类处理
│   ├── cards/builder.py        # 消息卡片构建
│   ├── security/validator.py   # 安全验证
│   └── monitoring/stats.py     # 监控统计
├── tests/                       # 测试
├── configs/                     # 配置模板
├── docs/                        # 文档
├── scripts/                     # 运维脚本
├── pyproject.toml               # 项目配置
└── Makefile                     # 常用命令
```

## 🧪 测试

```bash
# 运行所有测试
make test

# 运行单元测试
make test-unit

# 生成覆盖率报告
make test-cov
```

## 🛠️ 开发

```bash
# 安装开发依赖
make install-dev

# 代码格式化
make format

# 类型检查
make type-check

# 完整CI检查
make ci
```

## 📖 文档

- [部署指南](docs/DEPLOYMENT.md) - 详细部署步骤
- [架构设计](docs/ARCHITECTURE.md) - 系统架构说明
- [API文档](docs/API.md) - API接口文档

## 🔧 部署

### 使用 systemd (推荐)

```bash
sudo cp scripts/feishu-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start feishu-bot
sudo systemctl enable feishu-bot
```

### 使用 Docker

```bash
docker build -t feishu-ai-bot .
docker run -d -p 8081:8081 --env-file .env feishu-ai-bot
```

## 📝 配置说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `FEISHU_APP_ID` | ✅ | 飞书应用ID |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用密钥 |
| `AI_API_KEY` | ✅ | AI服务API密钥 |
| `OPENCLAW_TOKEN` | ❌ | OpenClaw认证令牌 |
| `SERVER_PORT` | ❌ | 服务端口(默认8081) |

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License
