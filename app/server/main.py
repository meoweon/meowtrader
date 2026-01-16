"""
服务端入口 - 无 UI 模式，运行策略和服务

用法:
    python -m meowtrader.app.server
    或
    python meowtrader/app/server/main.py
"""

import sys
import signal
from pathlib import Path

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    """启动服务端"""
    from meowtrader.core import ProductEngine, ConfigManager, RuntimeManager
    from meowtrader.core.registry.editions import Edition
    
    print("=" * 60)
    print("MeowTrader Server 启动中...")
    print("=" * 60)
    
    # 1. 初始化运行时管理器
    runtime = RuntimeManager()
    runtime.setup_data_directory()
    runtime.setup_logging(level="INFO")
    
    # 2. 加载配置
    config_manager = ConfigManager()
    config = config_manager.load(edition=Edition.PRO)
    
    # 3. 创建并启动产品引擎
    engine = ProductEngine()
    engine.start(config)
    
    print("服务端启动成功，按 Ctrl+C 退出")
    print("=" * 60)
    
    # 4. 设置信号处理
    def signal_handler(sig, frame):
        print("\n正在关闭服务端...")
        engine.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 5. 保持运行
    try:
        while engine.is_running:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        engine.shutdown()


if __name__ == "__main__":
    main()
