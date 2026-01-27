"""
K 线生成器

从 Tick 数据生成 K 线数据
"""

from typing import Callable, Optional
from datetime import datetime

from .models import TickData, BarData


class BarGenerator:
    """
    K 线生成器
    
    从 Tick 数据生成 1 分钟 K 线
    """
    
    def __init__(self, on_bar: Callable[[BarData], None]):
        """
        初始化
        
        Args:
            on_bar: K 线完成时的回调函数
        """
        self.bar: Optional[BarData] = None
        self.on_bar: Callable = on_bar
        self.last_tick: Optional[TickData] = None
    
    def update_tick(self, tick: TickData) -> None:
        """
        更新 Tick 数据，生成 K 线
        
        Args:
            tick: Tick 数据
        """
        # 过滤无效数据
        if not tick.last_price:
            return
        
        new_minute = False
        
        # 判断是否新分钟
        if not self.bar:
            # 第一个 Tick，创建新 K 线
            new_minute = True
        elif (
            self.bar.datetime.minute != tick.datetime.minute
            or self.bar.datetime.hour != tick.datetime.hour
        ):
            # 时间跨分钟/小时，完成当前 K 线
            self.bar.datetime = self.bar.datetime.replace(second=0, microsecond=0)
            self.on_bar(self.bar)
            new_minute = True
        
        # 创建新 K 线
        if new_minute:
            self.bar = BarData(
                symbol=tick.symbol,
                exchange=tick.exchange,
                datetime=tick.datetime,
                interval="1m",
                open_price=tick.last_price,   # 开盘价 = 第一个 Tick 的价格
                high_price=tick.last_price,   # 最高价 = 第一个 Tick 的价格
                low_price=tick.last_price,    # 最低价 = 第一个 Tick 的价格
                close_price=tick.last_price,  # 收盘价 = 第一个 Tick 的价格
                open_interest=tick.open_interest
            )
        # 更新当前 K 线
        elif self.bar:
            # 更新最高价
            self.bar.high_price = max(self.bar.high_price, tick.last_price)
            if self.last_tick and tick.high_price > self.last_tick.high_price:
                self.bar.high_price = max(self.bar.high_price, tick.high_price)
            
            # 更新最低价
            self.bar.low_price = min(self.bar.low_price, tick.last_price)
            if self.last_tick and tick.low_price < self.last_tick.low_price:
                self.bar.low_price = min(self.bar.low_price, tick.low_price)
            
            # 更新收盘价（总是等于最新 Tick 的价格）
            self.bar.close_price = tick.last_price
            self.bar.open_interest = tick.open_interest
            self.bar.datetime = tick.datetime
        
        # 计算成交量增量
        if self.last_tick and self.bar:
            volume_change = tick.volume - self.last_tick.volume
            self.bar.volume += max(volume_change, 0)  # 只累加正增量
            
            turnover_change = tick.turnover - self.last_tick.turnover
            self.bar.turnover += max(turnover_change, 0)
        
        # 保存上一个 Tick（用于下次计算增量）
        self.last_tick = tick
