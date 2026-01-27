"""
使用示例

演示如何使用数据录制模块
"""

import time
from datetime import datetime

from datarecorder import (
    RecorderEngine,
    TickData,
    BarData,
    Exchange,
    SQLiteDatabase
)


def main():
    """主函数"""
    
    # 1. 创建数据库实例
    db = SQLiteDatabase("market_data.db")
    
    # 2. 创建录制引擎
    recorder = RecorderEngine(db)
    
    # 3. 添加要录制的合约
    recorder.add_tick_recording("BTCUSDT.BINANCE")
    recorder.add_bar_recording("BTCUSDT.BINANCE")
    
    # 4. 启动录制
    recorder.start()
    
    # 5. 模拟接收 Tick 数据
    base_price = 50000.0
    base_volume = 1000.0
    
    print("开始录制数据...")
    for i in range(10):
        # 创建 Tick 数据
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
        
        # 推送 Tick 数据
        recorder.on_tick(tick)
        
        # 调用定时器（实际使用中应该每秒调用一次）
        recorder.on_timer()
        
        print(f"推送 Tick {i+1}: {tick.last_price}")
        time.sleep(0.5)  # 模拟实时数据
    
    # 6. 等待数据保存完成
    print("等待数据保存...")
    time.sleep(2)
    
    # 7. 查看录制状态
    status = recorder.get_recording_status()
    print(f"\n录制状态: {status}")
    
    # 8. 停止录制
    recorder.stop()
    print("\n录制已停止")


if __name__ == "__main__":
    main()
