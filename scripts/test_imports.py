"""
Test script - verify vendor modules can be imported correctly
"""

import sys
from pathlib import Path

# Ensure project root is in Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test all module imports"""
    print("=" * 60)
    print("MeowTrader Module Import Test")
    print("=" * 60)
    
    # Import core module first (configures vendor path)
    print("\n1. Import core module...")
    try:
        from meowtrader.core import ProductEngine, ConfigManager, RuntimeManager
        print("   [OK] meowtrader.core")
    except Exception as e:
        print(f"   [FAIL] meowtrader.core: {e}")
        return False
    
    # Test vnpy core
    print("\n2. Test vnpy core modules...")
    vnpy_modules = [
        ("vnpy.event", "EventEngine"),
        ("vnpy.trader.engine", "MainEngine"),
        ("vnpy.trader.object", "TickData"),
        ("vnpy.trader.constant", "Exchange"),
    ]
    
    for module_name, class_name in vnpy_modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   [OK] {module_name}.{class_name}")
        except Exception as e:
            print(f"   [FAIL] {module_name}.{class_name}: {e}")
    
    # Test Gateway
    print("\n3. Test Gateway modules...")
    gateway_modules = [
        ("vnpy_okx", "OkxGateway"),
        ("vnpy_binance", "BinanceSpotGateway"),
        ("vnpy_binance", "BinanceLinearGateway"),
        ("vnpy_binance", "BinanceInverseGateway"),
    ]
    
    for module_name, class_name in gateway_modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   [OK] {module_name}.{class_name}")
        except Exception as e:
            print(f"   [FAIL] {module_name}.{class_name}: {e}")
    
    # Test App
    print("\n4. Test App modules...")
    app_modules = [
        ("vnpy_ctastrategy", "CtaStrategyApp"),
        ("vnpy_ctabacktester", "CtaBacktesterApp"),
        ("vnpy_datamanager", "DataManagerApp"),
        ("vnpy_riskmanager", "RiskManagerApp"),
        ("vnpy_paperaccount", "PaperAccountApp"),
        ("vnpy_portfoliostrategy", "PortfolioStrategyApp"),
        ("vnpy_chartwizard", "ChartWizardApp"),
        ("vnpy_webtrader", "WebTraderApp"),
        ("vnpy_rpcservice", "RpcServiceApp"),
    ]
    
    for module_name, class_name in app_modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   [OK] {module_name}.{class_name}")
        except Exception as e:
            print(f"   [FAIL] {module_name}.{class_name}: {e}")
    
    # Test Database
    print("\n5. Test Database modules...")
    db_modules = [
        ("vnpy_sqlite", "Database"),
    ]
    
    for module_name, class_name in db_modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   [OK] {module_name}.{class_name}")
        except Exception as e:
            print(f"   [FAIL] {module_name}.{class_name}: {e}")
    
    # Test libs
    print("\n6. Test lib modules...")
    lib_modules = [
        ("vnpy_rest", "RestClient"),
        ("vnpy_websocket", "WebsocketClient"),
    ]
    
    for module_name, class_name in lib_modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   [OK] {module_name}.{class_name}")
        except Exception as e:
            print(f"   [FAIL] {module_name}.{class_name}: {e}")
    
    print("\n" + "=" * 60)
    print("Import test completed")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    test_imports()
