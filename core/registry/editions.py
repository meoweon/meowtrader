"""
EditionManager - 版本矩阵管理

职责:
- 定义版本（精简版/专业版/定制版）
- 管理版本与模块的映射关系
"""

from dataclasses import dataclass
from enum import Enum


class Edition(Enum):
    """产品版本"""
    BASIC = "basic"       # 精简版 - 分发给普通用户
    PRO = "pro"           # 专业版 - 分发给专业用户
    CUSTOM = "custom"     # 客户定制版 - 按需配置
    ALL = "all"           # 开发版 - 启用所有模块（本地开发/build.py 使用）


@dataclass
class ModuleAvailability:
    """模块可用性配置"""
    required: bool = False   # 是否必选
    enabled: bool = True     # 是否默认启用
    visible: bool = True     # 是否在 UI 中可见


# 版本矩阵定义
EDITION_MATRIX: dict[Edition, dict[str, ModuleAvailability]] = {
    # ================================================================
    # 精简版 - 基础交易功能
    # ================================================================
    Edition.BASIC: {
        # Gateway
        "okx": ModuleAvailability(enabled=True),
        "binance_spot": ModuleAvailability(enabled=True),
        "binance_linear": ModuleAvailability(enabled=True),
        "binance_inverse": ModuleAvailability(enabled=True),
        
        # App - 核心功能
        "cta_strategy": ModuleAvailability(required=True, enabled=True),
        "risk_manager": ModuleAvailability(enabled=True),
        "paper_account": ModuleAvailability(enabled=True),
        
        # App - 禁用功能
        "cta_backtester": ModuleAvailability(enabled=False, visible=False),
        "data_manager": ModuleAvailability(enabled=False, visible=False),
        "portfolio_strategy": ModuleAvailability(enabled=False, visible=False),
        "chart_wizard": ModuleAvailability(enabled=False, visible=False),
        "web_trader": ModuleAvailability(enabled=False, visible=False),
        "rpc_service": ModuleAvailability(enabled=False, visible=False),
        
        # Database
        "sqlite": ModuleAvailability(required=True, enabled=True),
        "postgresql": ModuleAvailability(enabled=False, visible=False),
    },
    
    # ================================================================
    # 专业版 - 完整功能
    # ================================================================
    Edition.PRO: {
        # Gateway
        "okx": ModuleAvailability(enabled=True),
        "binance_spot": ModuleAvailability(enabled=True),
        "binance_linear": ModuleAvailability(enabled=True),
        "binance_inverse": ModuleAvailability(enabled=True),
        
        # App - 全部启用
        "cta_strategy": ModuleAvailability(required=True, enabled=True),
        "cta_backtester": ModuleAvailability(enabled=True),
        "data_manager": ModuleAvailability(enabled=True),
        "risk_manager": ModuleAvailability(enabled=True),
        "paper_account": ModuleAvailability(enabled=True),
        "portfolio_strategy": ModuleAvailability(enabled=True),
        "chart_wizard": ModuleAvailability(enabled=True),
        "web_trader": ModuleAvailability(enabled=True),
        "rpc_service": ModuleAvailability(enabled=True),
        
        # Database
        "sqlite": ModuleAvailability(enabled=True),
        "postgresql": ModuleAvailability(enabled=True),
    },
    
    # ================================================================
    # 定制版 - 按需配置（默认同专业版）
    # ================================================================
    Edition.CUSTOM: {
        # 默认同专业版，通过配置文件覆盖
        "okx": ModuleAvailability(enabled=True),
        "binance_spot": ModuleAvailability(enabled=True),
        "binance_linear": ModuleAvailability(enabled=True),
        "binance_inverse": ModuleAvailability(enabled=True),
        "cta_strategy": ModuleAvailability(required=True, enabled=True),
        "cta_backtester": ModuleAvailability(enabled=True),
        "data_manager": ModuleAvailability(enabled=True),
        "risk_manager": ModuleAvailability(enabled=True),
        "paper_account": ModuleAvailability(enabled=True),
        "portfolio_strategy": ModuleAvailability(enabled=True),
        "chart_wizard": ModuleAvailability(enabled=True),
        "web_trader": ModuleAvailability(enabled=True),
        "rpc_service": ModuleAvailability(enabled=True),
        "sqlite": ModuleAvailability(enabled=True),
        "postgresql": ModuleAvailability(enabled=True),
    },
    
    # ================================================================
    # 开发版 - 启用所有模块（本地开发 + build.py 使用）
    # ================================================================
    Edition.ALL: {
        # Gateway - 加密货币
        "okx": ModuleAvailability(enabled=True),
        "binance_spot": ModuleAvailability(enabled=True),
        "binance_linear": ModuleAvailability(enabled=True),
        "binance_inverse": ModuleAvailability(enabled=True),
        # Gateway - 国内期货
        "ctp": ModuleAvailability(enabled=True),
        "ctp_test": ModuleAvailability(enabled=True),
        "mini": ModuleAvailability(enabled=True),
        "femas": ModuleAvailability(enabled=True),
        "uft": ModuleAvailability(enabled=True),
        "esunny": ModuleAvailability(enabled=True),
        "tts": ModuleAvailability(enabled=True),
        "rohon": ModuleAvailability(enabled=True),
        "jees": ModuleAvailability(enabled=True),
        "tora_futures": ModuleAvailability(enabled=True),
        # Gateway - 国内股票/期权
        "xtp": ModuleAvailability(enabled=True),
        "tora_stock": ModuleAvailability(enabled=True),
        "tora_option": ModuleAvailability(enabled=True),
        "sopt": ModuleAvailability(enabled=True),
        "sec": ModuleAvailability(enabled=True),
        "hts": ModuleAvailability(enabled=True),
        # Gateway - 贵金属
        "ksgold": ModuleAvailability(enabled=True),
        # Gateway - 外盘/国际
        "ib": ModuleAvailability(enabled=True),
        "tap": ModuleAvailability(enabled=True),
        "da": ModuleAvailability(enabled=True),
        # Gateway - 数据服务
        "tqsdk": ModuleAvailability(enabled=True),
        "xt": ModuleAvailability(enabled=True),
        # Gateway - 特殊接口
        "rpc": ModuleAvailability(enabled=True),
        # App - 全部启用
        "cta_strategy": ModuleAvailability(required=True, enabled=True),
        "cta_backtester": ModuleAvailability(enabled=True),
        "data_manager": ModuleAvailability(enabled=True),
        "risk_manager": ModuleAvailability(enabled=True),
        "paper_account": ModuleAvailability(enabled=True),
        "portfolio_strategy": ModuleAvailability(enabled=True),
        "chart_wizard": ModuleAvailability(enabled=True),
        "web_trader": ModuleAvailability(enabled=True),
        "rpc_service": ModuleAvailability(enabled=True),
        "algotrading": ModuleAvailability(enabled=True),
        "datarecorder": ModuleAvailability(enabled=True),
        "excelrtd": ModuleAvailability(enabled=True),
        "optionmaster": ModuleAvailability(enabled=True),
        "portfoliomanager": ModuleAvailability(enabled=True),
        "scripttrader": ModuleAvailability(enabled=True),
        "spreadtrading": ModuleAvailability(enabled=True),
        # Database
        "sqlite": ModuleAvailability(enabled=True),
        "postgresql": ModuleAvailability(enabled=True),
    },
}


class EditionManager:
    """
    版本管理器
    
    根据版本配置返回可用的模块列表
    """
    
    def __init__(self, edition: Edition = Edition.PRO) -> None:
        self.edition = edition
    
    def get_available_modules(self) -> dict[str, ModuleAvailability]:
        """获取当前版本可用的模块配置"""
        return EDITION_MATRIX.get(self.edition, {})
    
    def is_module_enabled(self, module_name: str) -> bool:
        """检查模块是否启用"""
        matrix = self.get_available_modules()
        availability = matrix.get(module_name)
        return availability.enabled if availability else False
    
    def is_module_visible(self, module_name: str) -> bool:
        """检查模块是否在 UI 中可见"""
        matrix = self.get_available_modules()
        availability = matrix.get(module_name)
        return availability.visible if availability else False
    
    def get_enabled_modules(self) -> list[str]:
        """获取所有启用的模块名称"""
        matrix = self.get_available_modules()
        return [name for name, avail in matrix.items() if avail.enabled]
    
    def get_visible_modules(self) -> list[str]:
        """获取所有可见的模块名称"""
        matrix = self.get_available_modules()
        return [name for name, avail in matrix.items() if avail.visible]
