"""
CSV 导出器

导出数据为 CSV 格式，兼容 vnpy_datamanager 的导入要求
"""

import csv
from pathlib import Path
from typing import List
from datetime import datetime

from ..core.models import TickData, BarData


class CSVExporter:
    """CSV 导出器"""
    
    @staticmethod
    def export_bar_data(bars: List[BarData], file_path: str, append: bool = False) -> bool:
        """
        导出 K 线数据到 CSV 文件
        
        Args:
            bars: K 线数据列表
            file_path: CSV 文件路径
            append: 是否追加模式（默认 False，覆盖模式）
        
        Returns:
            是否成功
        """
        if not bars:
            return True
        
        try:
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 表头（与 vnpy_datamanager 兼容）
            fieldnames = [
                "symbol",
                "exchange",
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover",
                "open_interest"
            ]
            
            # 打开文件（追加或覆盖模式）
            mode = "a" if append else "w"
            file_exists = Path(file_path).exists()
            
            with open(file_path, mode, newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
                
                # 如果是新文件或覆盖模式，写入表头
                if not append or not file_exists:
                    writer.writeheader()
                
                # 写入数据
                for bar in bars:
                    writer.writerow({
                        "symbol": bar.symbol,
                        "exchange": bar.exchange.value,
                        "datetime": bar.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": bar.open_price,
                        "high": bar.high_price,
                        "low": bar.low_price,
                        "close": bar.close_price,
                        "volume": bar.volume,
                        "turnover": bar.turnover,
                        "open_interest": bar.open_interest,
                    })
            
            return True
        except Exception as e:
            print(f"导出 K 线 CSV 失败: {e}")
            return False
    
    @staticmethod
    def export_tick_data(ticks: List[TickData], file_path: str, append: bool = False) -> bool:
        """
        导出 Tick 数据到 CSV 文件
        
        Args:
            ticks: Tick 数据列表
            file_path: CSV 文件路径
            append: 是否追加模式（默认 False，覆盖模式）
        
        Returns:
            是否成功
        """
        if not ticks:
            return True
        
        try:
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 表头
            fieldnames = [
                "symbol",
                "exchange",
                "datetime",
                "last_price",
                "volume",
                "turnover",
                "open_interest",
                "high_price",
                "low_price",
                "bid_price_1",
                "ask_price_1"
            ]
            
            # 打开文件（追加或覆盖模式）
            mode = "a" if append else "w"
            file_exists = Path(file_path).exists()
            
            with open(file_path, mode, newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
                
                # 如果是新文件或覆盖模式，写入表头
                if not append or not file_exists:
                    writer.writeheader()
                
                # 写入数据
                for tick in ticks:
                    writer.writerow({
                        "symbol": tick.symbol,
                        "exchange": tick.exchange.value,
                        "datetime": tick.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "last_price": tick.last_price,
                        "volume": tick.volume,
                        "turnover": tick.turnover,
                        "open_interest": tick.open_interest,
                        "high_price": tick.high_price,
                        "low_price": tick.low_price,
                        "bid_price_1": tick.bid_price_1,
                        "ask_price_1": tick.ask_price_1,
                    })
            
            return True
        except Exception as e:
            print(f"导出 Tick CSV 失败: {e}")
            return False
