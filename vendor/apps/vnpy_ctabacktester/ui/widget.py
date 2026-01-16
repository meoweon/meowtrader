import csv
import subprocess
from datetime import datetime, timedelta
from copy import copy
from typing import List, Tuple

import numpy as np
import pyqtgraph as pg
from pandas import DataFrame

from vnpy.trader.constant import Interval, Direction, Exchange, Offset
from vnpy.trader.engine import MainEngine, BaseEngine
from vnpy.trader.ui import QtCore, QtWidgets, QtGui
from vnpy.trader.ui.widget import BaseMonitor, BaseCell, DirectionCell, EnumCell
from vnpy.event import Event, EventEngine
from vnpy.chart import ChartWidget, CandleItem, VolumeItem
from vnpy.trader.utility import load_json, save_json
from vnpy.trader.object import BarData, TradeData, OrderData
from vnpy.trader.database import DB_TZ, BarOverview
from vnpy.trader.database import BaseDatabase, get_database
from vnpy_ctastrategy.backtesting import DailyResult
from qfluentwidgets import (
    PushButton, ComboBox, LineEdit, BodyLabel, DateEdit, TableWidget, SpinBox, MessageBox
)
from qframelesswindow import FramelessDialog, FramelessWindow
from qframelesswindow.titlebar import StandardTitleBar

from ..engine import (
    APP_NAME,
    EVENT_BACKTESTER_LOG,
    EVENT_BACKTESTER_BACKTESTING_FINISHED,
    EVENT_BACKTESTER_OPTIMIZATION_FINISHED,
    OptimizationSetting
)


class BacktesterManager(FramelessWindow):
    """"""

    setting_filename: str = "cta_backtester_setting.json"

    signal_log: QtCore.Signal = QtCore.Signal(Event)
    signal_backtesting_finished: QtCore.Signal = QtCore.Signal(Event)
    signal_optimization_finished: QtCore.Signal = QtCore.Signal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        # Set up Fluent-style title bar
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background for Fluent theme
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.backtester_engine: BaseEngine = main_engine.get_engine(APP_NAME)
        self.class_names: list = []
        self.settings: dict = {}

        self.target_display: str = ""
        
        self.database: BaseDatabase = get_database()

        self.init_ui()
        self.register_event()
        self.backtester_engine.init_engine()
        self.init_strategy_settings()
        self.init_symbol_list()  # 初始化合约列表
        self.load_backtesting_setting()

    def init_symbol_list(self) -> None:
        """
        从数据库加载可用的合约列表到下拉框
        """
        try:
            if not self.database:
                # 如果数据库未初始化，使用默认值
                if self.symbol_combo.count() == 0:
                    self.symbol_combo.addItem("IF88.CFFEX")
                return
            
            overviews: list[BarOverview] = self.database.get_bar_overview()
            
            # 获取当前选择的周期
            current_interval: str = self.interval_combo.currentText()
            if not current_interval:
                # 如果周期还未设置，使用默认值
                if self.symbol_combo.count() == 0:
                    self.symbol_combo.addItem("IF88.CFFEX")
                return
                
            interval: Interval = Interval(current_interval)
            
            # 过滤出当前周期下的所有合约
            vt_symbols: set = set()
            for overview in overviews:
                if overview.interval == interval:
                    vt_symbol: str = f"{overview.symbol}.{overview.exchange.value}"
                    vt_symbols.add(vt_symbol)
            
            # 排序并添加到下拉框
            sorted_symbols: list = sorted(vt_symbols)
            self.symbol_combo.clear()
            self.symbol_combo.addItems(sorted_symbols)
            
            if sorted_symbols:
                self.write_log(f"已加载 {len(sorted_symbols)} 个可用合约")
            else:
                self.write_log(f"当前周期({current_interval})下没有可用数据，请先下载数据")
                # 如果没有数据，至少保留一个默认值
                if self.symbol_combo.count() == 0:
                    self.symbol_combo.addItem("IF88.CFFEX")
        except Exception as e:
            self.write_log(f"加载合约列表失败: {e}")
            # 如果加载失败，至少保留一个默认值
            if self.symbol_combo.count() == 0:
                self.symbol_combo.addItem("IF88.CFFEX")

    def on_interval_changed(self, interval_text: str) -> None:
        """
        当K线周期改变时，更新合约列表
        """
        self.init_symbol_list()

    def init_strategy_settings(self) -> None:
        """"""
        self.class_names = self.backtester_engine.get_strategy_class_names()
        self.class_names.sort()

        for class_name in self.class_names:
            setting: dict = self.backtester_engine.get_default_setting(class_name)
            self.settings[class_name] = setting

        self.class_combo.addItems(self.class_names)

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("CTA回测")

        # Setting Part
        self.class_combo: ComboBox = ComboBox()

        # 使用标准 QComboBox 以支持可编辑功能
        self.symbol_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.symbol_combo.setEditable(True)  # 允许手动输入，也支持下拉选择
        self.symbol_combo.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)  # 不自动插入新项
        
        # 设置样式以匹配 Fluent 主题，使用Qt默认箭头
        self.symbol_combo.setStyleSheet("""
            QComboBox {
                background-color: rgb(45, 45, 45);
                color: white;
                border: 1px solid rgb(60, 60, 60);
                border-radius: 4px;
                padding: 4px;
                padding-right: 30px;
            }
            QComboBox:hover {
                border: 1px solid rgb(80, 80, 80);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid rgb(60, 60, 60);
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: rgb(50, 50, 50);
            }
            QComboBox::drop-down:hover {
                background-color: rgb(60, 60, 60);
            }
            QComboBox QAbstractItemView {
                background-color: rgb(45, 45, 45);
                color: white;
                selection-background-color: rgb(60, 60, 60);
                border: 1px solid rgb(60, 60, 60);
            }
        """)

        self.interval_combo: ComboBox = ComboBox()
        for interval in Interval:
            self.interval_combo.addItem(interval.value)
        self.interval_combo.currentTextChanged.connect(self.on_interval_changed)  # 当周期改变时更新合约列表

        end_dt: datetime = datetime.now()
        start_dt: datetime = end_dt - timedelta(days=3 * 365)

        self.start_date_edit: DateEdit = DateEdit()
        self.start_date_edit.setDate(QtCore.QDate(
            start_dt.year,
            start_dt.month,
            start_dt.day
        ))
        self.end_date_edit: DateEdit = DateEdit()
        self.end_date_edit.setDate(QtCore.QDate.currentDate())

        self.rate_line: LineEdit = LineEdit()
        self.rate_line.setText("0.000025")
        self.slippage_line: LineEdit = LineEdit()
        self.slippage_line.setText("0.2")
        self.size_line: LineEdit = LineEdit()
        self.size_line.setText("300")
        self.pricetick_line: LineEdit = LineEdit()
        self.pricetick_line.setText("0.2")
        self.capital_line: LineEdit = LineEdit()
        self.capital_line.setText("1000000")

        backtesting_button: PushButton = PushButton("开始回测")
        backtesting_button.clicked.connect(self.start_backtesting)

        optimization_button: PushButton = PushButton("参数优化")
        optimization_button.clicked.connect(self.start_optimization)

        self.result_button: PushButton = PushButton("优化结果")
        self.result_button.clicked.connect(self.show_optimization_result)
        self.result_button.setEnabled(False)

        downloading_button: PushButton = PushButton("下载数据")
        downloading_button.clicked.connect(self.start_downloading)

        self.order_button: PushButton = PushButton("委托记录")
        self.order_button.clicked.connect(self.show_backtesting_orders)
        self.order_button.setEnabled(False)

        self.trade_button: PushButton = PushButton("成交记录")
        self.trade_button.clicked.connect(self.show_backtesting_trades)
        self.trade_button.setEnabled(False)

        self.daily_button: PushButton = PushButton("每日盈亏")
        self.daily_button.clicked.connect(self.show_daily_results)
        self.daily_button.setEnabled(False)

        self.candle_button: PushButton = PushButton("K线图表")
        self.candle_button.clicked.connect(self.show_candle_chart)
        self.candle_button.setEnabled(False)

        edit_button: PushButton = PushButton("代码编辑")
        edit_button.clicked.connect(self.edit_strategy_code)

        reload_button: PushButton = PushButton("策略重载")
        reload_button.clicked.connect(self.reload_strategy_class)

        for button in [
            backtesting_button,
            optimization_button,
            downloading_button,
            self.result_button,
            self.order_button,
            self.trade_button,
            self.daily_button,
            self.candle_button,
            edit_button,
            reload_button
        ]:
            button.setFixedHeight(button.sizeHint().height() * 2)

        # Use QGridLayout with BodyLabel for proper Fluent theme inheritance
        form: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        form.addWidget(BodyLabel("交易策略"), 0, 0)
        form.addWidget(self.class_combo, 0, 1)
        form.addWidget(BodyLabel("本地代码"), 1, 0)
        form.addWidget(self.symbol_combo, 1, 1)
        form.addWidget(BodyLabel("K线周期"), 2, 0)
        form.addWidget(self.interval_combo, 2, 1)
        form.addWidget(BodyLabel("开始日期"), 3, 0)
        form.addWidget(self.start_date_edit, 3, 1)
        form.addWidget(BodyLabel("结束日期"), 4, 0)
        form.addWidget(self.end_date_edit, 4, 1)
        form.addWidget(BodyLabel("手续费率"), 5, 0)
        form.addWidget(self.rate_line, 5, 1)
        form.addWidget(BodyLabel("交易滑点"), 6, 0)
        form.addWidget(self.slippage_line, 6, 1)
        form.addWidget(BodyLabel("合约乘数"), 7, 0)
        form.addWidget(self.size_line, 7, 1)
        form.addWidget(BodyLabel("价格跳动"), 8, 0)
        form.addWidget(self.pricetick_line, 8, 1)
        form.addWidget(BodyLabel("回测资金"), 9, 0)
        form.addWidget(self.capital_line, 9, 1)

        result_grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        result_grid.addWidget(self.trade_button, 0, 0)
        result_grid.addWidget(self.order_button, 0, 1)
        result_grid.addWidget(self.daily_button, 1, 0)
        result_grid.addWidget(self.candle_button, 1, 1)

        left_vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        left_vbox.addLayout(form)
        left_vbox.addWidget(backtesting_button)
        left_vbox.addWidget(downloading_button)
        left_vbox.addStretch()
        left_vbox.addLayout(result_grid)
        left_vbox.addStretch()
        left_vbox.addWidget(optimization_button)
        left_vbox.addWidget(self.result_button)
        left_vbox.addStretch()
        left_vbox.addWidget(edit_button)
        left_vbox.addWidget(reload_button)

        # Result part
        self.statistics_monitor: StatisticsMonitor = StatisticsMonitor()

        self.log_monitor: QtWidgets.QPlainTextEdit = QtWidgets.QPlainTextEdit()
        # 设置深色主题样式
        self.log_monitor.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgb(32, 32, 32);
                color: white;
                border: 1px solid rgb(60, 60, 60);
                border-radius: 4px;
            }
        """)

        self.chart: BacktesterChart = BacktesterChart()
        chart: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        chart.addWidget(self.chart)

        self.trade_dialog: BacktestingResultDialog = BacktestingResultDialog(
            self.main_engine,
            self.event_engine,
            "回测成交记录",
            BacktestingTradeMonitor
        )
        self.order_dialog: BacktestingResultDialog = BacktestingResultDialog(
            self.main_engine,
            self.event_engine,
            "回测委托记录",
            BacktestingOrderMonitor
        )
        self.daily_dialog: BacktestingResultDialog = BacktestingResultDialog(
            self.main_engine,
            self.event_engine,
            "回测每日盈亏",
            DailyResultMonitor
        )

        # Candle Chart
        self.candle_dialog: CandleChartDialog = CandleChartDialog()

        # Layout
        middle_vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        middle_vbox.addWidget(self.statistics_monitor)
        middle_vbox.addWidget(self.log_monitor)

        left_hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        left_hbox.addLayout(left_vbox)
        left_hbox.addLayout(middle_vbox)

        left_widget: QtWidgets.QWidget = QtWidgets.QWidget()
        left_widget.setLayout(left_hbox)

        right_vbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        right_vbox.addWidget(self.chart)

        right_widget: QtWidgets.QWidget = QtWidgets.QWidget()
        right_widget.setLayout(right_vbox)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addWidget(left_widget)
        hbox.addWidget(right_widget)

        # Create container widget for FramelessWindow content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(hbox)

        # Main layout with title bar margin
        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def load_backtesting_setting(self) -> None:
        """"""
        setting: dict = load_json(self.setting_filename)
        if not setting:
            return

        self.class_combo.setCurrentIndex(
            self.class_combo.findText(setting["class_name"])
        )

        # 设置合约下拉框的值
        symbol_index: int = self.symbol_combo.findText(setting["vt_symbol"])
        if symbol_index >= 0:
            self.symbol_combo.setCurrentIndex(symbol_index)
        else:
            # 如果找不到，设置为当前文本（可能是手动输入的）
            self.symbol_combo.setCurrentText(setting["vt_symbol"])

        self.interval_combo.setCurrentIndex(
            self.interval_combo.findText(setting["interval"])
        )

        start_str: str = setting.get("start", "")
        if start_str:
            start_dt: QtCore.QDate = QtCore.QDate.fromString(start_str, "yyyy-MM-dd")
            self.start_date_edit.setDate(start_dt)

        self.rate_line.setText(str(setting["rate"]))
        self.slippage_line.setText(str(setting["slippage"]))
        self.size_line.setText(str(setting["size"]))
        self.pricetick_line.setText(str(setting["pricetick"]))
        self.capital_line.setText(str(setting["capital"]))

    def register_event(self) -> None:
        """"""
        self.signal_log.connect(self.process_log_event)
        self.signal_backtesting_finished.connect(
            self.process_backtesting_finished_event)
        self.signal_optimization_finished.connect(
            self.process_optimization_finished_event)

        self.event_engine.register(EVENT_BACKTESTER_LOG, self.signal_log.emit)
        self.event_engine.register(
            EVENT_BACKTESTER_BACKTESTING_FINISHED, self.signal_backtesting_finished.emit)
        self.event_engine.register(
            EVENT_BACKTESTER_OPTIMIZATION_FINISHED, self.signal_optimization_finished.emit)

    def process_log_event(self, event: Event) -> None:
        """"""
        msg = event.data
        self.write_log(msg)

    def write_log(self, msg) -> None:
        """"""
        timestamp: str = datetime.now().strftime("%H:%M:%S")
        msg: str = f"{timestamp}\t{msg}"
        self.log_monitor.appendPlainText(msg)

    def process_backtesting_finished_event(self, event: Event) -> None:
        """"""
        statistics: dict = self.backtester_engine.get_result_statistics()
        self.statistics_monitor.set_data(statistics)

        df: DataFrame = self.backtester_engine.get_result_df()
        self.chart.set_data(df)

        self.trade_button.setEnabled(True)
        self.order_button.setEnabled(True)
        self.daily_button.setEnabled(True)

        # Tick data can not be displayed using candle chart
        interval: str = self.interval_combo.currentText()
        if interval != Interval.TICK.value:
            self.candle_button.setEnabled(True)

    def process_optimization_finished_event(self, event: Event) -> None:
        """"""
        self.write_log("请点击[优化结果]按钮查看")
        self.result_button.setEnabled(True)

    def start_backtesting(self) -> None:
        """"""
        class_name: str = self.class_combo.currentText()
        if not class_name:
            self.write_log("请选择要回测的策略")
            return

        vt_symbol: str = self.symbol_combo.currentText()
        interval: str = self.interval_combo.currentText()
        start: datetime = self.start_date_edit.dateTime().toPython()
        end: datetime = self.end_date_edit.dateTime().toPython()
        rate: float = float(self.rate_line.text())
        slippage: float = float(self.slippage_line.text())
        size: float = float(self.size_line.text())
        pricetick: float = float(self.pricetick_line.text())
        capital: float = float(self.capital_line.text())

        # Check validity of vt_symbol
        if "." not in vt_symbol:
            self.write_log("本地代码缺失交易所后缀，请检查")
            return

        _, exchange_str = vt_symbol.split(".")
        if exchange_str not in Exchange.__members__:
            self.write_log("本地代码的交易所后缀不正确，请检查")
            return

        # Save backtesting parameters
        backtesting_setting: dict = {
            "class_name": class_name,
            "vt_symbol": vt_symbol,
            "interval": interval,
            "start": start.strftime("%Y-%m-%d"),
            "rate": rate,
            "slippage": slippage,
            "size": size,
            "pricetick": pricetick,
            "capital": capital
        }
        save_json(self.setting_filename, backtesting_setting)

        # Get strategy setting
        old_setting: dict = self.settings[class_name]
        dialog: BacktestingSettingEditor = BacktestingSettingEditor(class_name, old_setting)
        i: int = dialog.exec()
        if i != QtWidgets.QDialog.DialogCode.Accepted:
            return

        new_setting: dict = dialog.get_setting()
        self.settings[class_name] = new_setting

        result: bool = self.backtester_engine.start_backtesting(
            class_name,
            vt_symbol,
            interval,
            start,
            end,
            rate,
            slippage,
            size,
            pricetick,
            capital,
            new_setting
        )

        if result:
            self.statistics_monitor.clear_data()
            self.chart.clear_data()

            self.trade_button.setEnabled(False)
            self.order_button.setEnabled(False)
            self.daily_button.setEnabled(False)
            self.candle_button.setEnabled(False)

            self.trade_dialog.clear_data()
            self.order_dialog.clear_data()
            self.daily_dialog.clear_data()
            self.candle_dialog.clear_data()

    def start_optimization(self) -> None:
        """"""
        class_name: str = self.class_combo.currentText()
        vt_symbol: str = self.symbol_combo.currentText()
        interval: str = self.interval_combo.currentText()
        start: object = self.start_date_edit.dateTime().toPython()
        end: object = self.end_date_edit.dateTime().toPython()
        rate: float = float(self.rate_line.text())
        slippage: float = float(self.slippage_line.text())
        size: float = float(self.size_line.text())
        pricetick: float = float(self.pricetick_line.text())
        capital: float = float(self.capital_line.text())

        parameters: dict = self.settings[class_name]
        dialog: OptimizationSettingEditor = OptimizationSettingEditor(class_name, parameters)
        i: int = dialog.exec()
        if i != QtWidgets.QDialog.DialogCode.Accepted:
            return

        optimization_setting, use_ga, max_workers = dialog.get_setting()
        self.target_display: str = dialog.target_display

        self.backtester_engine.start_optimization(
            class_name,
            vt_symbol,
            interval,
            start,
            end,
            rate,
            slippage,
            size,
            pricetick,
            capital,
            optimization_setting,
            use_ga,
            max_workers
        )

        self.result_button.setEnabled(False)

    def start_downloading(self) -> None:
        """"""
        vt_symbol: str = self.symbol_combo.currentText()
        interval: str = self.interval_combo.currentText()
        start_date: QtCore.QDate = self.start_date_edit.date()
        end_date: QtCore.QDate = self.end_date_edit.date()

        start: datetime = datetime(
            start_date.year(),
            start_date.month(),
            start_date.day(),
        )
        start: datetime = start.replace(tzinfo=DB_TZ)

        end: datetime = datetime(
            end_date.year(),
            end_date.month(),
            end_date.day(),
            23,
            59,
            59,
        )
        end: datetime = end.replace(tzinfo=DB_TZ)

        self.backtester_engine.start_downloading(
            vt_symbol,
            interval,
            start,
            end
        )

    def show_optimization_result(self) -> None:
        """"""
        result_values: list = self.backtester_engine.get_result_values()

        dialog: OptimizationResultMonitor = OptimizationResultMonitor(
            result_values,
            self.target_display
        )
        dialog.exec()

    def show_backtesting_trades(self) -> None:
        """"""
        if not self.trade_dialog.is_updated():
            trades: List[TradeData] = self.backtester_engine.get_all_trades()
            self.trade_dialog.update_data(trades)

        self.trade_dialog.exec()

    def show_backtesting_orders(self) -> None:
        """"""
        if not self.order_dialog.is_updated():
            orders: List[OrderData] = self.backtester_engine.get_all_orders()
            self.order_dialog.update_data(orders)

        self.order_dialog.exec()

    def show_daily_results(self) -> None:
        """"""
        if not self.daily_dialog.is_updated():
            results: List[DailyResult] = self.backtester_engine.get_all_daily_results()
            self.daily_dialog.update_data(results)

        self.daily_dialog.exec()

    def show_candle_chart(self) -> None:
        """"""
        if not self.candle_dialog.is_updated():
            history: list = self.backtester_engine.get_history_data()
            self.candle_dialog.update_history(history)

            trades: List[TradeData] = self.backtester_engine.get_all_trades()
            self.candle_dialog.update_trades(trades)

        self.candle_dialog.exec()

    def edit_strategy_code(self) -> None:
        """"""
        class_name: str = self.class_combo.currentText()
        if not class_name:
            return

        file_path: str = self.backtester_engine.get_strategy_class_file(class_name)
        cmd: list = ["code", file_path]

        p: subprocess.CompletedProcess = subprocess.run(cmd, shell=True)
        if p.returncode:
            MessageBox("启动代码编辑器失败", "请检查是否安装了Visual Studio Code，并将其路径添加到了系统全局变量中！", self).exec()

    def reload_strategy_class(self) -> None:
        """"""
        self.backtester_engine.reload_strategy_class()

        current_strategy_name: str = self.class_combo.currentText()

        self.class_combo.clear()
        self.init_strategy_settings()

        ix: int = self.class_combo.findText(current_strategy_name)
        self.class_combo.setCurrentIndex(ix)

    def show(self) -> None:
        """"""
        self.showMaximized()


class StatisticsMonitor(TableWidget):
    """"""
    KEY_NAME_MAP: dict = {
        "start_date": "首个交易日",
        "end_date": "最后交易日",

        "total_days": "总交易日",
        "profit_days": "盈利交易日",
        "loss_days": "亏损交易日",

        "capital": "起始资金",
        "end_balance": "结束资金",

        "total_return": "总收益率",
        "annual_return": "年化收益",
        "max_drawdown": "最大回撤",
        "max_ddpercent": "百分比最大回撤",

        "total_net_pnl": "总盈亏",
        "total_commission": "总手续费",
        "total_slippage": "总滑点",
        "total_turnover": "总成交额",
        "total_trade_count": "总成交笔数",

        "daily_net_pnl": "日均盈亏",
        "daily_commission": "日均手续费",
        "daily_slippage": "日均滑点",
        "daily_turnover": "日均成交额",
        "daily_trade_count": "日均成交笔数",

        "daily_return": "日均收益率",
        "return_std": "收益标准差",
        "sharpe_ratio": "夏普比率",
        "return_drawdown_ratio": "收益回撤比"
    }

    def __init__(self) -> None:
        """"""
        super().__init__()

        self.cells: dict = {}

        # Apply Fluent style settings
        self.setBorderVisible(True)
        self.setBorderRadius(8)

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setRowCount(len(self.KEY_NAME_MAP))
        self.setVerticalHeaderLabels(list(self.KEY_NAME_MAP.values()))

        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        for row, key in enumerate(self.KEY_NAME_MAP.keys()):
            cell: QtWidgets.QTableWidgetItem = QtWidgets.QTableWidgetItem()
            self.setItem(row, 0, cell)
            self.cells[key] = cell

    def clear_data(self) -> None:
        """"""
        for cell in self.cells.values():
            cell.setText("")

    def set_data(self, data: dict) -> None:
        """"""
        data["capital"] = f"{data['capital']:,.2f}"
        data["end_balance"] = f"{data['end_balance']:,.2f}"
        data["total_return"] = f"{data['total_return']:,.2f}%"
        data["annual_return"] = f"{data['annual_return']:,.2f}%"
        data["max_drawdown"] = f"{data['max_drawdown']:,.2f}"
        data["max_ddpercent"] = f"{data['max_ddpercent']:,.2f}%"
        data["total_net_pnl"] = f"{data['total_net_pnl']:,.2f}"
        data["total_commission"] = f"{data['total_commission']:,.2f}"
        data["total_slippage"] = f"{data['total_slippage']:,.2f}"
        data["total_turnover"] = f"{data['total_turnover']:,.2f}"
        data["daily_net_pnl"] = f"{data['daily_net_pnl']:,.2f}"
        data["daily_commission"] = f"{data['daily_commission']:,.2f}"
        data["daily_slippage"] = f"{data['daily_slippage']:,.2f}"
        data["daily_turnover"] = f"{data['daily_turnover']:,.2f}"
        data["daily_trade_count"] = f"{data['daily_trade_count']:,.2f}"
        data["daily_return"] = f"{data['daily_return']:,.2f}%"
        data["return_std"] = f"{data['return_std']:,.2f}%"
        data["sharpe_ratio"] = f"{data['sharpe_ratio']:,.2f}"
        data["return_drawdown_ratio"] = f"{data['return_drawdown_ratio']:,.2f}"

        for key, cell in self.cells.items():
            value = data.get(key, "")
            cell.setText(str(value))


class BacktestingSettingEditor(FramelessDialog):
    """
    For creating new strategy and editing strategy parameters.
    """

    def __init__(
        self, class_name: str, parameters: dict
    ) -> None:
        """"""
        super(BacktestingSettingEditor, self).__init__()
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.class_name: str = class_name
        self.parameters: dict = parameters
        self.edits: dict = {}

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()

        # Add vt_symbol and name edit if add new strategy
        self.setWindowTitle(f"策略参数配置：{self.class_name}")
        button_text: str = "确定"
        parameters: dict = self.parameters

        for name, value in parameters.items():
            type_ = type(value)

            edit: LineEdit = LineEdit()
            edit.setText(str(value))
            if type_ is int:
                validator: QtGui.QIntValidator = QtGui.QIntValidator()
                edit.setValidator(validator)
            elif type_ is float:
                validator: QtGui.QDoubleValidator = QtGui.QDoubleValidator()
                edit.setValidator(validator)

            label: BodyLabel = BodyLabel(f"{name} {type_}")
            form.addRow(label, edit)

            self.edits[name] = (edit, type_)

        button: PushButton = PushButton(button_text)
        button.clicked.connect(self.accept)
        form.addRow(button)

        widget: QtWidgets.QWidget = QtWidgets.QWidget()
        widget.setLayout(form)

        scroll: QtWidgets.QScrollArea = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addWidget(scroll)

        # Create container for FramelessDialog content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(vbox)

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def get_setting(self) -> dict:
        """"""
        setting: dict = {}

        for name, tp in self.edits.items():
            edit, type_ = tp
            value_text = edit.text()

            if type_ == bool:
                if value_text == "True":
                    value = True
                else:
                    value = False
            else:
                value = type_(value_text)

            setting[name] = value

        return setting


class BacktesterChart(pg.GraphicsLayoutWidget):
    """"""

    def __init__(self) -> None:
        """"""
        super().__init__(title="Backtester Chart")

        self.dates: dict = {}

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        pg.setConfigOptions(antialias=True)

        # Create plot widgets
        self.balance_plot = self.addPlot(
            title="账户净值",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom")}
        )
        self.nextRow()

        self.drawdown_plot = self.addPlot(
            title="净值回撤",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom")}
        )
        self.nextRow()

        self.pnl_plot = self.addPlot(
            title="每日盈亏",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom")}
        )
        self.nextRow()

        self.distribution_plot = self.addPlot(title="盈亏分布")

        # Add curves and bars on plot widgets
        self.balance_curve = self.balance_plot.plot(
            pen=pg.mkPen("#ffc107", width=3)
        )

        dd_color: str = "#303f9f"
        self.drawdown_curve = self.drawdown_plot.plot(
            fillLevel=-0.3, brush=dd_color, pen=dd_color
        )

        profit_color: str = 'r'
        loss_color: str = 'g'
        self.profit_pnl_bar = pg.BarGraphItem(
            x=[], height=[], width=0.3, brush=profit_color, pen=profit_color
        )
        self.loss_pnl_bar = pg.BarGraphItem(
            x=[], height=[], width=0.3, brush=loss_color, pen=loss_color
        )
        self.pnl_plot.addItem(self.profit_pnl_bar)
        self.pnl_plot.addItem(self.loss_pnl_bar)

        distribution_color: str = "#6d4c41"
        self.distribution_curve = self.distribution_plot.plot(
            fillLevel=-0.3, brush=distribution_color, pen=distribution_color
        )

    def clear_data(self) -> None:
        """"""
        self.balance_curve.setData([], [])
        self.drawdown_curve.setData([], [])
        self.profit_pnl_bar.setOpts(x=[], height=[])
        self.loss_pnl_bar.setOpts(x=[], height=[])
        self.distribution_curve.setData([], [])

    def set_data(self, df) -> None:
        """"""
        if df is None:
            return

        count: int = len(df)

        self.dates.clear()
        for n, date in enumerate(df.index):
            self.dates[n] = date

        # Set data for curve of balance and drawdown
        self.balance_curve.setData(df["balance"])
        self.drawdown_curve.setData(df["drawdown"])

        # Set data for daily pnl bar
        profit_pnl_x: list = []
        profit_pnl_height: list = []
        loss_pnl_x: list = []
        loss_pnl_height: list = []

        for count, pnl in enumerate(df["net_pnl"]):
            if pnl >= 0:
                profit_pnl_height.append(pnl)
                profit_pnl_x.append(count)
            else:
                loss_pnl_height.append(pnl)
                loss_pnl_x.append(count)

        self.profit_pnl_bar.setOpts(x=profit_pnl_x, height=profit_pnl_height)
        self.loss_pnl_bar.setOpts(x=loss_pnl_x, height=loss_pnl_height)

        # Set data for pnl distribution
        hist, x = np.histogram(df["net_pnl"], bins="auto")
        x = x[:-1]
        self.distribution_curve.setData(x, hist)


class DateAxis(pg.AxisItem):
    """Axis for showing date data"""

    def __init__(self, dates: dict, *args, **kwargs) -> None:
        """"""
        super().__init__(*args, **kwargs)
        self.dates: dict = dates

    def tickStrings(self, values, scale, spacing) -> list:
        """"""
        strings: list = []
        for v in values:
            dt = self.dates.get(v, "")
            strings.append(str(dt))
        return strings


class OptimizationSettingEditor(FramelessDialog):
    """
    For setting up parameters for optimization.
    """
    DISPLAY_NAME_MAP: dict = {
        "总收益率": "total_return",
        "夏普比率": "sharpe_ratio",
        "收益回撤比": "return_drawdown_ratio",
        "日均盈亏": "daily_net_pnl"
    }

    def __init__(
        self, class_name: str, parameters: dict
    ) -> None:
        """"""
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.class_name: str = class_name
        self.parameters: dict = parameters
        self.edits: dict = {}

        self.optimization_setting: OptimizationSetting = None
        self.use_ga: bool = False

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.target_combo: ComboBox = ComboBox()
        self.target_combo.addItems(list(self.DISPLAY_NAME_MAP.keys()))

        self.worker_spin: SpinBox = SpinBox()
        self.worker_spin.setRange(0, 10000)
        self.worker_spin.setValue(0)
        self.worker_spin.setToolTip("设为0则自动根据CPU核心数启动对应数量的进程")

        grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        grid.addWidget(BodyLabel("优化目标"), 0, 0)
        grid.addWidget(self.target_combo, 0, 1, 1, 3)
        grid.addWidget(BodyLabel("进程上限"), 1, 0)
        grid.addWidget(self.worker_spin, 1, 1, 1, 3)
        grid.addWidget(BodyLabel("参数"), 2, 0)
        grid.addWidget(BodyLabel("开始"), 2, 1)
        grid.addWidget(BodyLabel("步进"), 2, 2)
        grid.addWidget(BodyLabel("结束"), 2, 3)

        # Add vt_symbol and name edit if add new strategy
        self.setWindowTitle(f"优化参数配置：{self.class_name}")

        validator: QtGui.QDoubleValidator = QtGui.QDoubleValidator()
        row: int = 3

        for name, value in self.parameters.items():
            type_ = type(value)
            if type_ not in [int, float]:
                continue

            start_edit: LineEdit = LineEdit()
            start_edit.setText(str(value))
            step_edit: LineEdit = LineEdit()
            step_edit.setText(str(1))
            end_edit: LineEdit = LineEdit()
            end_edit.setText(str(value))

            for edit in [start_edit, step_edit, end_edit]:
                edit.setValidator(validator)

            grid.addWidget(BodyLabel(name), row, 0)
            grid.addWidget(start_edit, row, 1)
            grid.addWidget(step_edit, row, 2)
            grid.addWidget(end_edit, row, 3)

            self.edits[name] = {
                "type": type_,
                "start": start_edit,
                "step": step_edit,
                "end": end_edit
            }

            row += 1

        parallel_button: PushButton = PushButton("多进程优化")
        parallel_button.clicked.connect(self.generate_parallel_setting)
        grid.addWidget(parallel_button, row, 0, 1, 4)

        row += 1
        ga_button: PushButton = PushButton("遗传算法优化")
        ga_button.clicked.connect(self.generate_ga_setting)
        grid.addWidget(ga_button, row, 0, 1, 4)

        widget: QtWidgets.QWidget = QtWidgets.QWidget()
        widget.setLayout(grid)

        scroll: QtWidgets.QScrollArea = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addWidget(scroll)

        # Create container for FramelessDialog content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(vbox)

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def generate_ga_setting(self) -> None:
        """"""
        self.use_ga: bool = True
        self.generate_setting()

    def generate_parallel_setting(self) -> None:
        """"""
        self.use_ga: bool = False
        self.generate_setting()

    def generate_setting(self) -> None:
        """"""
        self.optimization_setting = OptimizationSetting()

        self.target_display: str = self.target_combo.currentText()
        target_name: str = self.DISPLAY_NAME_MAP[self.target_display]
        self.optimization_setting.set_target(target_name)

        for name, d in self.edits.items():
            type_ = d["type"]
            start_value = type_(d["start"].text())
            step_value = type_(d["step"].text())
            end_value = type_(d["end"].text())

            if start_value == end_value:
                self.optimization_setting.add_parameter(name, start_value)
            else:
                self.optimization_setting.add_parameter(
                    name,
                    start_value,
                    end_value,
                    step_value
                )

        self.accept()

    def get_setting(self) -> Tuple[OptimizationSetting, bool, int]:
        """"""
        return self.optimization_setting, self.use_ga, self.worker_spin.value()


class OptimizationResultMonitor(FramelessDialog):
    """
    For viewing optimization result.
    """

    def __init__(
        self, result_values: list, target_display: str
    ) -> None:
        """"""
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.result_values: list = result_values
        self.target_display: str = target_display

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("参数优化结果")
        self.resize(1100, 500)

        # Creat table to show result
        table: TableWidget = TableWidget()

        table.setColumnCount(2)
        table.setRowCount(len(self.result_values))
        table.setHorizontalHeaderLabels(["参数", self.target_display])
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)

        table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )

        for n, tp in enumerate(self.result_values):
            setting, target_value, _ = tp
            setting_cell: QtWidgets.QTableWidgetItem = QtWidgets.QTableWidgetItem(str(setting))
            target_cell: QtWidgets.QTableWidgetItem = QtWidgets.QTableWidgetItem(f"{target_value:.2f}")

            setting_cell.setTextAlignment(QtCore.Qt.AlignCenter)
            target_cell.setTextAlignment(QtCore.Qt.AlignCenter)

            table.setItem(n, 0, setting_cell)
            table.setItem(n, 1, target_cell)

        # Create layout
        button: PushButton = PushButton("保存")
        button.clicked.connect(self.save_csv)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(button)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addWidget(table)
        vbox.addLayout(hbox)

        # Create container for FramelessDialog content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(vbox)

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def save_csv(self) -> None:
        """
        Save table data into a csv file
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存数据", "", "CSV(*.csv)")

        if not path:
            return

        with open(path, "w") as f:
            writer = csv.writer(f, lineterminator="\n")

            writer.writerow(["参数", self.target_display])

            for tp in self.result_values:
                setting, target_value, _ = tp
                row_data: list = [str(setting), str(target_value)]
                writer.writerow(row_data)


class BacktestingTradeMonitor(BaseMonitor):
    """
    Monitor for backtesting trade data.
    """

    headers: dict = {
        "tradeid": {"display": "成交号 ", "cell": BaseCell, "update": False},
        "orderid": {"display": "委托号", "cell": BaseCell, "update": False},
        "symbol": {"display": "代码", "cell": BaseCell, "update": False},
        "exchange": {"display": "交易所", "cell": EnumCell, "update": False},
        "direction": {"display": "方向", "cell": DirectionCell, "update": False},
        "offset": {"display": "开平", "cell": EnumCell, "update": False},
        "price": {"display": "价格", "cell": BaseCell, "update": False},
        "volume": {"display": "数量", "cell": BaseCell, "update": False},
        "datetime": {"display": "时间", "cell": BaseCell, "update": False},
        "gateway_name": {"display": "接口", "cell": BaseCell, "update": False},
    }


class BacktestingOrderMonitor(BaseMonitor):
    """
    Monitor for backtesting order data.
    """

    headers: dict = {
        "orderid": {"display": "委托号", "cell": BaseCell, "update": False},
        "symbol": {"display": "代码", "cell": BaseCell, "update": False},
        "exchange": {"display": "交易所", "cell": EnumCell, "update": False},
        "type": {"display": "类型", "cell": EnumCell, "update": False},
        "direction": {"display": "方向", "cell": DirectionCell, "update": False},
        "offset": {"display": "开平", "cell": EnumCell, "update": False},
        "price": {"display": "价格", "cell": BaseCell, "update": False},
        "volume": {"display": "总数量", "cell": BaseCell, "update": False},
        "traded": {"display": "已成交", "cell": BaseCell, "update": False},
        "status": {"display": "状态", "cell": EnumCell, "update": False},
        "datetime": {"display": "时间", "cell": BaseCell, "update": False},
        "gateway_name": {"display": "接口", "cell": BaseCell, "update": False},
    }


class FloatCell(BaseCell):
    """
    Cell used for showing pnl data.
    """

    def __init__(self, content, data) -> None:
        """"""
        content: str = f"{content:.2f}"
        super().__init__(content, data)


class DailyResultMonitor(BaseMonitor):
    """
    Monitor for backtesting daily result.
    """

    headers: dict = {
        "date": {"display": "日期", "cell": BaseCell, "update": False},
        "trade_count": {"display": "成交笔数", "cell": BaseCell, "update": False},
        "start_pos": {"display": "开盘持仓", "cell": BaseCell, "update": False},
        "end_pos": {"display": "收盘持仓", "cell": BaseCell, "update": False},
        "turnover": {"display": "成交额", "cell": FloatCell, "update": False},
        "commission": {"display": "手续费", "cell": FloatCell, "update": False},
        "slippage": {"display": "滑点", "cell": FloatCell, "update": False},
        "trading_pnl": {"display": "交易盈亏", "cell": FloatCell, "update": False},
        "holding_pnl": {"display": "持仓盈亏", "cell": FloatCell, "update": False},
        "total_pnl": {"display": "总盈亏", "cell": FloatCell, "update": False},
        "net_pnl": {"display": "净盈亏", "cell": FloatCell, "update": False},
    }


class BacktestingResultDialog(FramelessDialog):
    """"""

    def __init__(
        self,
        main_engine: MainEngine,
        event_engine: EventEngine,
        title: str,
        table_class: TableWidget
    ) -> None:
        """"""
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine
        self.title: str = title
        self.table_class: TableWidget = table_class

        self.updated: bool = False

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle(self.title)
        self.resize(1100, 600)

        self.table: TableWidget = self.table_class(self.main_engine, self.event_engine)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.table)

        # Create container for FramelessDialog content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(vbox)

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def clear_data(self) -> None:
        """"""
        self.updated = False
        self.table.setRowCount(0)

    def update_data(self, data: list) -> None:
        """"""
        self.updated = True

        data.reverse()
        for obj in data:
            self.table.insert_new_row(obj)

    def is_updated(self) -> bool:
        """"""
        return self.updated


class CandleChartDialog(FramelessDialog):
    """"""

    def __init__(self) -> None:
        """"""
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.updated: bool = False

        self.dt_ix_map: dict = {}
        self.ix_bar_map: dict = {}

        self.high_price = 0
        self.low_price = 0
        self.price_range = 0

        self.items: list = []
        self.text_items: list = []  # Store text items separately for easy removal

        # Flag to control position number display
        self.show_position_numbers: bool = True
        # Flag to control extra field display
        self.show_extra_fields: bool = False
        self.current_trades: list = []  # Store trades for redrawing
        self.current_history: list = []  # Store history for redrawing
        self.extra_text_items: list = []  # Store extra text items separately for easy removal

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("回测K线图表")
        self.resize(1400, 800)

        # Create toolbar for controls (above chart)
        toolbar: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        
        # Add checkbox to toggle position number display
        self.show_position_checkbox: QtWidgets.QCheckBox = QtWidgets.QCheckBox()
        self.show_position_checkbox.setText("显示仓位数字")
        self.show_position_checkbox.setChecked(True)  # Default: show
        self.show_position_checkbox.toggled.connect(self.on_toggle_position_numbers)
        self.show_position_checkbox.setStyleSheet("QCheckBox { font-size: 12px; padding: 5px; }")
        
        # Add checkbox to toggle extra field display
        self.show_extra_checkbox: QtWidgets.QCheckBox = QtWidgets.QCheckBox()
        self.show_extra_checkbox.setText("显示额外字段")
        self.show_extra_checkbox.setChecked(False)  # Default: hide
        self.show_extra_checkbox.toggled.connect(self.on_toggle_extra_fields)
        self.show_extra_checkbox.setStyleSheet("QCheckBox { font-size: 12px; padding: 5px; }")
        
        toolbar.addWidget(self.show_position_checkbox)
        toolbar.addWidget(self.show_extra_checkbox)
        toolbar.addStretch()

        # Create chart widget
        self.chart: ChartWidget = ChartWidget()
        self.chart.add_plot("candle", hide_x_axis=True)
        self.chart.add_plot("volume", maximum_height=200)
        self.chart.add_item(CandleItem, "candle", "candle")
        self.chart.add_item(VolumeItem, "volume", "volume")
        self.chart.add_cursor()

        # Create help widget
        text1: str = "红色虚线 —— 盈利交易"
        label1: BodyLabel = BodyLabel(text1)
        label1.setStyleSheet("color:red")

        text2: str = "绿色虚线 —— 亏损交易"
        label2: BodyLabel = BodyLabel(text2)
        label2.setStyleSheet("color:#00FF00")

        text3: str = "黄色向上箭头 —— 买入开仓 Buy"
        label3: BodyLabel = BodyLabel(text3)
        label3.setStyleSheet("color:yellow")

        text4: str = "黄色向下箭头 —— 卖出平仓 Sell"
        label4: BodyLabel = BodyLabel(text4)
        label4.setStyleSheet("color:yellow")

        text5: str = "紫红向下箭头 —— 卖出开仓 Short"
        label5: BodyLabel = BodyLabel(text5)
        label5.setStyleSheet("color:magenta")

        text6: str = "紫红向上箭头 —— 买入平仓 Cover"
        label6: BodyLabel = BodyLabel(text6)
        label6.setStyleSheet("color:magenta")

        hbox1: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox1.addStretch()
        hbox1.addWidget(label1)
        hbox1.addStretch()
        hbox1.addWidget(label2)
        hbox1.addStretch()

        hbox2: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox2.addStretch()
        hbox2.addWidget(label3)
        hbox2.addStretch()
        hbox2.addWidget(label4)
        hbox2.addStretch()

        hbox3: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox3.addStretch()
        hbox3.addWidget(label5)
        hbox3.addStretch()
        hbox3.addWidget(label6)
        hbox3.addStretch()

        # Set layout
        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addLayout(toolbar)  # Add toolbar at the top
        vbox.addWidget(self.chart)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        # Create container for FramelessDialog content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(vbox)

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def update_history(self, history: list) -> None:
        """"""
        self.current_history = history  # Store history for redrawing
        self.updated = True
        self.chart.update_history(history)

        for ix, bar in enumerate(history):
            self.ix_bar_map[ix] = bar
            self.dt_ix_map[bar.datetime] = ix

            if not self.high_price:
                self.high_price = bar.high_price
                self.low_price = bar.low_price
            else:
                self.high_price = max(self.high_price, bar.high_price)
                self.low_price = min(self.low_price, bar.low_price)

        self.price_range = self.high_price - self.low_price

    def update_trades(self, trades: list) -> None:
        """"""
        self.current_trades = trades  # Store trades for redrawing
        trade_pairs: list = generate_trade_pairs(trades)

        candle_plot: pg.PlotItem = self.chart.get_plot("candle")

        scatter_data: list = []

        y_adjustment: float = self.price_range * 0.001

        for d in trade_pairs:
            open_ix = self.dt_ix_map[d["open_dt"]]
            close_ix = self.dt_ix_map[d["close_dt"]]
            open_price = d["open_price"]
            close_price = d["close_price"]

            # Trade Line
            x: list = [open_ix, close_ix]
            y: list = [open_price, close_price]

            if d["direction"] == Direction.LONG and close_price >= open_price:
                color: str = "r"
            elif d["direction"] == Direction.SHORT and close_price <= open_price:
                color: str = "r"
            else:
                color: str = "g"

            pen: QtGui.QPen = pg.mkPen(color, width=1.5, style=QtCore.Qt.DashLine)
            item: pg.PlotCurveItem = pg.PlotCurveItem(x, y, pen=pen)

            self.items.append(item)
            candle_plot.addItem(item)

            # Trade Scatter
            open_bar: BarData = self.ix_bar_map[open_ix]
            close_bar: BarData = self.ix_bar_map[close_ix]

            if d["direction"] == Direction.LONG:
                scatter_color: str = "yellow"
                open_symbol: str = "t1"
                close_symbol: str = "t"
                open_side: int = 1
                close_side: int = -1
                open_y: float = open_bar.low_price
                close_y: float = close_bar.high_price
            else:
                scatter_color: str = "magenta"
                open_symbol: str = "t"
                close_symbol: str = "t1"
                open_side: int = -1
                close_side: int = 1
                open_y: float = open_bar.high_price
                close_y: float = close_bar.low_price

            pen = pg.mkPen(QtGui.QColor(scatter_color))
            brush: QtGui.QBrush = pg.mkBrush(QtGui.QColor(scatter_color))
            size: int = 10

            open_scatter: dict = {
                "pos": (open_ix, open_y - open_side * y_adjustment),
                "size": size,
                "pen": pen,
                "brush": brush,
                "symbol": open_symbol
            }

            close_scatter: dict = {
                "pos": (close_ix, close_y - close_side * y_adjustment),
                "size": size,
                "pen": pen,
                "brush": brush,
                "symbol": close_symbol
            }

            scatter_data.append(open_scatter)
            scatter_data.append(close_scatter)

            # Trade text (only if show_position_numbers is True)
            text_offset_multiplier = 3  # Offset multiplier for position numbers
            if self.show_position_numbers:
                volume = d["volume"]
                text_color: QtGui.QColor = QtGui.QColor(scatter_color)
                open_text: pg.TextItem = pg.TextItem(f"[{volume}]", color=text_color, anchor=(0.5, 0.5))
                close_text: pg.TextItem = pg.TextItem(f"[{volume}]", color=text_color, anchor=(0.5, 0.5))

                open_text.setPos(open_ix, open_y - open_side * y_adjustment * text_offset_multiplier)
                close_text.setPos(close_ix, close_y - close_side * y_adjustment * text_offset_multiplier)

                self.items.append(open_text)
                self.items.append(close_text)
                self.text_items.append(open_text)  # Store separately for easy removal
                self.text_items.append(close_text)

                candle_plot.addItem(open_text)
                candle_plot.addItem(close_text)
                text_offset_multiplier += 1  # Increase offset for extra fields
            
            # Extra fields text (only if show_extra_fields is True)
            if self.show_extra_fields:
                # Display open extra
                open_extra = d.get("open_extra")
                if open_extra:
                    extra_text = str(open_extra)  # Convert dict to string for display
                    extra_text_color: QtGui.QColor = QtGui.QColor(scatter_color)
                    open_extra_text: pg.TextItem = pg.TextItem(extra_text, color=extra_text_color, anchor=(0.5, 0.5))
                    open_extra_text.setPos(open_ix, open_y - open_side * y_adjustment * text_offset_multiplier)
                    
                    self.items.append(open_extra_text)
                    self.extra_text_items.append(open_extra_text)
                    candle_plot.addItem(open_extra_text)
                
                # Display close extra
                close_extra = d.get("close_extra")
                if close_extra:
                    extra_text = str(close_extra)  # Convert dict to string for display
                    extra_text_color: QtGui.QColor = QtGui.QColor(scatter_color)
                    close_extra_text: pg.TextItem = pg.TextItem(extra_text, color=extra_text_color, anchor=(0.5, 0.5))
                    close_extra_text.setPos(close_ix, close_y - close_side * y_adjustment * text_offset_multiplier)
                    
                    self.items.append(close_extra_text)
                    self.extra_text_items.append(close_extra_text)
                    candle_plot.addItem(close_extra_text)

        trade_scatter: pg.ScatterPlotItem = pg.ScatterPlotItem(scatter_data)
        self.items.append(trade_scatter)
        candle_plot.addItem(trade_scatter)

    def clear_data(self) -> None:
        """"""
        self.updated = False

        candle_plot: pg.PlotItem = self.chart.get_plot("candle")
        for item in self.items:
            candle_plot.removeItem(item)
        self.items.clear()
        self.text_items.clear()  # Clear text items list
        self.extra_text_items.clear()  # Clear extra text items list

        self.chart.clear_all()

        self.dt_ix_map.clear()
        self.ix_bar_map.clear()

    def on_toggle_position_numbers(self, checked: bool) -> None:
        """
        Handle checkbox toggle for position number display.

        Args:
            checked: Whether to show position numbers
        """
        self.show_position_numbers = checked

        # If trades are already displayed, update text items visibility
        if self.current_trades and self.updated:
            candle_plot: pg.PlotItem = self.chart.get_plot("candle")

            if checked:
                # Show text items: need to redraw trades to add text items
                # Remove existing text items first
                for text_item in self.text_items[:]:  # Copy list to avoid modification during iteration
                    if text_item in self.items:
                        candle_plot.removeItem(text_item)
                        self.items.remove(text_item)
                self.text_items.clear()

                # Redraw trades to add text items back
                trade_pairs: list = generate_trade_pairs(self.current_trades)
                y_adjustment: float = self.price_range * 0.001

                for d in trade_pairs:
                    open_ix = self.dt_ix_map[d["open_dt"]]
                    close_ix = self.dt_ix_map[d["close_dt"]]
                    
                    open_bar: BarData = self.ix_bar_map[open_ix]
                    close_bar: BarData = self.ix_bar_map[close_ix]

                    if d["direction"] == Direction.LONG:
                        scatter_color: str = "yellow"
                        open_side: int = 1
                        close_side: int = -1
                        open_y: float = open_bar.low_price
                        close_y: float = close_bar.high_price
                    else:
                        scatter_color: str = "magenta"
                        open_side: int = -1
                        close_side: int = 1
                        open_y: float = open_bar.high_price
                        close_y: float = close_bar.low_price

                    volume = d["volume"]
                    text_color: QtGui.QColor = QtGui.QColor(scatter_color)
                    open_text: pg.TextItem = pg.TextItem(f"[{volume}]", color=text_color, anchor=(0.5, 0.5))
                    close_text: pg.TextItem = pg.TextItem(f"[{volume}]", color=text_color, anchor=(0.5, 0.5))

                    open_text.setPos(open_ix, open_y - open_side * y_adjustment * 3)
                    close_text.setPos(close_ix, close_y - close_side * y_adjustment * 3)

                    self.items.append(open_text)
                    self.items.append(close_text)
                    self.text_items.append(open_text)
                    self.text_items.append(close_text)

                    candle_plot.addItem(open_text)
                    candle_plot.addItem(close_text)
            else:
                # Hide text items: remove all text items
                for text_item in self.text_items[:]:  # Copy list to avoid modification during iteration
                    if text_item in self.items:
                        candle_plot.removeItem(text_item)
                        self.items.remove(text_item)
                self.text_items.clear()

    def on_toggle_extra_fields(self, checked: bool) -> None:
        """
        Handle checkbox toggle for extra field display.

        Args:
            checked: Whether to show extra fields
        """
        self.show_extra_fields = checked

        # If trades are already displayed, update extra field visibility
        if self.current_trades and self.updated:
            candle_plot: pg.PlotItem = self.chart.get_plot("candle")

            if checked:
                # Show extra fields: need to redraw trades to add extra text items
                # Remove existing extra text items first
                for extra_text_item in self.extra_text_items[:]:  # Copy list to avoid modification during iteration
                    if extra_text_item in self.items:
                        candle_plot.removeItem(extra_text_item)
                        self.items.remove(extra_text_item)
                self.extra_text_items.clear()

                # Redraw trades to add extra text items back
                trade_pairs: list = generate_trade_pairs(self.current_trades)
                y_adjustment: float = self.price_range * 0.001
                text_offset_multiplier = 4 if self.show_position_numbers else 3  # Start after position numbers if shown

                for d in trade_pairs:
                    open_ix = self.dt_ix_map[d["open_dt"]]
                    close_ix = self.dt_ix_map[d["close_dt"]]
                    
                    open_bar: BarData = self.ix_bar_map[open_ix]
                    close_bar: BarData = self.ix_bar_map[close_ix]

                    if d["direction"] == Direction.LONG:
                        scatter_color: str = "yellow"
                        open_side: int = 1
                        close_side: int = -1
                        open_y: float = open_bar.low_price
                        close_y: float = close_bar.high_price
                    else:
                        scatter_color: str = "magenta"
                        open_side: int = -1
                        close_side: int = 1
                        open_y: float = open_bar.high_price
                        close_y: float = close_bar.low_price

                    # Display open extra
                    open_extra = d.get("open_extra")
                    if open_extra:
                        extra_text = str(open_extra)  # Convert dict to string for display
                        extra_text_color: QtGui.QColor = QtGui.QColor(scatter_color)
                        open_extra_text: pg.TextItem = pg.TextItem(extra_text, color=extra_text_color, anchor=(0.5, 0.5))
                        open_extra_text.setPos(open_ix, open_y - open_side * y_adjustment * text_offset_multiplier)
                        
                        self.items.append(open_extra_text)
                        self.extra_text_items.append(open_extra_text)
                        candle_plot.addItem(open_extra_text)

                    # Display close extra
                    close_extra = d.get("close_extra")
                    if close_extra:
                        extra_text = str(close_extra)  # Convert dict to string for display
                        extra_text_color: QtGui.QColor = QtGui.QColor(scatter_color)
                        close_extra_text: pg.TextItem = pg.TextItem(extra_text, color=extra_text_color, anchor=(0.5, 0.5))
                        close_extra_text.setPos(close_ix, close_y - close_side * y_adjustment * text_offset_multiplier)
                        
                        self.items.append(close_extra_text)
                        self.extra_text_items.append(close_extra_text)
                        candle_plot.addItem(close_extra_text)
            else:
                # Hide extra text items: remove all extra text items
                for extra_text_item in self.extra_text_items[:]:  # Copy list to avoid modification during iteration
                    if extra_text_item in self.items:
                        candle_plot.removeItem(extra_text_item)
                        self.items.remove(extra_text_item)
                self.extra_text_items.clear()

    def is_updated(self) -> bool:
        """"""
        return self.updated


def generate_trade_pairs(trades: list) -> list:
    """
    Generate trade pairs from trade list.
    
    Note: In futures trading:
    - Open long: Direction.LONG, Offset.OPEN
    - Close long: Direction.SHORT, Offset.CLOSE (direction is opposite to close)
    - Open short: Direction.SHORT, Offset.OPEN
    - Close short: Direction.LONG, Offset.CLOSE (direction is opposite to close)
    
    The matching logic:
    - OPEN trades are added to the position list of their direction
    - CLOSE trades are matched with OPEN trades of the OPPOSITE direction
      (because close direction is opposite to open direction)
    """
    long_trades: list = []  # Unclosed LONG positions (Direction.LONG, Offset.OPEN)
    short_trades: list = []  # Unclosed SHORT positions (Direction.SHORT, Offset.OPEN)
    trade_pairs: list = []

    for trade in trades:
        trade: TradeData = copy(trade)

        # Only process OPEN trades as positions, CLOSE trades should match positions
        if trade.offset == Offset.OPEN:
            # This is an opening trade, add to the position list
            if trade.direction == Direction.LONG:
                long_trades.append(trade)
            else:  # Direction.SHORT
                short_trades.append(trade)
        elif trade.offset == Offset.CLOSE:
            # This is a closing trade, match with opposite direction positions
            # Close LONG: Direction.SHORT, Offset.CLOSE -> match with long_trades
            # Close SHORT: Direction.LONG, Offset.CLOSE -> match with short_trades
            if trade.direction == Direction.LONG:
                # Closing SHORT positions (Direction.LONG, Offset.CLOSE)
                opposite_direction: list = short_trades
            else:  # trade.direction == Direction.SHORT
                # Closing LONG positions (Direction.SHORT, Offset.CLOSE)
                opposite_direction: list = long_trades

            # Match with unclosed positions (LIFO: Last In First Out)
            while trade.volume and opposite_direction:
                open_trade: TradeData = opposite_direction[-1]

                close_volume = min(open_trade.volume, trade.volume)
                d: dict = {
                    "open_dt": open_trade.datetime,
                    "open_price": open_trade.price,
                    "close_dt": trade.datetime,
                    "close_price": trade.price,
                    "direction": open_trade.direction,  # Use open_trade's direction (the actual position direction)
                    "volume": close_volume,
                    # Add extra information from trade objects
                    "open_extra": open_trade.extra if hasattr(open_trade, 'extra') and open_trade.extra else None,
                    "close_extra": trade.extra if hasattr(trade, 'extra') and trade.extra else None,
                }
                trade_pairs.append(d)

                open_trade.volume -= close_volume
                if not open_trade.volume:
                    opposite_direction.pop(-1)

                trade.volume -= close_volume
            
            # If there's remaining volume after matching, it means there's no position to close
            # This might be a data issue, but we'll ignore it
        # If offset is NONE or other, ignore it (shouldn't happen in normal backtesting)

    return trade_pairs
