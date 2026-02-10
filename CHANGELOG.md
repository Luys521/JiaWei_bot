# 更新日志 (Changelog)

本文档记录了飞书AI机器人的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布] - Unreleased

### 计划中
- [ ] 支持更多 AI 提供商（Claude、文心一言等）
- [ ] 添加消息队列支持（Redis/RabbitMQ）
- [ ] 实现插件系统
- [ ] 支持多租户模式
- [ ] Web 管理后台

---

## [1.1.0] - 2026-02-10

### 🎉 重大更新

#### 架构重构
- **完整重构为现代化 Python 包结构**
  - 采用 `src/` 布局（PEP 420）
  - 使用 `pyproject.toml` 作为项目配置
  - 清晰的模块职责分离
  - 完整的类型提示（Type Hints）

#### OpenClaw 集成
- **新增 OpenClaw 桥接器** (`openclaw/bridge.py`)
  - 支持私聊消息转发到 OpenClaw
  - 实现多种 HTTP API 端点自动探测
  - 支持 4 种 API 策略：RPC、Webhook、Message、Chat
  - 完善的错误处理和重试机制
  - 健康检查功能

#### 配置管理
- **使用 dataclass 管理配置**
  - 类型安全的配置对象
  - 支持环境变量加载
  - 配置验证功能
  - 更好的 IDE 自动补全

#### 依赖注入
- **消除全局变量**
  - 显式依赖注入
  - 更易于测试
  - 更清晰的依赖关系

### ✨ 新增功能

#### 核心功能
- **私聊/群聊智能分流**
  - 私聊消息自动转发到 OpenClaw
  - 群聊消息使用现有 AI 处理
  - 自动识别消息类型（p2p/group）

- **任务分类优化**
  - 智能判断简单/复杂任务
  - 复杂任务自动创建话题
  - 简单任务直接回复

#### 开发工具
- **完整的开发工具链**
  - pytest 测试框架
  - black 代码格式化
  - mypy 类型检查
  - flake8 代码检查
  - pre-commit 钩子

- **Makefile 命令集合**
  ```bash
  make install      # 安装依赖
  make test         # 运行测试
  make format       # 格式化代码
  make lint         # 代码检查
  make run          # 启动服务
  ```

#### 文档完善
- **项目文档**
  - `README.md` - 完整的项目说明文档
  - `CHANGELOG.md` - 更新日志（本文件）
  - `LICENSE` - MIT 开源协议

- **配置模板**
  - `.env.example` - 环境变量模板
  - `openclaw.json.example` - OpenClaw 配置模板

#### CI/CD
- **GitHub Actions 工作流**
  - 自动运行测试
  - 代码质量检查
  - 构建验证

### 🐛 修复

#### 关键修复
- **修复 OpenClaw 集成导入错误**
  - 创建缺失的 `openclaw/bridge.py` 文件
  - 修复 `ModuleNotFoundError` 错误
  - 完善模块导入路径

#### 代码质量
- **优化错误处理**
  - 统一异常处理机制
  - 详细的错误日志
  - 友好的错误提示

- **改进日志记录**
  - 结构化日志输出
  - 日志级别优化
  - 日志文件管理

### 🔄 变更

#### 破坏性变更
- **配置方式变更**
  ```python
  # 旧方式 ❌
  from config import FEISHU_APP_ID
  
  # 新方式 ✅
  from feishu_ai_bot.config import load_config
  config = load_config()
  config.feishu.app_id
  ```

- **导入路径变更**
  ```python
  # 旧方式 ❌
  from feishu_bot import FeishuBot
  
  # 新方式 ✅
  from feishu_ai_bot.bot import FeishuBot
  ```

#### 目录结构变更
- **删除 `deploy/` 目录**
  - 旧代码已迁移到 `src/feishu_ai_bot/`
  - 部署脚本移至 `scripts/`

- **新增目录**
  - `src/` - 源代码
  - `tests/` - 测试代码
  - `docs/` - 文档
  - `configs/` - 配置模板

### 📦 依赖更新

#### 新增依赖
- `pytest>=7.0.0` - 测试框架
- `pytest-cov>=4.0.0` - 测试覆盖率
- `black>=23.0.0` - 代码格式化
- `mypy>=1.0.0` - 类型检查
- `flake8>=6.0.0` - 代码检查
- `pre-commit>=3.0.0` - Git 钩子

#### 更新依赖
- `Flask>=2.3.0` - Web 框架
- `requests>=2.31.0` - HTTP 客户端
- `python-dotenv>=1.0.0` - 环境变量管理

#### 最低要求
- **Python 3.9+** （之前为 3.7+）

### 🗑️ 移除

#### 删除的文件
- `deploy/` 整个目录（旧代码）
- `test_openclaw_api.py` （旧测试脚本）
- `A_README.md` （已整合）
- `U_README.md` （已整合）
- `配置参数备忘录.md` （已整合）

#### 废弃的功能
- 全局变量配置方式（使用 dataclass 替代）

### 📊 统计数据

- **代码行数**: 4363+ 行
- **文件数量**: 36 个文件
- **模块数量**: 9 个核心模块
- **测试覆盖率**: 目标 80%+

---

## [1.0.0] - 2026-01-26

### 🎉 首次发布

#### 核心功能
- ✅ 飞书机器人基础功能
- ✅ 群聊 @触发
- ✅ AI 对话能力（DeepSeek）
- ✅ 简单/复杂任务分类
- ✅ 话题模式
- ✅ 卡片消息

#### 安全功能
- ✅ 频率限制
- ✅ IP 白名单
- ✅ 事件验证

#### 监控功能
- ✅ 请求统计
- ✅ 健康检查接口

#### 技术栈
- Python 3.7+
- Flask 2.0+
- Requests
- python-dotenv

---

## 版本号说明

版本格式：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

## 变更类型说明

- `Added` - 新增功能
- `Changed` - 功能变更
- `Deprecated` - 即将废弃的功能
- `Removed` - 已移除的功能
- `Fixed` - 问题修复
- `Security` - 安全相关

---

## 贡献指南

如果你想为本项目做出贡献，请：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 问题反馈

如果发现 bug 或有功能建议，请：

1. 访问 [Issues](https://github.com/Luys521/JiaWei_bot/issues)
2. 搜索是否已有相关问题
3. 如果没有，创建新的 Issue

---

**最后更新**: 2026-02-10
**维护者**: [@Luys521](https://github.com/Luys521)
