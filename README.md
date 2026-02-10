# 飞书 AI 机器人

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-1.1.0-brightgreen.svg)](https://github.com/Luys521/JiaWei_bot/releases)
[![AI Powered](https://img.shields.io/badge/🤖_AI-Powered-ff69b4.svg)](https://github.com/Luys521/JiaWei_bot)

> 🚀 基于 Flask 的企业级飞书 AI 机器人  
> 💡 支持智能对话、任务处理和 AI Agent 集成

---

## 📖 关于本项目

本项目采用**纯 Vibe Coding** 开发模式，由人类开发者与 AI 协作完成。

**🤖 AI 协作声明**：
> *作者信奉"懒惰是程序员的美德"，本项目的架构设计、代码实现、文档编写均由 AI 辅助完成。*  
> *如果你发现任何 AI 生成的痕迹，恭喜你，这正是我们想要的效果！*  
> *欢迎任何不服的 AI 进行代码审查和技术挑战。*

**💪 技术栈**：

- **后端框架**：Flask 2.3+
- **AI 集成**：支持多种主流 AI 提供商
- **开发工具**：现代化 Python 开发工具链
- **部署方式**：systemd / Docker

---

## 🙏 致谢

本项目得益于以下优秀的开源项目、工具和 AI 模型的支持。

向所有开源贡献者和 AI 技术提供者致敬！🌟

---

## ✨ 功能特性

- 🤖 **群聊AI助手**: @机器人触发智能对话，自动分类简单/复杂任务
- 💬 **私聊AI Agent**: 支持完整的 AI Agent 能力
- 🧵 **话题模式**: 复杂任务自动创建话题处理
- 🔌 **多AI提供商**: 灵活切换不同的 AI 服务
- 📊 **监控统计**: 请求统计、健康检查接口
- 🔒 **安全防护**: 频率限制、访问控制、事件验证

## 🏗️ 架构设计

```
┌─────────────────────────────────────────┐
│          飞书开放平台                    │
│         (Webhook 模式)                   │
└─────────────────┬───────────────────────┘
                  │
                  │ HTTP Webhook
                  ↓
┌─────────────────────────────────────────┐
│       应用服务器 (Flask)                 │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  主服务 (server.py)            │    │
│  └──────┬──────────────┬──────────┘    │
│         │              │                │
│  ┌──────▼──────┐  ┌───▼──────────┐    │
│  │  私聊消息   │  │  群聊消息     │    │
│  │  处理器     │  │  处理器       │    │
│  └──────┬──────┘  └───┬──────────┘    │
│         │              │                │
│  ┌──────▼──────┐  ┌───▼──────────┐    │
│  │  AI Agent   │  │  AI Processor │    │
│  │  Bridge     │  │  对话处理     │    │
│  └─────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

### 消息流程

**群聊消息**：
```
用户@机器人 → 接收处理 → 任务分类 → AI处理 → 卡片回复
```

**私聊消息**：
```
用户发消息 → 接收处理 → Agent桥接 → AI处理 → 文本回复
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

# 安装依赖
pip install -e .
```

### 配置

```bash
# 复制环境变量模板
cp configs/.env.example .env

# 编辑配置文件
vim .env
```

**关键配置项**:
```env
# 飞书应用配置
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_BOT_OPEN_ID=your_bot_open_id

# AI 服务配置
AI_PROVIDER=your_ai_provider
AI_API_KEY=your_api_key

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
```

### 运行

```bash
# 开发模式
make run

# 生产模式
make run-prod

# 或使用 Python 模块
python -m feishu_ai_bot.server
```

## 📁 项目结构

```
feishu_ai_bot/
├── src/feishu_ai_bot/          # 源代码
│   ├── server.py               # Flask主服务
│   ├── config.py               # 配置管理
│   ├── cli.py                  # CLI入口
│   ├── bot/                    # 飞书机器人模块
│   ├── ai/                     # AI处理模块
│   ├── tasks/                  # 任务处理模块
│   ├── cards/                  # 消息卡片构建
│   ├── security/               # 安全验证
│   └── monitoring/             # 监控统计
├── tests/                      # 测试
├── configs/                    # 配置模板
├── pyproject.toml              # 项目配置
└── Makefile                    # 常用命令
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

## 🔧 部署

详细的部署指南请参考 [DEPLOYMENT.md](DEPLOYMENT.md)，包括：

- 直接部署（有公网IP）
- 使用内网穿透（frp）
- 使用 systemd 服务
- 使用 Docker 容器
- 安全配置和故障排查

### 快速部署

#### 使用 systemd

```bash
# 复制服务文件
sudo cp deployment/feishu-bot.service /etc/systemd/system/

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start feishu-bot
sudo systemctl enable feishu-bot
```

### 使用 Docker

```bash
# 构建镜像
docker build -t feishu-ai-bot .

# 运行容器
docker run -d -p 8080:8080 --env-file .env feishu-ai-bot
```

## 📝 配置说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `FEISHU_APP_ID` | ✅ | 飞书应用ID |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用密钥 |
| `AI_PROVIDER` | ✅ | AI服务提供商 |
| `AI_API_KEY` | ✅ | AI服务API密钥 |
| `SERVER_PORT` | ❌ | 服务端口(默认8080) |

## 🔒 安全建议

- 请勿将 `.env` 文件提交到版本控制系统
- 定期更换 API 密钥
- 使用防火墙限制服务器访问
- 启用 HTTPS 加密通信
- 配置适当的访问控制策略

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

在提交代码前，请确保：
- 代码通过所有测试
- 遵循项目的代码风格
- 更新相关文档

## 📋 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的版本更新记录。

### 最新版本 v1.1.0

**🎉 重大更新**
- ✨ 完整重构为现代化 Python 包结构
- ✨ 添加 AI Agent 桥接器
- ✨ 使用 dataclass 管理配置，类型安全
- ✨ 完善的测试框架和 CI/CD
- 📚 完整的项目文档

**🐛 修复**
- 🔧 优化错误处理和日志记录
- 🔧 提升系统稳定性

**📦 依赖更新**
- 升级到 Python 3.9+
- 添加 pytest、black、mypy 等开发工具

## 📞 联系方式

- **GitHub Issues**: [提交问题](https://github.com/Luys521/JiaWei_bot/issues)
- **Pull Requests**: [贡献代码](https://github.com/Luys521/JiaWei_bot/pulls)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**注意**: 本项目仅供学习和研究使用，请遵守相关法律法规和服务条款。
