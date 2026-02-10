#!/usr/bin/env python3
"""代码迁移脚本

将旧架构代码从 deploy/ 迁移到新架构 src/feishu_ai_bot/
"""

import os
import shutil
from pathlib import Path


def main():
    """主迁移函数"""
    print("🚀 开始迁移代码到新架构...")
    
    # 项目根目录
    root = Path(__file__).parent.parent
    
    # 创建必要的目录结构
    dirs_to_create = [
        "src/feishu_ai_bot",
        "src/feishu_ai_bot/bot",
        "src/feishu_ai_bot/ai",
        "src/feishu_ai_bot/openclaw",
        "src/feishu_ai_bot/tasks",
        "src/feishu_ai_bot/cards",
        "src/feishu_ai_bot/security",
        "src/feishu_ai_bot/monitoring",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "configs",
        "scripts",
        "docs",
    ]
    
    print("\n📁 创建目录结构...")
    for dir_path in dirs_to_create:
        (root / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")
    
    print("\n✅ 目录结构创建完成!")
    print("\n📦 已创建的核心文件:")
    print("  - src/feishu_ai_bot/config.py (dataclass配置)")
    print("  - src/feishu_ai_bot/bot/feishu.py (飞书机器人)")
    print("  - src/feishu_ai_bot/openclaw/bridge.py (OpenClaw桥接)")
    print("  - tests/unit/test_config.py (配置测试)")
    print("  - tests/unit/test_openclaw_bridge.py (桥接器测试)")
    
    print("\n📝 下一步:")
    print("  1. 复制 deploy/ 中的代码到新位置")
    print("  2. 修改导入语句: from config import * → from feishu_ai_bot.config import load_config")
    print("  3. 修改配置访问: FEISHU_APP_ID → config.feishu.app_id")
    print("  4. 运行测试: make test")
    
    print("\n🎉 迁移准备完成!")


if __name__ == "__main__":
    main()
