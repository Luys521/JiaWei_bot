# 飞书 AI 机器人 | JiaWei Bot

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-1.1.0-brightgreen.svg)](https://github.com/Luys521/JiaWei_bot/releases)
[![AI Powered](https://img.shields.io/badge/🤖_AI-Powered-ff69b4.svg)](https://github.com/Luys521/JiaWei_bot)

> 🚀 珈伟新能的智能飞书机器人 - 基于 Flask 的企业级 AI 助手  
> 💡 目标是为了实现智能客服和 Agent 办公集成

---

## 📖 关于本项目

本项目采用**纯 Vibe Coding** 开发模式，由人类开发者与 AI 协作完成。

**🤖 AI 协作声明**：
> *作者信奉"懒惰是程序员的美德"，本项目的架构设计、代码实现、文档编写均由 AI 辅助完成。*  
> *如果你发现任何 AI 生成的痕迹，恭喜你，这正是我们想要的效果！*  
> *欢迎任何不服的 AI 进行代码审查和技术挑战。*

**💪 技术栈**：

- **后端框架**：Flask 2.3+
- **AI 集成**：DeepSeek、Kimi 2.5
- **开发工具**：OpenCode/ Trae/ StepFun
- **部署方式**：systemd / Docker

---

## 🙏 致谢

本项目得益于以下优秀的开源项目、工具和 AI 模型的支持：

- 免费的大模型：https://integrate.api.nvidia.com/v1
- 免费的CLI/IDE：OpenCode / TraeCN / StepFun

---

向所有开源贡献者和 AI 技术提供者致敬！🌟 正是因为有了你们的卓越工作，本项目才得以实现。

## ✨ 功能特性

- 🤖 **群聊AI助手**: @机器人触发智能对话，自动分类简单/复杂任务
- 💬 **私聊OpenClaw**: 完整AI Agent能力，可操作服务器文件系统
- 🧵 **话题模式**: 复杂任务自动创建话题处理
- 🔌 **多AI提供商**: DeepSeek、MiniMax、OpenAI
- 📊 **监控统计**: 请求统计、健康检查接口
- 🔒 **安全防护**: 频率限制、IP白名单、事件验证

## 🏗️ 架构设计

```
┌─────────────────────────────────────────┐
│          飞书开放平台                    │
│      (单一应用 - Webhook 模式)          │
└─────────────────┬───────────────────────┘
                  │
                  │ HTTP Webhook
                  ↓
┌─────────────────────────────────────────┐
│       远端服务器 (Flask)                 │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  server.py (主服务)            │    │
│  │  端口: 8081                     │    │
│  └──────┬──────────────┬──────────┘    │
│         │              │                │
│  ┌──────▼──────┐  ┌───▼──────────┐    │
│  │  私聊消息   │  │  群聊消息     │    │
│  │  (p2p)      │  │  (group)      │    │
│  └──────┬──────┘  └───┬──────────┘    │
│         │              │                │
│  ┌──────▼──────┐  ┌───▼──────────┐    │
│  │  OpenClaw   │  │  AI Processor │    │
│  │  Bridge     │  │  (DeepSeek)   │    │
│  │  Agent能力  │  │  对话能力     │    │
│  └─────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

### 消息流程

**群聊消息**：
```
用户@机器人 → Flask接收 → 任务分类 → AI处理 → 卡片回复
```

**私聊消息**：
```
用户发消息 → Flask接收 → OpenClaw桥接 → Agent处理 → 文本回复
```

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/Luys521/JiaWei_bot.git
cd JiaWei_bot

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

详细的部署步骤和架构说明请参考本 README 文档的相关章节。

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

## 📋 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的版本更新记录。

### 最新版本 v1.1.0 (2026-02-10)

**🎉 重大更新**
- ✨ 完整重构为现代化 Python 包结构
- ✨ 添加 OpenClaw 桥接器，支持私聊 AI Agent
- ✨ 使用 dataclass 管理配置，类型安全
- ✨ 完善的测试框架和 CI/CD
- 📚 完整的项目文档

**🐛 修复**
- 🔧 修复 OpenClaw 集成的导入错误
- 🔧 优化错误处理和日志记录

**📦 依赖更新**
- 升级到 Python 3.9+
- 添加 pytest、black、mypy 等开发工具

查看完整更新历史：[CHANGELOG.md](CHANGELOG.md)

## 📞 联系方式

- **WeiXin**:luyushun007
- **邮箱**: luyushun@qq.com 

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
