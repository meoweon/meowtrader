"""
ModuleRegistry - 模块注册与版本矩阵管理

职责:
- 维护 Gateway/App/DB/工具模块清单
- 维护版本矩阵映射
- 提供模块依赖校验
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ModuleType(Enum):
    """模块类型"""
    GATEWAY = "gateway"
    APP = "app"
    DATABASE = "database"
    LIBRARY = "library"


class GatewayCategory(Enum):
    """Gateway 分类"""
    CRYPTO = "crypto"           # 加密货币
    CN_FUTURES = "cn_futures"   # 国内期货
    CN_STOCK = "cn_stock"       # 国内股票/期权
    CN_GOLD = "cn_gold"         # 国内贵金属
    GLOBAL = "global"           # 国际/外盘
    DATAFEED = "datafeed"       # 数据服务
    SPECIAL = "special"         # 特殊接口


# Gateway 分类显示名称
GATEWAY_CATEGORY_NAMES = {
    GatewayCategory.CRYPTO: "加密货币交易所",
    GatewayCategory.CN_FUTURES: "国内期货",
    GatewayCategory.CN_STOCK: "国内股票/期权",
    GatewayCategory.CN_GOLD: "国内贵金属",
    GatewayCategory.GLOBAL: "国际/外盘",
    GatewayCategory.DATAFEED: "数据服务",
    GatewayCategory.SPECIAL: "特殊接口",
}


@dataclass
class ModuleInfo:
    """模块信息"""
    name: str
    module_type: ModuleType
    class_path: str  # 模块类的导入路径
    display_name: str  # 显示名称
    description: str = ""
    dependencies: list[str] | None = None  # 依赖的其他模块名
    category: str = ""  # Gateway 分类


class ModuleRegistry:
    """
    模块注册表
    
    管理所有可用的 Gateway、App、Database 模块
    """
    
    def __init__(self) -> None:
        self._modules: dict[str, ModuleInfo] = {}
        self._register_builtin_modules()
    
    def _register_builtin_modules(self) -> None:
        """注册内置模块"""
        # ============================================================
        # Gateway 模块 - 加密货币
        # ============================================================
        self.register(ModuleInfo(
            name="okx",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_okx.OkxGateway",
            display_name="OKX",
            description="OKX 交易所（现货、合约、期权）",
            category="crypto"
        ))
        self.register(ModuleInfo(
            name="binance_spot",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_binance.BinanceSpotGateway",
            display_name="Binance 现货",
            description="Binance 现货交易",
            category="crypto"
        ))
        self.register(ModuleInfo(
            name="binance_linear",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_binance.BinanceLinearGateway",
            display_name="Binance U本位",
            description="Binance U本位永续/交割合约",
            category="crypto"
        ))
        self.register(ModuleInfo(
            name="binance_inverse",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_binance.BinanceInverseGateway",
            display_name="Binance 币本位",
            description="Binance 币本位永续/交割合约",
            category="crypto"
        ))
        
        # ============================================================
        # Gateway 模块 - 国内期货
        # ============================================================
        self.register(ModuleInfo(
            name="ctp",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_ctp.CtpGateway",
            display_name="CTP",
            description="上期技术 CTP 期货接口",
            category="cn_futures"
        ))
        self.register(ModuleInfo(
            name="ctp_test",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_ctptest.CtptestGateway",
            display_name="CTP测试",
            description="CTP 测试环境",
            category="cn_futures"
        ))
        self.register(ModuleInfo(
            name="mini",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_mini.MiniGateway",
            display_name="CTP Mini",
            description="CTP Mini 轻量接口",
            category="cn_futures"
        ))
        self.register(ModuleInfo(
            name="femas",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_femas.FemasGateway",
            display_name="飞马",
            description="飞马期货接口",
            category="cn_futures"
        ))
        self.register(ModuleInfo(
            name="uft",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_uft.UftGateway",
            display_name="恒生UFT",
            description="恒生 UFT 期货接口",
            category="cn_futures"
        ))
        self.register(ModuleInfo(
            name="esunny",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_esunny.EsunnyGateway",
            display_name="易盛",
            description="易盛期货接口",
            category="cn_futures"
        ))
        self.register(ModuleInfo(
            name="tts",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_tts.TtsGateway",
            display_name="TTS仿真",
            description="TTS 期货仿真",
            category="cn_futures"
        ))
        self.register(ModuleInfo(
            name="rohon",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_rohon.RohonGateway",
            display_name="融航",
            description="融航期货资管",
            category="cn_futures"
        ))
        self.register(ModuleInfo(
            name="jees",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_jees.JeesGateway",
            display_name="杰宜斯",
            description="杰宜斯期货资管",
            category="cn_futures"
        ))
        # 注意：vnpy_tora 只提供 ToraStockGateway 和 ToraOptionGateway，没有 ToraFuturesGateway
        
        # ============================================================
        # Gateway 模块 - 国内股票/期权
        # ============================================================
        self.register(ModuleInfo(
            name="xtp",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_xtp.XtpGateway",
            display_name="中泰XTP",
            description="中泰证券 XTP 接口",
            category="cn_stock"
        ))
        self.register(ModuleInfo(
            name="tora_stock",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_tora.ToraStockGateway",
            display_name="华鑫股票",
            description="华鑫奇点股票",
            category="cn_stock"
        ))
        self.register(ModuleInfo(
            name="tora_option",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_tora.ToraOptionGateway",
            display_name="华鑫期权",
            description="华鑫奇点 ETF 期权",
            category="cn_stock"
        ))
        self.register(ModuleInfo(
            name="sopt",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_sopt.SoptGateway",
            display_name="CTP期权",
            description="CTP ETF 期权接口",
            category="cn_stock"
        ))
        self.register(ModuleInfo(
            name="sec",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_sec.SecGateway",
            display_name="顶点飞创",
            description="顶点飞创 ETF 期权",
            category="cn_stock"
        ))
        self.register(ModuleInfo(
            name="hts",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_hts.HtsGateway",
            display_name="顶点HTS",
            description="顶点 HTS ETF 期权",
            category="cn_stock"
        ))
        
        # ============================================================
        # Gateway 模块 - 国内贵金属
        # ============================================================
        self.register(ModuleInfo(
            name="ksgold",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_ksgold.KsgoldGateway",
            display_name="金仕达黄金",
            description="金仕达黄金 TD",
            category="cn_gold"
        ))
        
        # ============================================================
        # Gateway 模块 - 国际/外盘
        # ============================================================
        self.register(ModuleInfo(
            name="ib",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_ib.IbGateway",
            display_name="盈透证券",
            description="Interactive Brokers 全球市场",
            category="global"
        ))
        self.register(ModuleInfo(
            name="tap",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_tap.TapGateway",
            display_name="易盛外盘",
            description="易盛 9.0 外盘期货",
            category="global"
        ))
        self.register(ModuleInfo(
            name="da",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_da.DaGateway",
            display_name="直达期货",
            description="直达外盘期货",
            category="global"
        ))
        
        # ============================================================
        # Gateway 模块 - 数据服务
        # ============================================================
        # 注意：tqsdk 是 Datafeed，不是 Gateway，应该通过 datafeed.name 配置使用
        self.register(ModuleInfo(
            name="xt",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_xt.XtGateway",
            display_name="迅投研",
            description="迅投研数据服务",
            category="datafeed"
        ))
        
        # ============================================================
        # Gateway 模块 - 特殊接口
        # ============================================================
        self.register(ModuleInfo(
            name="rpc",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_rpcservice.rpc_gateway.RpcGateway",
            display_name="RPC服务",
            description="RPC 远程接口",
            category="special"
        ))
        
        # ============================================================
        # App 模块
        # ============================================================
        self.register(ModuleInfo(
            name="cta_strategy",
            module_type=ModuleType.APP,
            class_path="vnpy_ctastrategy.CtaStrategyApp",
            display_name="CTA策略",
            description="CTA自动交易模块"
        ))
        
        self.register(ModuleInfo(
            name="cta_backtester",
            module_type=ModuleType.APP,
            class_path="vnpy_ctabacktester.CtaBacktesterApp",
            display_name="CTA回测",
            description="CTA策略回测研究模块",
            dependencies=["cta_strategy"]
        ))
        
        self.register(ModuleInfo(
            name="data_manager",
            module_type=ModuleType.APP,
            class_path="vnpy_datamanager.DataManagerApp",
            display_name="数据管理",
            description="历史数据管理模块"
        ))
        
        self.register(ModuleInfo(
            name="risk_manager",
            module_type=ModuleType.APP,
            class_path="vnpy_riskmanager.RiskManagerApp",
            display_name="风险管理",
            description="事前风险管理模块"
        ))
        
        self.register(ModuleInfo(
            name="paper_account",
            module_type=ModuleType.APP,
            class_path="vnpy_paperaccount.PaperAccountApp",
            display_name="模拟账户",
            description="本地仿真交易模块"
        ))
        
        self.register(ModuleInfo(
            name="portfolio_strategy",
            module_type=ModuleType.APP,
            class_path="vnpy_portfoliostrategy.PortfolioStrategyApp",
            display_name="组合策略",
            description="多合约组合策略模块"
        ))
        
        self.register(ModuleInfo(
            name="chart_wizard",
            module_type=ModuleType.APP,
            class_path="vnpy_chartwizard.ChartWizardApp",
            display_name="图表工具",
            description="实时K线图表模块"
        ))
        
        self.register(ModuleInfo(
            name="web_trader",
            module_type=ModuleType.APP,
            class_path="vnpy_webtrader.WebTraderApp",
            display_name="Web交易",
            description="Web服务器模块"
        ))
        
        self.register(ModuleInfo(
            name="rpc_service",
            module_type=ModuleType.APP,
            class_path="vnpy_rpcservice.RpcServiceApp",
            display_name="RPC服务",
            description="RPC服务器模块"
        ))
        
        # ============================================================
        # Database 模块
        # ============================================================
        self.register(ModuleInfo(
            name="sqlite",
            module_type=ModuleType.DATABASE,
            class_path="vnpy_sqlite.Database",
            display_name="SQLite",
            description="SQLite 轻量级数据库"
        ))
        
        self.register(ModuleInfo(
            name="postgresql",
            module_type=ModuleType.DATABASE,
            class_path="vnpy_postgresql.Database",
            display_name="PostgreSQL",
            description="PostgreSQL 数据库"
        ))
    
    def register(self, module_info: ModuleInfo) -> None:
        """注册模块"""
        self._modules[module_info.name] = module_info
    
    def get(self, name: str) -> ModuleInfo | None:
        """获取模块信息"""
        return self._modules.get(name)
    
    def get_by_type(self, module_type: ModuleType) -> list[ModuleInfo]:
        """按类型获取模块列表"""
        return [m for m in self._modules.values() if m.module_type == module_type]
    
    def get_gateways_by_category(self) -> dict[str, list[ModuleInfo]]:
        """按分类获取 Gateway 列表"""
        gateways = self.get_by_type(ModuleType.GATEWAY)
        result: dict[str, list[ModuleInfo]] = {}
        for gw in gateways:
            category = gw.category or "other"
            if category not in result:
                result[category] = []
            result[category].append(gw)
        return result
    
    def get_all(self) -> list[ModuleInfo]:
        """获取所有模块"""
        return list(self._modules.values())
    
    def load_module_class(self, name: str) -> Any:
        """
        动态加载模块类
        
        Args:
            name: 模块名称
            
        Returns:
            模块类
        """
        module_info = self.get(name)
        if not module_info:
            raise ValueError(f"Unknown module: {name}")
        
        # 动态导入
        import importlib
        
        parts = module_info.class_path.rsplit(".", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid class path: {module_info.class_path}")
        
        module_path, class_name = parts
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
