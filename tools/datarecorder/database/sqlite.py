"""
SQLite 数据库实现
"""

import sqlite3
from typing import List
from datetime import datetime
from pathlib import Path

from .base import Database
from ..core.models import TickData, BarData


class SQLiteDatabase(Database):
    """
    SQLite 数据库实现
    
    使用 SQLite 存储 Tick 和 K 线数据
    """
    
    def __init__(self, db_path: str = "market_data.db"):
        """
        初始化
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建 Tick 数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tick_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                exchange TEXT NOT NULL,
                datetime TEXT NOT NULL,
                last_price REAL NOT NULL,
                volume REAL DEFAULT 0,
                turnover REAL DEFAULT 0,
                open_interest REAL DEFAULT 0,
                high_price REAL DEFAULT 0,
                low_price REAL DEFAULT 0,
                bid_price_1 REAL DEFAULT 0,
                ask_price_1 REAL DEFAULT 0,
                UNIQUE(symbol, exchange, datetime)
            )
        """)
        
        # 创建 K 线数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bar_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                exchange TEXT NOT NULL,
                datetime TEXT NOT NULL,
                interval TEXT NOT NULL DEFAULT '1m',
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                volume REAL DEFAULT 0,
                turnover REAL DEFAULT 0,
                open_interest REAL DEFAULT 0,
                UNIQUE(symbol, exchange, datetime, interval)
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tick_symbol_datetime 
            ON tick_data(symbol, exchange, datetime)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bar_symbol_datetime 
            ON bar_data(symbol, exchange, datetime, interval)
        """)
        
        conn.commit()
        conn.close()
    
    def save_tick_data(self, ticks: List[TickData]) -> bool:
        """保存 Tick 数据"""
        if not ticks:
            return True
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for tick in ticks:
                cursor.execute("""
                    INSERT OR REPLACE INTO tick_data 
                    (symbol, exchange, datetime, last_price, volume, turnover, 
                     open_interest, high_price, low_price, bid_price_1, ask_price_1)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tick.symbol,
                    tick.exchange.value,
                    tick.datetime.isoformat(),
                    tick.last_price,
                    tick.volume,
                    tick.turnover,
                    tick.open_interest,
                    tick.high_price,
                    tick.low_price,
                    tick.bid_price_1,
                    tick.ask_price_1,
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存 Tick 数据失败: {e}")
            return False
    
    def save_bar_data(self, bars: List[BarData]) -> bool:
        """保存 K 线数据"""
        if not bars:
            return True
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for bar in bars:
                cursor.execute("""
                    INSERT OR REPLACE INTO bar_data 
                    (symbol, exchange, datetime, interval, open_price, high_price, 
                     low_price, close_price, volume, turnover, open_interest)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bar.symbol,
                    bar.exchange.value,
                    bar.datetime.isoformat(),
                    bar.interval,
                    bar.open_price,
                    bar.high_price,
                    bar.low_price,
                    bar.close_price,
                    bar.volume,
                    bar.turnover,
                    bar.open_interest,
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存 K 线数据失败: {e}")
            return False
