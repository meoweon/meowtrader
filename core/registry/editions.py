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
    BASIC = "basic"       # 精简版
    PRO = "pro"           # 专业版
    CUSTOM = "custom"     # 客户定制版


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
