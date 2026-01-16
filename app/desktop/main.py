"""
桌面入口 - 启动带 Fluent UI 的桌面交易客户端

用法:
    python -m meowtrader.app.desktop
    或
    python meowtrader/app/desktop/main.py
"""

import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    """启动桌面客户端"""
    # 导入 core 模块（这会自动配置 vendor 路径）
    from meowtrader.core import ProductEngine, ConfigManager, RuntimeManager
    from meowtrader.core.registry.editions import Edition
    
    print("=" * 60)
    print("MeowTrader Desktop 启动中...")
    print("=" * 60)
    
    # 1. 初始化运行时管理器
    runtime = RuntimeManager()
    
    # 检查环境
    env_check = runtime.check_environment()
    if not all(env_check.values()):
        print("Environment check failed:")
        for key, value in env_check.items():
            status = "[OK]" if value else "[FAIL]"
            print(f"  {status} {key}")
        sys.exit(1)
    
    # 设置数据目录和日志
    runtime.setup_data_directory()
    runtime.setup_logging(level="INFO")
    
    # 2. 加载配置（开发环境使用 ALL 版本，启用所有模块）
    config_manager = ConfigManager()
    config = config_manager.load(edition=Edition.ALL)
    
    product_info = config.get('product', {})
    print(f"产品: {product_info.get('name', 'MeowTrader')}")
    print(f"版本: {product_info.get('edition', 'pro')}")
    print("-" * 60)
    
    # 3. 创建 Qt 应用（必须在创建任何 Widget 之前）
    from vnpy.trader.ui import create_qapp
    qapp = create_qapp("MeowTrader")
    
    # 4. 创建并启动产品引擎（会加载 Gateway 和 App）
    engine = ProductEngine()
    engine.start(config)
    
    # 显示已加载的模块
    print("Loaded Gateways:")
    for gw in engine.loaded_gateways:
        print(f"  [OK] {gw}")
    
    print("-" * 60)
    print("Loaded Apps:")
    for app in engine.loaded_apps:
        print(f"  [OK] {app}")
    
    # 显示配置中但未加载的应用
    config_apps = config.get("apps", [])
    loaded_app_names = set(engine.loaded_apps)
    failed_apps = []
    for app_config in config_apps:
        app_name = app_config.get("name")
        if app_name and app_name not in loaded_app_names:
            failed_apps.append(app_name)
    
    if failed_apps:
        print("-" * 60)
        print("Failed to Load Apps:")
        for app in failed_apps:
            print(f"  [FAIL] {app}")
    print("-" * 60)
    
    # 5. 创建主窗口（使用 Fluent Design UI）
    from vnpy.trader.ui import FluentMainWindow
    main_window = FluentMainWindow(engine.main_engine, engine.event_engine)
    main_window.show()
    
    print("=" * 60)
    print("MeowTrader Desktop started successfully! (Fluent Design UI)")
    print("=" * 60)
    
    # 6. 运行事件循环
    exit_code = qapp.exec()
    
    # 7. 清理资源
    engine.shutdown()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
