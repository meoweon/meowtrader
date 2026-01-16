# vnpy_ctabacktester 模块修改记录

## 基本信息

- **模块版本**: vnpy_ctabacktester-1.1.0
- **修改日期**: 2025-12-24
- **修改文件**: `src/vnpy_ctabacktester-1.1.0/vnpy_ctabacktester/ui/widget.py`

## 修改记录

### widget.py

#### CandleChartDialog.__init__ (修改方法)

**新增字段**:
- `self.text_items: list = []` - 文本项列表，用于存储仓位数字文本项
- `self.show_position_numbers: bool = True` - 仓位数字显示标志，默认显示
- `self.show_extra_fields: bool = False` - 额外字段显示标志，默认不显示
- `self.current_trades: list = []` - 存储当前交易数据，用于重绘
- `self.current_history: list = []` - 存储当前历史数据，用于重绘
- `self.extra_text_items: list = []` - 额外字段文本项列表

**修改前**: 无这些字段
**修改后**: 添加字段以支持仓位数字和额外字段的显示/隐藏功能

#### CandleChartDialog.init_ui (修改方法)

**新增字段**:
- `self.show_position_checkbox: QtWidgets.QCheckBox` - "显示仓位数字"复选框
- `self.show_extra_checkbox: QtWidgets.QCheckBox` - "显示额外字段"复选框

**新增功能**:
- 修改前: 图表上方无工具栏
- 修改后: 在图表上方创建工具栏，包含两个复选框，连接 `toggled` 信号到相应处理方法

#### CandleChartDialog.update_history (修改方法)

**新增功能**:
- 修改前: 不保存历史数据
- 修改后: 添加 `self.current_history = history`，保存历史数据用于重绘

#### CandleChartDialog.update_trades (修改方法)

**新增功能**:
- 修改前: 不保存交易数据，直接显示所有仓位数字
- 修改后: 
  1. 添加 `self.current_trades = trades`，保存交易数据用于重绘
  2. 根据 `self.show_position_numbers` 标志控制仓位数字显示
  3. 根据 `self.show_extra_fields` 标志显示额外字段（`open_extra` 和 `close_extra`）
  4. 将文本项添加到 `self.text_items` 和 `self.extra_text_items` 列表

**修改字段**:
- 仓位数字文本项创建条件
  - 修改前: 无条件创建
  - 修改后: `if self.show_position_numbers:` 条件下创建

#### CandleChartDialog.clear_data (修改方法)

**新增功能**:
- 修改前: 只清除图表数据
- 修改后: 添加 `self.text_items.clear()` 和 `self.extra_text_items.clear()`，清除文本项列表

#### CandleChartDialog.on_toggle_position_numbers (新增方法)

**新增方法**:
```python
def on_toggle_position_numbers(self, checked: bool) -> None
```

**功能**: 处理仓位数字显示复选框切换事件
- 更新 `self.show_position_numbers` 标志
- 如果交易数据已显示，根据复选框状态重新绘制或移除仓位数字

#### CandleChartDialog.on_toggle_extra_fields (新增方法)

**新增方法**:
```python
def on_toggle_extra_fields(self, checked: bool) -> None
```

**功能**: 处理额外字段显示复选框切换事件
- 更新 `self.show_extra_fields` 标志
- 如果交易数据已显示，根据复选框状态重新绘制或移除额外字段文本

#### StatisticsMonitor.init_ui (修改方法)

**修改字段**:
- `self.NoEditTriggers`
  - 修改前: `self.NoEditTriggers` (PySide2 风格)
  - 修改后: `QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers` (PySide6 风格)

#### BacktesterManager.start_backtesting (修改方法)

**修改字段**:
- `dialog.Accepted`
  - 修改前: `dialog.Accepted` (PySide2 风格)
  - 修改后: `QtWidgets.QDialog.DialogCode.Accepted` (PySide6 风格)

#### BacktesterManager.start_optimization (修改方法)

**修改字段**:
- `dialog.Accepted`
  - 修改前: `dialog.Accepted` (PySide2 风格)
  - 修改后: `QtWidgets.QDialog.DialogCode.Accepted` (PySide6 风格)

#### BacktesterManager.show_optimization_result (修改方法)

**修改字段**:
- `dialog.exec_()`
  - 修改前: `dialog.exec_()` (PySide2 风格)
  - 修改后: `dialog.exec()` (PySide6 风格)

#### BacktesterManager.show_backtesting_trades (修改方法)

**修改字段**:
- `self.trade_dialog.exec_()`
  - 修改前: `self.trade_dialog.exec_()` (PySide2 风格)
  - 修改后: `self.trade_dialog.exec()` (PySide6 风格)

#### BacktesterManager.show_backtesting_orders (修改方法)

**修改字段**:
- `self.order_dialog.exec_()`
  - 修改前: `self.order_dialog.exec_()` (PySide2 风格)
  - 修改后: `self.order_dialog.exec()` (PySide6 风格)

#### BacktesterManager.show_daily_results (修改方法)

**修改字段**:
- `self.daily_dialog.exec_()`
  - 修改前: `self.daily_dialog.exec_()` (PySide2 风格)
  - 修改后: `self.daily_dialog.exec()` (PySide6 风格)

#### BacktesterManager.show_candle_chart (修改方法)

**修改字段**:
- `self.candle_dialog.exec_()`
  - 修改前: `self.candle_dialog.exec_()` (PySide2 风格)
  - 修改后: `self.candle_dialog.exec()` (PySide6 风格)

#### OptimizationResultMonitor.init_ui (修改方法)

**修改字段**:
- `table.NoEditTriggers`
  - 修改前: `table.NoEditTriggers` (PySide2 风格)
  - 修改后: `QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers` (PySide6 风格)

#### generate_trade_pairs (模块级函数，修改)

**新增导入**:
- `Offset` 到导入语句: `from vnpy.trader.constant import Interval, Direction, Exchange, Offset`
- 修改前: 只导入 `Interval, Direction, Exchange`
- 修改后: 添加 `Offset` 导入

**修改逻辑**:
- 修改前: 只按 `direction` 配对交易，将 `Direction.SHORT` 的交易都当作开空仓
- 修改后: 
  1. 使用 `offset` 字段区分开仓和平仓
  2. 只有 `Offset.OPEN` 的交易才作为持仓加入列表
  3. `Offset.CLOSE` 的交易匹配相反方向的持仓（LIFO 策略）
  4. 使用开仓交易的 `direction` 作为配对结果的方向

**新增字段**:
- 配对数据字典中添加 `open_extra` 和 `close_extra` 字段
  - `open_extra`: 从开仓交易的 `trade.extra` 字段获取（如果存在）
  - `close_extra`: 从平仓交易的 `trade.extra` 字段获取（如果存在）

**修改效果**:
- 修改前: 如果策略只做多，图表上仍会显示紫色的做空箭头（误将平多仓的 `Direction.SHORT` 当作开空仓）
- 修改后: 如果策略只做多，图表只显示黄色箭头（多头交易），不会误显示紫色箭头
