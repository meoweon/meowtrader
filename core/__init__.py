"""
产品层 - 统一引擎封装、模块注册、配置管理、授权控制
"""

from .engine.product_engine import ProductEngine
from .registry.modules import ModuleRegistry
from .config.loader import ConfigManager
from .runtime.bootstrap import RuntimeManager

__all__ = [
    "ProductEngine",
    "ModuleRegistry", 
    "ConfigManager",
    "RuntimeManager",
]
