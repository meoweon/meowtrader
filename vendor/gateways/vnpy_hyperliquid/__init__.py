"""
vnpy_hyperliquid - Hyperliquid 交易所网关

说明:
- 本模块作为 MeowTrader/VeighNa 的 Gateway 封装
- 具体实现位于同目录下的 hyperliquid/hyperliquid_gateway.py
- 依赖本仓库附带的 hyperliquid Python SDK（hyperliquid-python-sdk-master）
"""

from .hyperliquid.hyperliquid_gateway import HyperliquidGateway

__all__ = ["HyperliquidGateway"]

