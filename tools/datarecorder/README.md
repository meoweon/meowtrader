# 数据录制模块

独立的数据录制模块，从 `vnpy_datarecorder` 提取核心功能，完全独立，不依赖任何框架。

## 功能特性

- ✅ **Tick 数据录制**：实时录制每个 Tick 的详细数据
- ✅ **K 线自动生成**：从 Tick 数据自动生成 1 分钟 K 线
- ✅ **多合约支持**：同时录制多个合约的行情
- ✅ **数据持久化**：自动保存到数据库（SQLite）
- ✅ **配置管理**：录制列表、时间过滤等配置可保存
- ✅ **批量保存**：定时批量保存，提高性能
- ✅ **时间过滤**：过滤异常时间戳的 Tick 数据

## 快速开始

### 1. 基本使用

```python
from datarecorder import RecorderEngine, TickData, Exchange, SQLiteDatabase
from datetime import datetime

# 创建数据库
db = SQLiteDatabase("market_data.db")

# 创建录制引擎
recorder = RecorderEngine(db)

# 添加要录制的合约
recorder.add_tick_recording("BTCUSDT.BINANCE")
recorder.add_bar_recording("BTCUSDT.BINANCE")

# 启动录制
recorder.start()

# 接收 Tick 数据
tick = TickData(
    symbol="BTCUSDT",
    exchange=Exchange.BINANCE,
    datetime=datetime.now(),
    last_price=50000.0,
    volume=1000.0,
    turnover=50000000.0
)
recorder.on_tick(tick)

# 定期调用定时器（建议每秒调用一次）
recorder.on_timer()

# 停止录制
recorder.stop()
```

### 2. 完整示例

参见 `example.py` 文件。

## 数据结构

### TickData（Tick 数据）

**必需字段：**
- `symbol`: 合约代码
- `exchange`: 交易所枚举
- `datetime`: 时间戳
- `last_price`: 最新价（不能为 0）

**建议字段：**
- `volume`: 累计成交量（用于计算 K 线成交量）
- `turnover`: 累计成交额（用于计算 K 线成交额）
- `high_price`: Tick 内最高价（提高 K 线 High 准确性）
- `low_price`: Tick 内最低价（提高 K 线 Low 准确性）

### BarData（K 线数据）

自动生成，包含：
- `open_price`: 开盘价
- `high_price`: 最高价
- `low_price`: 最低价
- `close_price`: 收盘价
- `volume`: 成交量（该周期内的增量）
- `turnover`: 成交额（该周期内的增量）

## API 参考

### RecorderEngine

#### 方法

- `start()`: 启动录制
- `stop()`: 停止录制
- `on_tick(tick: TickData)`: 接收 Tick 数据
- `on_timer()`: 定时器回调（建议每秒调用一次）
- `add_tick_recording(vt_symbol: str)`: 添加 Tick 录制
- `remove_tick_recording(vt_symbol: str)`: 移除 Tick 录制
- `add_bar_recording(vt_symbol: str)`: 添加 K 线录制
- `remove_bar_recording(vt_symbol: str)`: 移除 K 线录制
- `get_recording_status()`: 获取录制状态

### Database

#### SQLiteDatabase

- `save_tick_data(ticks: List[TickData])`: 保存 Tick 数据
- `save_bar_data(bars: List[BarData])`: 保存 K 线数据

## 配置

配置文件：`data_recorder_setting.json`

```json
{
  "tick": ["BTCUSDT.BINANCE", "ETHUSDT.BINANCE"],
  "bar": ["BTCUSDT.BINANCE"],
  "filter_window": 60
}
```

## 注意事项

1. **定时器调用**：`on_timer()` 建议每秒调用一次，用于批量保存数据
2. **时间过滤**：默认过滤偏离本地时间 60 秒以上的 Tick 数据
3. **数据保存**：数据会定时批量保存（默认每 10 个周期保存一次）
4. **停止录制**：调用 `stop()` 时会自动保存剩余数据

## 目录结构

```
datarecorder/
├── __init__.py              # 模块导出
├── core/                    # 核心功能
│   ├── models.py           # 数据模型
│   ├── bar_generator.py    # K 线生成器
│   └── recorder.py         # 录制引擎
├── database/               # 数据库实现
│   ├── base.py            # 数据库接口
│   └── sqlite.py          # SQLite 实现
├── example.py             # 使用示例
└── README.md              # 说明文档
```

## 许可证

MIT License
