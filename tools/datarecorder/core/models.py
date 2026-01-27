"""
数据模型定义
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Exchange(Enum):
    """交易所枚举"""
    # 国内期货
    SHFE = "SHFE"      # 上海期货交易所
    DCE = "DCE"        # 大连商品交易所
    CZCE = "CZCE"      # 郑州商品交易所
    CFFEX = "CFFEX"    # 中国金融期货交易所
    INE = "INE"        # 上海国际能源交易中心
    
    # 国内股票
    SSE = "SSE"        # 上海证券交易所
    SZSE = "SZSE"      # 深圳证券交易所
    
    # 加密货币
    BINANCE = "BINANCE"
    OKX = "OKX"
    HYPERLIQUID = "HYPERLIQUID"
    COINBASE = "COINBASE"
    BYBIT = "BYBIT"
    
    # 其他
    LOCAL = "LOCAL"    # 本地合成数据


@dataclass
class TickData:
    """
    Tick 数据
    
    包含市场的最小粒度行情快照
    """
    symbol: str
    exchange: Exchange
    datetime: datetime
    
    # 价格数据
    last_price: float = 0          # 最新价（必须）
    high_price: float = 0          # Tick 内最高价（可选，提高 K 线准确性）
    low_price: float = 0           # Tick 内最低价（可选，提高 K 线准确性）
    
    # 成交量数据
    volume: float = 0              # 累计成交量（建议提供，用于计算 K 线成交量）
    turnover: float = 0            # 累计成交额（建议提供，用于计算 K 线成交额）
    last_volume: float = 0         # 最新成交量
    
    # 持仓量
    open_interest: float = 0       # 持仓量
    
    # 买卖盘（可选，K 线生成不需要）
    bid_price_1: float = 0
    bid_price_2: float = 0
    bid_price_3: float = 0
    bid_price_4: float = 0
    bid_price_5: float = 0
    ask_price_1: float = 0
    ask_price_2: float = 0
    ask_price_3: float = 0
    ask_price_4: float = 0
    ask_price_5: float = 0
    bid_volume_1: float = 0
    bid_volume_2: float = 0
    bid_volume_3: float = 0
    bid_volume_4: float = 0
    bid_volume_5: float = 0
    ask_volume_1: float = 0
    ask_volume_2: float = 0
    ask_volume_3: float = 0
    ask_volume_4: float = 0
    ask_volume_5: float = 0
    
    # 其他
    name: str = ""                 # 合约名称
    pre_close: float = 0           # 昨收价
    open_price: float = 0          # 开盘价
    limit_up: float = 0            # 涨停价
    limit_down: float = 0          # 跌停价
    
    @property
    def vt_symbol(self) -> str:
        """虚拟合约代码：symbol.exchange"""
        return f"{self.symbol}.{self.exchange.value}"


@dataclass
class BarData:
    """
    K 线数据
    
    包含某个时间周期的 OHLC 数据
    """
    symbol: str
    exchange: Exchange
    datetime: datetime
    
    # OHLC 数据
    open_price: float = 0          # 开盘价
    high_price: float = 0          # 最高价
    low_price: float = 0           # 最低价
    close_price: float = 0          # 收盘价
    
    # 成交量数据
    volume: float = 0              # 成交量（该周期内的增量）
    turnover: float = 0             # 成交额（该周期内的增量）
    
    # 持仓量
    open_interest: float = 0       # 持仓量（取最后一个 Tick 的值）
    
    # 周期（可选，用于标识 K 线周期）
    interval: str = "1m"           # 周期标识，如 "1m", "5m", "1h", "1d"
    
    @property
    def vt_symbol(self) -> str:
        """虚拟合约代码：symbol.exchange"""
        return f"{self.symbol}.{self.exchange.value}"
