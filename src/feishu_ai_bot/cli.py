"""CLI入口模块

提供命令行接口
"""

import logging
import sys

from feishu_ai_bot.config import load_config, validate_config
from feishu_ai_bot.server import app

logger = logging.getLogger(__name__)


def main():
    """CLI主函数"""
    config = load_config()
    
    # 验证配置
    is_valid, errors = validate_config(config)
    if not is_valid:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print(f"🚀 启动飞书AI机器人 v{config.version}")
    print(f"📡 服务地址: http://{config.server.host}:{config.server.port}")
    
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug
    )


if __name__ == "__main__":
    main()
