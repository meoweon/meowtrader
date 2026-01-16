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


@dataclass
class ModuleInfo:
    """模块信息"""
    name: str
    module_type: ModuleType
    class_path: str  # 模块类的导入路径
    display_name: str  # 显示名称
    description: str = ""
    dependencies: list[str] | None = None  # 依赖的其他模块名


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
        # Gateway 模块
        # ============================================================
        self.register(ModuleInfo(
            name="okx",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_okx.OkxGateway",
            display_name="OKX",
            description="OKX 交易所接口（现货、合约、期权）"
        ))
        
        self.register(ModuleInfo(
            name="binance_spot",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_binance.BinanceSpotGateway",
            display_name="Binance 现货",
            description="Binance 现货交易接口"
        ))
        
        self.register(ModuleInfo(
            name="binance_linear",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_binance.BinanceLinearGateway",
            display_name="Binance U本位合约",
            description="Binance U本位永续/交割合约接口"
        ))
        
        self.register(ModuleInfo(
            name="binance_inverse",
            module_type=ModuleType.GATEWAY,
            class_path="vnpy_binance.BinanceInverseGateway",
            display_name="Binance 币本位合约",
            description="Binance 币本位永续/交割合约接口"
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
