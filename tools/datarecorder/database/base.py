"""
数据库接口抽象基类
"""

from abc import ABC, abstractmethod
from typing import List

from ..core.models import TickData, BarData


class Database(ABC):
    """
    数据库接口抽象基类
    
    子类需要实现具体的数据库保存逻辑
    """
    
    @abstractmethod
    def save_tick_data(self, ticks: List[TickData]) -> bool:
        """
        保存 Tick 数据
        
        Args:
            ticks: Tick 数据列表
            
        Returns:
            是否保存成功
        """
        pass
    
    @abstractmethod
    def save_bar_data(self, bars: List[BarData]) -> bool:
        """
        保存 K 线数据
        
        Args:
            bars: K 线数据列表
            
        Returns:
            是否保存成功
        """
        pass
