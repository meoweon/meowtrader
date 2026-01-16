"""
ProductEngine - 产品层核心引擎

职责:
- 封装 vnpy MainEngine/EventEngine
- 按配置加载 Gateway/App/Database
- 统一生命周期管理（启动/关闭/资源释放）
- 提供稳定 API 给 UI 与服务层
"""

from typing import TYPE_CHECKING, Any
import logging

if TYPE_CHECKING:
    from vnpy.event import EventEngine
    from vnpy.trader.engine import MainEngine

logger = logging.getLogger(__name__)


# Gateway 名称到模块的映射
GATEWAY_MAP = {
    "okx": ("vnpy_okx", "OkxGateway"),
    "binance_spot": ("vnpy_binance", "BinanceSpotGateway"),
    "binance_linear": ("vnpy_binance", "BinanceLinearGateway"),
    "binance_inverse": ("vnpy_binance", "BinanceInverseGateway"),
}

# App 名称到模块的映射
APP_MAP = {
    "cta_strategy": ("vnpy_ctastrategy", "CtaStrategyApp"),
    "cta_backtester": ("vnpy_ctabacktester", "CtaBacktesterApp"),
    "data_manager": ("vnpy_datamanager", "DataManagerApp"),
    "risk_manager": ("vnpy_riskmanager", "RiskManagerApp"),
    "paper_account": ("vnpy_paperaccount", "PaperAccountApp"),
    "portfolio_strategy": ("vnpy_portfoliostrategy", "PortfolioStrategyApp"),
    "chart_wizard": ("vnpy_chartwizard", "ChartWizardApp"),
    "web_trader": ("vnpy_webtrader", "WebTraderApp"),
    "rpc_service": ("vnpy_rpcservice", "RpcServiceApp"),
    # 以下为可选应用
    "algotrading": ("vnpy_algotrading", "AlgoTradingApp"),
    "datarecorder": ("vnpy_datarecorder", "DataRecorderApp"),
    "excelrtd": ("vnpy_excelrtd", "ExcelRtdApp"),
    "optionmaster": ("vnpy_optionmaster", "OptionMasterApp"),
    "portfoliomanager": ("vnpy_portfoliomanager", "PortfolioManagerApp"),
    "scripttrader": ("vnpy_scripttrader", "ScriptTraderApp"),
    "spreadtrading": ("vnpy_spreadtrading", "SpreadTradingApp"),
}


class ProductEngine:
    """
    产品层核心引擎
    
    对外提供稳定 API，屏蔽 vnpy 内部变化
    """
    
    def __init__(self) -> None:
        self._event_engine: "EventEngine | None" = None
        self._main_engine: "MainEngine | None" = None
        self._initialized: bool = False
        self._loaded_gateways: list[str] = []
        self._loaded_apps: list[str] = []
    
    def start(self, config: dict | None = None) -> None:
        """
        启动产品引擎
        
        Args:
            config: 运行配置，如果为 None 则使用默认配置
        """
        if self._initialized:
            raise RuntimeError("ProductEngine already initialized")
        
        # 延迟导入（此时 vendor 路径已配置）
        from vnpy.event import EventEngine
        from vnpy.trader.engine import MainEngine
        
        # 创建事件引擎
        self._event_engine = EventEngine()
        
        # 创建主引擎
        self._main_engine = MainEngine(self._event_engine)
        
        # 按配置加载模块
        if config:
            self._load_modules(config)
        
        self._initialized = True
    
    def shutdown(self) -> None:
        """
        关闭产品引擎，释放资源
        """
        if not self._initialized:
            return
        
        if self._main_engine:
            self._main_engine.close()
            self._main_engine = None
        
        if self._event_engine:
            self._event_engine.stop()
            self._event_engine = None
        
        self._initialized = False
        self._loaded_gateways.clear()
        self._loaded_apps.clear()
    
    def _load_modules(self, config: dict) -> None:
        """
        按配置加载模块
        
        Args:
            config: 包含 gateways, apps, database 配置的字典
        """
        if not self._main_engine:
            raise RuntimeError("MainEngine not initialized")
        
        # 加载 Gateway
        gateways = config.get("gateways", [])
        logger.info(f"配置中的 Gateway 数量: {len(gateways)}")
        for gateway_config in gateways:
            self._load_gateway(gateway_config)
        
        # 加载 App
        apps = config.get("apps", [])
        logger.info(f"配置中的 App 数量: {len(apps)}")
        enabled_apps = [a for a in apps if a.get("enabled", True)]
        logger.info(f"启用的 App 数量: {len(enabled_apps)}")
        for app_config in apps:
            self._load_app(app_config)
    
    def _load_gateway(self, gateway_config: dict) -> None:
        """加载单个 Gateway"""
        name = gateway_config.get("name")
        enabled = gateway_config.get("enabled", True)
        
        if not enabled or not name:
            return
        
        if name not in GATEWAY_MAP:
            logger.warning(f"Unknown gateway: {name}")
            return
        
        module_name, class_name = GATEWAY_MAP[name]
        
        try:
            gateway_class = self._import_class(module_name, class_name)
            self._main_engine.add_gateway(gateway_class)
            self._loaded_gateways.append(name)
            logger.info(f"Loaded gateway: {name}")
        except Exception as e:
            logger.error(f"Failed to load gateway {name}: {e}")
    
    def _load_app(self, app_config: dict) -> None:
        """加载单个 App"""
        name = app_config.get("name")
        enabled = app_config.get("enabled", True)
        
        if not enabled or not name:
            if not enabled:
                logger.debug(f"App {name} is disabled, skipping")
            return
        
        if name not in APP_MAP:
            logger.warning(f"Unknown app: {name}")
            print(f"  [WARN] {name} - 未知应用（不在 APP_MAP 中）")
            return
        
        module_name, class_name = APP_MAP[name]
        
        try:
            app_class = self._import_class(module_name, class_name)
            self._main_engine.add_app(app_class)
            self._loaded_apps.append(name)
            logger.info(f"Loaded app: {name}")
            print(f"  [OK] {name}")
        except ImportError as e:
            import traceback
            logger.error(f"Failed to load app {name}: {e}")
            logger.debug(traceback.format_exc())
            print(f"  [FAIL] {name} - 导入失败: {e}")
            print(f"         模块: {module_name}.{class_name}")
        except Exception as e:
            import traceback
            logger.error(f"Failed to load app {name}: {e}")
            logger.debug(traceback.format_exc())
            print(f"  [FAIL] {name} - 加载失败: {e}")
            print(f"         模块: {module_name}.{class_name}")
            print(f"         详细错误: {traceback.format_exc()}")
    
    def _import_class(self, module_name: str, class_name: str) -> Any:
        """动态导入类"""
        import importlib
        import traceback
        try:
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except ImportError as e:
            # 提供更详细的错误信息
            import sys
            error_detail = traceback.format_exc()
            logger.error(f"Import error for {module_name}: {e}")
            logger.debug(f"Python path: {sys.path[:5]}")  # 只显示前5个路径
            logger.debug(error_detail)
            raise
        except Exception as e:
            # 捕获其他可能的异常
            error_detail = traceback.format_exc()
            logger.error(f"Unexpected error importing {module_name}: {e}")
            logger.debug(error_detail)
            raise
    
    @property
    def event_engine(self) -> "EventEngine":
        """获取事件引擎"""
        if not self._event_engine:
            raise RuntimeError("EventEngine not initialized")
        return self._event_engine
    
    @property
    def main_engine(self) -> "MainEngine":
        """获取主引擎（仅供内部扩展使用）"""
        if not self._main_engine:
            raise RuntimeError("MainEngine not initialized")
        return self._main_engine
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._initialized
    
    @property
    def loaded_gateways(self) -> list[str]:
        """已加载的 Gateway 列表"""
        return self._loaded_gateways.copy()
    
    @property
    def loaded_apps(self) -> list[str]:
        """已加载的 App 列表"""
        return self._loaded_apps.copy()
