"""
使用示例

演示如何使用数据录制模块
"""

import time
from datetime import datetime

from datarecorder import (
    RecorderEngine,
    TickData,
    Exchange,
    SQLiteDatabase
)


def example_csv_only():
    """示例 1: 只导出 CSV（默认）"""
    print("=" * 50)
    print("示例 1: 只导出 CSV（默认）")
    print("=" * 50)
    
    # 创建录制引擎（默认输出 CSV，database 可以为 None）
    recorder = RecorderEngine(
        database=None,  # 如果只导出 CSV，database 可以为 None
        output_format="csv",  # 默认 CSV
        output_dir="output"  # CSV 输出目录
    )
    
    # 添加要录制的合约
    recorder.add_tick_recording("BTCUSDT.BINANCE")
    recorder.add_bar_recording("BTCUSDT.BINANCE")
    
    # 启动录制
    recorder.start()
    
    # 模拟接收 Tick 数据
    base_price = 50000.0
    base_volume = 1000.0
    
    print("开始录制数据...")
    for i in range(10):
        tick = TickData(
            symbol="BTCUSDT",
            exchange=Exchange.BINANCE,
            datetime=datetime.now(),
            last_price=base_price + i * 10,
            volume=base_volume + i * 100,
            turnover=(base_price + i * 10) * (base_volume + i * 100),
            high_price=base_price + i * 10 + 5,
            low_price=base_price + i * 10 - 5,
            open_interest=1000000.0
        )
        
        recorder.on_tick(tick)
        recorder.on_timer()
        print(f"推送 Tick {i+1}: {tick.last_price}")
        time.sleep(0.1)
    
    time.sleep(1)
    recorder.stop()
    print("CSV 文件已导出到 output/ 目录\n")


def example_database_only():
    """示例 2: 只保存到数据库"""
    print("=" * 50)
    print("示例 2: 只保存到数据库")
    print("=" * 50)
    
    # 创建数据库实例
    db = SQLiteDatabase("market_data.db")
    
    # 创建录制引擎（只输出数据库）
    recorder = RecorderEngine(
        database=db,
        output_format="db"  # 只输出数据库
    )
    
    recorder.add_tick_recording("BTCUSDT.BINANCE")
    recorder.add_bar_recording("BTCUSDT.BINANCE")
    recorder.start()
    
    base_price = 50000.0
    base_volume = 1000.0
    
    print("开始录制数据...")
    for i in range(10):
        tick = TickData(
            symbol="BTCUSDT",
            exchange=Exchange.BINANCE,
            datetime=datetime.now(),
            last_price=base_price + i * 10,
            volume=base_volume + i * 100,
            turnover=(base_price + i * 10) * (base_volume + i * 100),
            high_price=base_price + i * 10 + 5,
            low_price=base_price + i * 10 - 5,
            open_interest=1000000.0
        )
        
        recorder.on_tick(tick)
        recorder.on_timer()
        print(f"推送 Tick {i+1}: {tick.last_price}")
        time.sleep(0.1)
    
    time.sleep(1)
    recorder.stop()
    print("数据已保存到 market_data.db\n")


def example_both():
    """示例 3: 同时输出 CSV 和数据库"""
    print("=" * 50)
    print("示例 3: 同时输出 CSV 和数据库")
    print("=" * 50)
    
    # 创建数据库实例
    db = SQLiteDatabase("market_data.db")
    
    # 创建录制引擎（同时输出 CSV 和数据库）
    recorder = RecorderEngine(
        database=db,
        output_format="both",  # 同时输出 CSV 和数据库
        output_dir="output"
    )
    
    recorder.add_tick_recording("BTCUSDT.BINANCE")
    recorder.add_bar_recording("BTCUSDT.BINANCE")
    recorder.start()
    
    base_price = 50000.0
    base_volume = 1000.0
    
    print("开始录制数据...")
    for i in range(10):
        tick = TickData(
            symbol="BTCUSDT",
            exchange=Exchange.BINANCE,
            datetime=datetime.now(),
            last_price=base_price + i * 10,
            volume=base_volume + i * 100,
            turnover=(base_price + i * 10) * (base_volume + i * 100),
            high_price=base_price + i * 10 + 5,
            low_price=base_price + i * 10 - 5,
            open_interest=1000000.0
        )
        
        recorder.on_tick(tick)
        recorder.on_timer()
        print(f"推送 Tick {i+1}: {tick.last_price}")
        time.sleep(0.1)
    
    time.sleep(1)
    recorder.stop()
    print("数据已同时保存到数据库和 CSV 文件\n")


def main():
    """主函数"""
    # 运行不同的示例
    example_csv_only()
    example_database_only()
    example_both()
    
    # 查看最终状态
    print("=" * 50)
    print("所有示例完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
