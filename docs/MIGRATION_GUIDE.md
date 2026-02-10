# 代码迁移指南

## 文件映射表

| 旧文件 (deploy/) | 新文件 (src/feishu_ai_bot/) | 状态 |
|------------------|----------------------------|------|
| config.py | config.py | ✅ 已迁移 - 使用dataclass |
| feishu_bot.py | bot/feishu.py | ✅ 已迁移 - 显式参数 |
| ai_processor.py | ai/processor.py | 📝 需迁移 - 修改导入 |
| openclaw_bridge.py | openclaw/bridge.py | ✅ 已迁移 |
| task_processor.py | tasks/processor.py | 📝 需迁移 - 修改导入 |
| card_builder.py | cards/builder.py | 📝 需迁移 - 直接复制 |
| security.py | security/validator.py | 📝 需迁移 - 修改导入 |
| monitoring.py | monitoring/stats.py | 📝 需迁移 - 修改导入 |
| bot_server.py | server.py | 📝 需重构 - 新架构主服务 |

## 导入语句修改对照

### 1. 配置导入

**旧代码:**
```python
from config import *
# 使用: FEISHU_APP_ID
```

**新代码:**
```python
from feishu_ai_bot.config import load_config

config = load_config()
# 使用: config.feishu.app_id
```

### 2. AI配置传入

**旧代码:**
```python
from config import get_ai_config
ai_processor = AITaskProcessor(WORKSPACE_DIR, get_ai_config())
```

**新代码:**
```python
from feishu_ai_bot.config import load_config
from feishu_ai_bot.ai.processor import AITaskProcessor

config = load_config()
ai_processor = AITaskProcessor(config.workspace_dir, config.ai)
```

### 3. 飞书机器人初始化

**旧代码:**
```python
from feishu_bot import FeishuBot
bot = FeishuBot()  # 从全局变量读取配置
```

**新代码:**
```python
from feishu_ai_bot.bot import FeishuBot
from feishu_ai_bot.config import load_config

config = load_config()
bot = FeishuBot(
    app_id=config.feishu.app_id,
    app_secret=config.feishu.app_secret,
    encrypt_key=config.feishu.encrypt_key,
    verification_token=config.feishu.verification_token
)
```

## 配置访问修改对照

| 旧变量 | 新访问方式 |
|--------|-----------|
| `FEISHU_APP_ID` | `config.feishu.app_id` |
| `FEISHU_APP_SECRET` | `config.feishu.app_secret` |
| `TARGET_CHAT_ID` | `config.feishu.target_chat_id` |
| `SERVER_PORT` | `config.server.port` |
| `AI_PROVIDER` | `config.ai.provider` |
| `AI_API_KEY` | `config.ai.api_key` |
| `OPENCLAW_ENABLED` | `config.openclaw.enabled` |
| `OPENCLAW_TOKEN` | `config.openclaw.token` |
| `WORKSPACE_DIR` | `config.workspace_dir` |

## 快速迁移步骤

### 第1步: 安装新架构依赖
```bash
cd /path/to/feishu_ai_bot
pip install -e .
```

### 第2步: 逐步迁移模块

对每个模块执行:
1. 复制文件到新位置
2. 修改导入语句
3. 修改配置访问方式
4. 运行测试验证

### 第3步: 验证迁移
```bash
# 检查导入
python -c "from feishu_ai_bot.config import load_config; print('✓ config')"
python -c "from feishu_ai_bot.bot import FeishuBot; print('✓ bot')"
python -c "from feishu_ai_bot.ai.processor import AITaskProcessor; print('✓ ai')"

# 运行测试
make test
```

## 常见问题和解决方案

### Q1: ImportError: cannot import name 'X'
**原因**: 导入路径错误或模块未创建
**解决**: 检查 `__init__.py` 是否存在，确认导入路径正确

### Q2: AttributeError: 'AppConfig' object has no attribute 'X'
**原因**: 配置项名称变更
**解决**: 检查新的配置结构，使用正确的属性名

### Q3: ModuleNotFoundError: No module named 'feishu_ai_bot'
**原因**: 包未安装
**解决**: 运行 `pip install -e .`

## 完全迁移后的目录结构

```
feishu_ai_bot/
├── src/
│   └── feishu_ai_bot/
│       ├── __init__.py
│       ├── _version.py
│       ├── config.py          ✅
│       ├── server.py          📝 需创建
│       ├── bot/
│       │   ├── __init__.py
│       │   └── feishu.py      ✅
│       ├── ai/
│       │   ├── __init__.py
│       │   └── processor.py   📝 需迁移
│       ├── openclaw/
│       │   ├── __init__.py
│       │   └── bridge.py      ✅
│       ├── tasks/
│       │   ├── __init__.py
│       │   └── processor.py   📝 需迁移
│       ├── cards/
│       │   ├── __init__.py
│       │   └── builder.py     📝 需迁移
│       ├── security/
│       │   ├── __init__.py
│       │   └── validator.py   📝 需迁移
│       └── monitoring/
│           ├── __init__.py
│           └── stats.py       📝 需迁移
├── tests/                     ✅
├── configs/                   ✅
├── scripts/                   ✅
├── deploy/                    (旧代码，迁移后删除)
├── pyproject.toml             ✅
├── Makefile                   ✅
└── README_NEW.md              ✅
```

## 迁移检查清单

- [ ] 安装开发依赖: `make install-dev`
- [ ] 迁移 config.py
- [ ] 迁移 feishu_bot.py
- [ ] 迁移 ai_processor.py
- [ ] 迁移 openclaw_bridge.py
- [ ] 迁移 task_processor.py
- [ ] 迁移 card_builder.py
- [ ] 迁移 security.py
- [ ] 迁移 monitoring.py
- [ ] 重构 bot_server.py
- [ ] 编写/更新测试
- [ ] 运行测试: `make test`
- [ ] 运行代码检查: `make ci`
- [ ] 验证功能正常
- [ ] 删除旧的 deploy/ 目录
- [ ] 更新文档

## 回滚方案

如果迁移出现问题:
1. 保留 deploy/ 目录不动
2. 临时切换回旧代码
3. 修复问题后继续迁移

## 帮助和支持

如遇到问题，请检查:
1. 所有 `__init__.py` 文件是否存在
2. 导入路径是否正确
3. 是否运行了 `pip install -e .`
4. 配置文件路径是否正确
