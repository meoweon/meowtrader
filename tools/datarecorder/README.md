# 数据录制模块

独立的数据录制模块，从 `vnpy_datarecorder` 提取核心功能，完全独立，不依赖任何框架。

## 功能特性

- ✅ **Tick 数据录制**：实时录制每个 Tick 的详细数据
- ✅ **K 线自动生成**：从 Tick 数据自动生成 1 分钟 K 线
- ✅ **多合约支持**：同时录制多个合约的行情
- ✅ **数据持久化**：支持 CSV 导出（默认）和数据库保存
- ✅ **vnpy 兼容**：CSV 格式兼容 vnpy_datamanager 的导入要求
- ✅ **配置管理**：录制列表、时间过滤等配置可保存
- ✅ **批量保存**：定时批量保存，提高性能
- ✅ **时间过滤**：过滤异常时间戳的 Tick 数据

## 输出格式

### CSV 格式（默认）

默认输出 CSV 文件，符合 vnpy_datamanager 的导入要求：

**K 线 CSV 格式：**
```csv
symbol,exchange,datetime,open,high,low,close,volume,turnover,open_interest
BTCUSDT,BINANCE,2025-01-27 10:00:00,50000.0,50010.0,49990.0,50005.0,1000.0,50000000.0,1000000.0
```

**Tick CSV 格式：**
```csv
symbol,exchange,datetime,last_price,volume,turnover,open_interest,high_price,low_price,bid_price_1,ask_price_1
BTCUSDT,BINANCE,2025-01-27 10:00:00,50000.0,1000.0,50000000.0,1000000.0,50005.0,49995.0,49999.0,50001.0
```

### 数据库格式（可选）

如果指定 `output_format="db"` 或 `"both"`，会生成 SQLite 数据库文件，表结构与 vnpy_sqlite 一致。

## 快速开始

### 1. 基本使用（默认 CSV 输出）

```python
from datarecorder import RecorderEngine, TickData, Exchange
from datetime import datetime

# 创建录制引擎（默认输出 CSV）
recorder = RecorderEngine(
    database=None,  # 只导出 CSV，不需要数据库
    output_format="csv",
    output_dir="output"  # CSV 文件保存目录
)

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

# 停止录制（会自动导出 CSV）
recorder.stop()
```

### 2. 同时输出 CSV 和数据库

```python
from datarecorder import RecorderEngine, SQLiteDatabase

# 创建数据库实例
db = SQLiteDatabase("market_data.db")

# 创建录制引擎（同时输出 CSV 和数据库）
recorder = RecorderEngine(
    database=db,
    output_format="both",  # 同时输出 CSV 和数据库
    output_dir="output"
)
```

### 3. 只输出数据库

```python
from datarecorder import RecorderEngine, SQLiteDatabase

db = SQLiteDatabase("market_data.db")
recorder = RecorderEngine(
    database=db,
    output_format="db"  # 只输出数据库
)
```

### 4. 完整示例

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

#### 初始化参数

- `database`: 数据库实例（可选，如果为 None 则只导出 CSV）
- `setting_file`: 配置文件路径（默认 "data_recorder_setting.json"）
- `log_callback`: 日志回调函数（默认 print）
- `output_format`: 输出格式，"csv"（默认）、"db" 或 "both"
- `output_dir`: 输出目录（CSV 文件保存位置，默认 "output"）

#### 方法

- `start()`: 启动录制
- `stop()`: 停止录制（会自动导出剩余数据）
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

## 使用 vnpy 导入数据

### 方式 1：导入 CSV 文件

1. 使用 datarecorder 生成 CSV 文件（默认）
2. 在 vnpy_datamanager 中：
   - 点击"导入数据"
   - 选择 CSV 文件
   - 配置字段映射（默认表头已匹配）
   - 导入完成

### 方式 2：使用数据库文件

1. 使用 datarecorder 生成数据库文件（`output_format="db"`）
2. 将数据库文件复制到 `.vntrader` 目录
3. vnpy 回测引擎会自动读取该数据库

## 注意事项

1. **定时器调用**：`on_timer()` 建议每秒调用一次，用于批量保存数据
2. **时间过滤**：默认过滤偏离本地时间 60 秒以上的 Tick 数据
3. **数据保存**：数据会定时批量保存（默认每 10 个周期保存一次）
4. **停止录制**：调用 `stop()` 时会自动保存剩余数据并导出 CSV
5. **CSV 文件命名**：格式为 `{symbol}_{exchange}_bar.csv` 和 `{symbol}_{exchange}_tick.csv`

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
│   ├── sqlite.py          # SQLite 实现
│   └── csv_exporter.py    # CSV 导出器
├── example.py             # 使用示例
└── README.md              # 说明文档
```

## 许可证

MIT License
