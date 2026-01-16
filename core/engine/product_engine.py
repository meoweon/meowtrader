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
# 格式: "name": ("module_name", "ClassName", "display_name", "category", "description")
GATEWAY_MAP = {
    # ==================== 加密货币交易所 ====================
    "okx": ("vnpy_okx", "OkxGateway", "OKX", "crypto", "OKX 交易所（现货、合约、期权）"),
    "binance_spot": ("vnpy_binance", "BinanceSpotGateway", "Binance 现货", "crypto", "Binance 现货交易"),
    "binance_linear": ("vnpy_binance", "BinanceLinearGateway", "Binance U本位", "crypto", "Binance U本位永续/交割合约"),
    "binance_inverse": ("vnpy_binance", "BinanceInverseGateway", "Binance 币本位", "crypto", "Binance 币本位永续/交割合约"),
    
    # ==================== 国内期货 ====================
    "ctp": ("vnpy_ctp", "CtpGateway", "CTP", "cn_futures", "上期技术 CTP 期货接口"),
    "ctp_test": ("vnpy_ctptest", "CtptestGateway", "CTP测试", "cn_futures", "CTP 测试环境"),
    "mini": ("vnpy_mini", "MiniGateway", "CTP Mini", "cn_futures", "CTP Mini 轻量接口"),
    "femas": ("vnpy_femas", "FemasGateway", "飞马", "cn_futures", "飞马期货接口"),
    "uft": ("vnpy_uft", "UftGateway", "恒生UFT", "cn_futures", "恒生 UFT 期货接口"),
    "esunny": ("vnpy_esunny", "EsunnyGateway", "易盛", "cn_futures", "易盛期货接口"),
    "tts": ("vnpy_tts", "TtsGateway", "TTS仿真", "cn_futures", "TTS 期货仿真"),
    "rohon": ("vnpy_rohon", "RohonGateway", "融航", "cn_futures", "融航期货资管"),
    "jees": ("vnpy_jees", "JeesGateway", "杰宜斯", "cn_futures", "杰宜斯期货资管"),
    "tora_futures": ("vnpy_tora", "ToraFuturesGateway", "华鑫期货", "cn_futures", "华鑫奇点期货"),
    
    # ==================== 国内股票/ETF期权 ====================
    "xtp": ("vnpy_xtp", "XtpGateway", "中泰XTP", "cn_stock", "中泰证券 XTP 接口"),
    "tora_stock": ("vnpy_tora", "ToraStockGateway", "华鑫股票", "cn_stock", "华鑫奇点股票"),
    "tora_option": ("vnpy_tora", "ToraOptionGateway", "华鑫期权", "cn_stock", "华鑫奇点 ETF 期权"),
    "sopt": ("vnpy_sopt", "SoptGateway", "CTP期权", "cn_stock", "CTP ETF 期权接口"),
    "sec": ("vnpy_sec", "SecGateway", "顶点飞创", "cn_stock", "顶点飞创 ETF 期权"),
    "hts": ("vnpy_hts", "HtsGateway", "顶点HTS", "cn_stock", "顶点 HTS ETF 期权"),
    
    # ==================== 国内贵金属 ====================
    "ksgold": ("vnpy_ksgold", "KsgoldGateway", "金仕达黄金", "cn_gold", "金仕达黄金 TD"),
    
    # ==================== 外盘/国际 ====================
    "ib": ("vnpy_ib", "IbGateway", "盈透证券", "global", "Interactive Brokers 全球市场"),
    "tap": ("vnpy_tap", "TapGateway", "易盛外盘", "global", "易盛 9.0 外盘期货"),
    "da": ("vnpy_da", "DaGateway", "直达期货", "global", "直达外盘期货"),
    
    # ==================== 数据服务 ====================
    # 注意：tqsdk 是 Datafeed，不是 Gateway，应该通过 datafeed.name 配置使用
    "xt": ("vnpy_xt", "XtGateway", "迅投研", "datafeed", "迅投研数据服务"),
    
    # ==================== 特殊接口 ====================
    "rpc": ("vnpy_rpcservice.rpc_gateway", "RpcGateway", "RPC服务", "special", "RPC 远程接口"),
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
        
        # 加载 Gateway（配置中有就加载）
        gateways = config.get("gateways", [])
        logger.info(f"配置中的 Gateway 数量: {len(gateways)}")
        for gateway_config in gateways:
            self._load_gateway(gateway_config)
        
        # 加载 App（配置中有就加载）
        apps = config.get("apps", [])
        logger.info(f"配置中的 App 数量: {len(apps)}")
        for app_config in apps:
            self._load_app(app_config)
    
    def _load_gateway(self, gateway_config: dict) -> None:
        """加载单个 Gateway"""
        name = gateway_config.get("name")
        
        if not name:
            return
        
        if name not in GATEWAY_MAP:
            logger.warning(f"Unknown gateway: {name}")
            return
        
        gateway_info = GATEWAY_MAP[name]
        module_name = gateway_info[0]
        class_name = gateway_info[1]
        display_name = gateway_info[2] if len(gateway_info) > 2 else name
        
        try:
            gateway_class = self._import_class(module_name, class_name)
            self._main_engine.add_gateway(gateway_class)
            self._loaded_gateways.append(name)
            logger.info(f"Loaded gateway: {display_name} ({name})")
        except Exception as e:
            logger.error(f"Failed to load gateway {display_name}: {e}")
    
    def _load_app(self, app_config: dict) -> None:
        """加载单个 App"""
        name = app_config.get("name")
        
        if not name:
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
