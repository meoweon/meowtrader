"""
Web 入口 - 启动 WebTrader 服务

用法:
    python -m meowtrader.app.web
    或
    python meowtrader/app/web/main.py
"""

import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    """启动 Web 服务"""
    from meowtrader.core import ProductEngine, ConfigManager, RuntimeManager
    from meowtrader.core.registry.editions import Edition
    
    print("=" * 60)
    print("MeowTrader Web 启动中...")
    print("=" * 60)
    
    # 1. 初始化运行时管理器
    runtime = RuntimeManager()
    runtime.setup_data_directory()
    runtime.setup_logging(level="INFO")
    
    # 2. 加载配置（只启用 web_trader）
    config_manager = ConfigManager()
    config = config_manager.load(edition=Edition.PRO)
    
    # 3. 创建并启动产品引擎
    engine = ProductEngine()
    engine.start(config)
    
    # 4. 启动 WebTrader
    # TODO: 获取 WebTrader App 并启动
    
    print("WebTrader 服务启动成功")
    print("访问地址: http://localhost:8000")
    print("=" * 60)
    
    # 5. 保持运行
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭 Web 服务...")
        engine.shutdown()


if __name__ == "__main__":
    main()
