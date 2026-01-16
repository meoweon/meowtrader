from functools import partial
from datetime import datetime, timedelta
import re

from vnpy.trader.ui import QtWidgets, QtCore
from vnpy.trader.engine import MainEngine, EventEngine
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.object import BarData
from vnpy.trader.database import DB_TZ
from vnpy.trader.utility import available_timezones
from qfluentwidgets import (
    PushButton, ComboBox, LineEdit, BodyLabel, TableWidget, DateEdit, CheckBox, MessageBox
)
from qframelesswindow import FramelessDialog, FramelessWindow
from qframelesswindow.titlebar import StandardTitleBar
from vnpy.trader.ui import QtGui

from ..engine import APP_NAME, ManagerEngine, BarOverview


INTERVAL_NAME_MAP = {
    Interval.MINUTE: "分钟线",
    Interval.HOUR: "小时线",
    Interval.DAILY: "日线",
}


class ManagerWidget(FramelessWindow):
    """"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        # Set up Fluent-style title bar
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background for Fluent theme
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.engine: ManagerEngine = main_engine.get_engine(APP_NAME)
        self.download_dialogs: list = []  # 支持多个下载对话框

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("数据管理")

        self.init_tree()
        self.init_table()

        refresh_button: PushButton = PushButton("刷新")
        refresh_button.clicked.connect(self.refresh_tree)

        import_button: PushButton = PushButton("导入数据")
        import_button.clicked.connect(self.import_data)

        update_button: PushButton = PushButton("更新数据")
        update_button.clicked.connect(self.update_data)

        download_button: PushButton = PushButton("下载数据")
        download_button.clicked.connect(self.download_data)

        hbox1: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox1.addWidget(refresh_button)
        hbox1.addStretch()
        hbox1.addWidget(import_button)
        hbox1.addWidget(update_button)
        hbox1.addWidget(download_button)

        hbox2: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.tree)
        hbox2.addWidget(self.table)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        # Create container widget for FramelessWindow content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(vbox)

        # Main layout with title bar margin
        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def init_tree(self) -> None:
        """"""
        labels: list = [
            "数据",
            "本地代码",
            "代码",
            "交易所",
            "数据量",
            "开始时间",
            "结束时间",
            "",
            "",
            "",
            ""
        ]

        self.tree: QtWidgets.QTreeWidget = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(len(labels))
        self.tree.setHeaderLabels(labels)
        # Set dark theme style for tree widget
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: rgb(32, 32, 32);
                color: white;
                border: 1px solid rgb(60, 60, 60);
            }
            QTreeWidget::item {
                color: white;
            }
            QTreeWidget::item:selected {
                background-color: rgb(60, 60, 60);
            }
            QHeaderView::section {
                background-color: rgb(45, 45, 45);
                color: white;
                border: 1px solid rgb(60, 60, 60);
                padding: 4px;
            }
        """)

    def init_table(self) -> None:
        """"""
        labels: list = [
            "时间",
            "开盘价",
            "最高价",
            "最低价",
            "收盘价",
            "成交量",
            "成交额",
            "持仓量"
        ]

        self.table: TableWidget = TableWidget()
        self.table.setColumnCount(len(labels))
        self.table.setHorizontalHeaderLabels(labels)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )

    def refresh_tree(self) -> None:
        """"""
        self.tree.clear()

        # 初始化节点缓存字典
        interval_childs: dict[Interval, QtWidgets.QTreeWidgetItem] = {}
        exchange_childs: dict[tuple[Interval, Exchange], QtWidgets.QTreeWidgetItem] = {}

        # 查询数据汇总，并基于合约代码进行排序
        overviews: list[BarOverview] = self.engine.get_bar_overview()
        overviews.sort(key=lambda x: x.symbol)

        # 添加数据周期节点
        for interval in [Interval.MINUTE, Interval.HOUR, Interval.DAILY]:
            interval_child = QtWidgets.QTreeWidgetItem()
            interval_childs[interval] = interval_child

            interval_name: str = INTERVAL_NAME_MAP[interval]
            interval_child.setText(0, interval_name)

        # 遍历添加数据节点
        for overview in overviews:
            # 获取交易所节点
            key: tuple = (overview.interval, overview.exchange)
            exchange_child: QtWidgets.QTreeWidgetItem = exchange_childs.get(key, None)

            if not exchange_child:
                interval_child = interval_childs[overview.interval]

                exchange_child = QtWidgets.QTreeWidgetItem(interval_child)
                exchange_child.setText(0, overview.exchange.value)

                exchange_childs[key] = exchange_child

            #  创建数据节点
            item = QtWidgets.QTreeWidgetItem(exchange_child)

            item.setText(1, f"{overview.symbol}.{overview.exchange.value}")
            item.setText(2, overview.symbol)
            item.setText(3, overview.exchange.value)
            item.setText(4, str(overview.count))
            item.setText(5, overview.start.strftime("%Y-%m-%d %H:%M:%S"))
            item.setText(6, overview.end.strftime("%Y-%m-%d %H:%M:%S"))

            output_button: PushButton = PushButton("导出")
            output_func = partial(
                self.output_data,
                overview.symbol,
                overview.exchange,
                overview.interval,
                overview.start,
                overview.end
            )
            output_button.clicked.connect(output_func)

            update_button: PushButton = PushButton("更新")
            update_func = partial(
                self.update_single_data,
                overview.symbol,
                overview.exchange,
                overview.interval,
                overview.end
            )
            update_button.clicked.connect(update_func)

            show_button: PushButton = PushButton("查看")
            show_func = partial(
                self.show_data,
                overview.symbol,
                overview.exchange,
                overview.interval,
                overview.start,
                overview.end
            )
            show_button.clicked.connect(show_func)

            delete_button: PushButton = PushButton("删除")
            delete_func = partial(
                self.delete_data,
                overview.symbol,
                overview.exchange,
                overview.interval
            )
            delete_button.clicked.connect(delete_func)

            self.tree.setItemWidget(item, 7, show_button)
            self.tree.setItemWidget(item, 8, output_button)
            self.tree.setItemWidget(item, 9, update_button)
            self.tree.setItemWidget(item, 10, delete_button)

        # 展开顶层节点
        self.tree.addTopLevelItems(list(interval_childs.values()))

        for interval_child in interval_childs.values():
            interval_child.setExpanded(True)

    def import_data(self) -> None:
        """"""
        dialog: ImportDialog = ImportDialog()
        n: int = dialog.exec()
        if n != QtWidgets.QDialog.DialogCode.Accepted:
            return

        file_path: str = dialog.file_edit.text()
        symbol: str = dialog.symbol_edit.text()
        exchange = dialog.exchange_combo.currentData()
        interval = dialog.interval_combo.currentData()
        tz_name: str = dialog.tz_combo.currentText()
        datetime_head: str = dialog.datetime_edit.text()
        open_head: str = dialog.open_edit.text()
        low_head: str = dialog.low_edit.text()
        high_head: str = dialog.high_edit.text()
        close_head: str = dialog.close_edit.text()
        volume_head: str = dialog.volume_edit.text()
        turnover_head: str = dialog.turnover_edit.text()
        open_interest_head: str = dialog.open_interest_edit.text()
        datetime_format: str = dialog.format_edit.text()

        start, end, count = self.engine.import_data_from_csv(
            file_path,
            symbol,
            exchange,
            interval,
            tz_name,
            datetime_head,
            open_head,
            high_head,
            low_head,
            close_head,
            volume_head,
            turnover_head,
            open_interest_head,
            datetime_format
        )

        msg: str = f"\
        CSV载入成功\n\
        代码：{symbol}\n\
        交易所：{exchange.value}\n\
        周期：{interval.value}\n\
        起始：{start}\n\
        结束：{end}\n\
        总数量：{count}\n\
        "
        MessageBox("载入成功！", msg, self).exec()

    def output_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> None:
        """"""
        # Get output date range
        dialog: DateRangeDialog = DateRangeDialog(start, end)
        n: int = dialog.exec()
        if n != QtWidgets.QDialog.DialogCode.Accepted:
            return
        start, end = dialog.get_date_range()

        # Get output file path
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "导出数据",
            "",
            "CSV(*.csv)"
        )
        if not path:
            return

        result: bool = self.engine.output_data_to_csv(
            path,
            symbol,
            exchange,
            interval,
            start,
            end
        )

        if not result:
            MessageBox("导出失败！", "该文件已在其他程序中打开，请关闭相关程序后再尝试导出数据。", self).exec()

    def show_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> None:
        """"""
        # Get output date range
        dialog: DateRangeDialog = DateRangeDialog(start, end)
        n: int = dialog.exec()
        if n != QtWidgets.QDialog.DialogCode.Accepted:
            return
        start, end = dialog.get_date_range()

        bars: list[BarData] = self.engine.load_bar_data(
            symbol,
            exchange,
            interval,
            start,
            end
        )

        self.table.setRowCount(0)
        self.table.setRowCount(len(bars))

        for row, bar in enumerate(bars):
            self.table.setItem(row, 0, DataCell(bar.datetime.strftime("%Y-%m-%d %H:%M:%S")))
            self.table.setItem(row, 1, DataCell(str(bar.open_price)))
            self.table.setItem(row, 2, DataCell(str(bar.high_price)))
            self.table.setItem(row, 3, DataCell(str(bar.low_price)))
            self.table.setItem(row, 4, DataCell(str(bar.close_price)))
            self.table.setItem(row, 5, DataCell(str(bar.volume)))
            self.table.setItem(row, 6, DataCell(str(bar.turnover)))
            self.table.setItem(row, 7, DataCell(str(bar.open_interest)))

    def delete_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval
    ) -> None:
        """"""
        reply = MessageBox("删除确认", f"请确认是否要删除{symbol} {exchange.value} {interval.value}的全部数据", self)
        if not reply.exec():
            return

        count: int = self.engine.delete_bar_data(
            symbol,
            exchange,
            interval
        )

        MessageBox("删除成功", f"已删除{symbol} {exchange.value} {interval.value}共计{count}条数据", self).exec()

    def update_data(self) -> None:
        """"""
        overviews: list[BarOverview] = self.engine.get_bar_overview()
        total: int = len(overviews)
        count: int = 0

        dialog: QtWidgets.QProgressDialog = QtWidgets.QProgressDialog(
            "历史数据更新中",
            "取消",
            0,
            100
        )
        dialog.setWindowTitle("更新进度")
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        dialog.setValue(0)

        for overview in overviews:
            if dialog.wasCanceled():
                break

            self.engine.download_bar_data(
                overview.symbol,
                overview.exchange,
                overview.interval.value,
                overview.end,
                self.output,
                end=None,
                skip_existing=True
            )
            count += 1
            progress = int(round(count / total * 100, 0))
            dialog.setValue(progress)

        dialog.close()

    def update_single_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime
    ) -> None:
        """更新单个数据项，从已有数据的结束时间开始下载到当前时间"""
        # 确认对话框
        reply = MessageBox("更新确认", f"确认要更新 {symbol} {exchange.value} {interval.value} 的数据吗？\n"
            f"将从 {start.strftime('%Y-%m-%d %H:%M:%S')} 开始下载到当前时间。", self)
        if not reply.exec():
            return
        
        # 执行更新
        try:
            count = self.engine.download_bar_data(
                symbol,
                exchange,
                interval.value,
                start,
                self.output,
                end=None,
                skip_existing=True
            )
            MessageBox("更新完成", f"已更新 {symbol} {exchange.value} {interval.value} 的数据，共下载 {count} 条K线", self).exec()
            # 刷新树以显示更新后的数据
            self.refresh_tree()
        except Exception as e:
            MessageBox("更新失败", f"更新数据时出错：{str(e)}", self).exec()

    def download_data(self) -> None:
        """"""
        # 创建新的下载对话框，允许同时打开多个
        dialog = DownloadDialog(self.engine, self)
        self.download_dialogs.append(dialog)
        # 使用destroyed信号来清理列表中的引用
        dialog.destroyed.connect(lambda obj: self._on_dialog_destroyed())
        dialog.show()  # 使用 show() 而非 exec_()，允许切换到其他窗口
    
    def _on_dialog_destroyed(self) -> None:
        """对话框被销毁时的回调，清理已销毁的对话框引用"""
        # 简单清理：移除None引用和检查widget是否存在
        # 由于Qt会自动管理widget的生命周期，我们只需要定期清理即可
        # 这里简化处理，因为WA_DeleteOnClose会自动清理
        self.download_dialogs = [d for d in self.download_dialogs if d is not None]

    def show(self) -> None:
        """"""
        self.showMaximized()

    def output(self, msg: str) -> None:
        """输出下载过程中的日志"""
        MessageBox("数据下载", msg, self).exec()


class DataCell(QtWidgets.QTableWidgetItem):
    """"""

    def __init__(self, text: str = "") -> None:
        super().__init__(text)

        self.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


class DateRangeDialog(FramelessDialog):
    """"""

    def __init__(self, start: datetime, end: datetime, parent: QtWidgets.QWidget | None = None) -> None:
        """"""
        super().__init__(parent)
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.setWindowTitle("选择数据区间")

        self.start_edit: DateEdit = DateEdit()
        self.start_edit.setDate(QtCore.QDate(
            start.year,
            start.month,
            start.day + 1
        ))
        self.end_edit: DateEdit = DateEdit()
        self.end_edit.setDate(QtCore.QDate(
            end.year,
            end.month,
            end.day + 1
        ))

        button: PushButton = PushButton("确定")
        button.clicked.connect(self.accept)

        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form.addRow(BodyLabel("开始时间"), self.start_edit)
        form.addRow(BodyLabel("结束时间"), self.end_edit)
        form.addRow(button)

        # Create container for FramelessDialog content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(form)

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def get_date_range(self) -> tuple[datetime, datetime]:
        """"""
        start = self.start_edit.dateTime().toPython()
        end = self.end_edit.dateTime().toPython() + timedelta(days=1)
        return start, end


class ImportDialog(FramelessDialog):
    """"""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """"""
        super().__init__(parent)
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.setWindowTitle("从CSV文件导入数据")
        self.setFixedWidth(300)

        file_button: PushButton = PushButton("选择文件")
        file_button.clicked.connect(self.select_file)

        load_button: PushButton = PushButton("确定")
        load_button.clicked.connect(self.accept)

        self.file_edit: LineEdit = LineEdit()
        self.symbol_edit: LineEdit = LineEdit()
        self.symbol_edit.setText("BTCUSDT_SPOT_OKX")  # 默认代码

        self.exchange_combo: ComboBox = ComboBox()
        for i in Exchange:
            self.exchange_combo.addItem(str(i.name))
            index = self.exchange_combo.count() - 1
            self.exchange_combo.setItemData(index, i)
            self.exchange_combo.setItemIcon(index, QtGui.QIcon())

        # 新增这一行：默认选中 GLOBAL
        ix = self.exchange_combo.findData(Exchange.GLOBAL)
        if ix >= 0:
            self.exchange_combo.setCurrentIndex(ix)

        self.interval_combo: ComboBox = ComboBox()
        for i in Interval:
            if i != Interval.TICK:
                self.interval_combo.addItem(str(i.name))
                index = self.interval_combo.count() - 1
                self.interval_combo.setItemData(index, i)
                self.interval_combo.setItemIcon(index, QtGui.QIcon())

        self.tz_combo: ComboBox = ComboBox()
        self.tz_combo.addItems(available_timezones())
        self.tz_combo.setCurrentIndex(self.tz_combo.findText("Asia/Shanghai"))

        self.datetime_edit: LineEdit = LineEdit()
        self.datetime_edit.setText("datetime")
        self.open_edit: LineEdit = LineEdit()
        self.open_edit.setText("open")
        self.high_edit: LineEdit = LineEdit()
        self.high_edit.setText("high")
        self.low_edit: LineEdit = LineEdit()
        self.low_edit.setText("low")
        self.close_edit: LineEdit = LineEdit()
        self.close_edit.setText("close")
        self.volume_edit: LineEdit = LineEdit()
        self.volume_edit.setText("volume")
        self.turnover_edit: LineEdit = LineEdit()
        self.turnover_edit.setText("turnover")
        self.open_interest_edit: LineEdit = LineEdit()
        self.open_interest_edit.setText("open_interest")

        self.format_edit: LineEdit = LineEdit()
        self.format_edit.setText("%Y-%m-%d %H:%M:%S")

        info_label: BodyLabel = BodyLabel("合约信息")
        info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        head_label: BodyLabel = BodyLabel("表头信息")
        head_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        format_label: BodyLabel = BodyLabel("格式信息")
        format_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form.addRow(file_button, self.file_edit)
        form.addRow(BodyLabel())
        form.addRow(info_label)
        form.addRow(BodyLabel("代码"), self.symbol_edit)
        form.addRow(BodyLabel("交易所"), self.exchange_combo)
        form.addRow(BodyLabel("周期"), self.interval_combo)
        form.addRow(BodyLabel("时区"), self.tz_combo)
        form.addRow(BodyLabel())
        form.addRow(head_label)
        form.addRow(BodyLabel("时间戳"), self.datetime_edit)
        form.addRow(BodyLabel("开盘价"), self.open_edit)
        form.addRow(BodyLabel("最高价"), self.high_edit)
        form.addRow(BodyLabel("最低价"), self.low_edit)
        form.addRow(BodyLabel("收盘价"), self.close_edit)
        form.addRow(BodyLabel("成交量"), self.volume_edit)
        form.addRow(BodyLabel("成交额"), self.turnover_edit)
        form.addRow(BodyLabel("持仓量"), self.open_interest_edit)
        form.addRow(BodyLabel())
        form.addRow(format_label)
        form.addRow(BodyLabel("时间格式"), self.format_edit)
        form.addRow(BodyLabel())
        form.addRow(load_button)

        # Create container for FramelessDialog content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(form)

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def select_file(self) -> None:
        """"""
        result: str = QtWidgets.QFileDialog.getOpenFileName(
            self, filter="CSV (*.csv)")
        filename: str = result[0]
        if filename:
            self.file_edit.setText(filename)


class DownloadWorker(QtCore.QThread):
    """后台下载线程"""
    
    finished = QtCore.Signal(int)  # 下载完成信号，传递下载数量
    progress = QtCore.Signal(str)  # 进度信号，传递日志消息
    progress_info = QtCore.Signal(int, float, str)  # 进度详细信息：已下载数量、时间进度百分比、当前时间点
    
    def __init__(
        self,
        engine: ManagerEngine,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime | None,
        skip_existing: bool
    ) -> None:
        super().__init__()
        self.engine = engine
        self.symbol = symbol
        self.exchange = exchange
        self.interval = interval
        self.start_time = start  # 使用 start_time 避免覆盖 QThread 的 start 方法
        self.end_time = end  # 使用 end_time 保持一致性
        self.skip_existing = skip_existing
        self._count = 0
        
    def run(self) -> None:
        """在线程中执行下载"""
        try:
            if self.interval == Interval.TICK:
                self._count = self.engine.download_tick_data(
                    self.symbol, self.exchange, self.start_time, self._output_callback
                )
            else:
                self._count = self.engine.download_bar_data(
                    self.symbol, self.exchange, self.interval.value, self.start_time,
                    self._output_callback, end=self.end_time, skip_existing=self.skip_existing
                )
        except Exception as e:
            self.progress.emit(f"下载出错: {str(e)}")
            self._count = 0
        finally:
            self.finished.emit(self._count)
    
    def _output_callback(self, msg: str) -> None:
        """将输出消息通过信号发送到主线程"""
        self.progress.emit(msg)
        
        # 尝试从消息中提取进度信息
        # 消息格式可能是："[1] BTC-USDT (1m): 已下载 100 条K线 (+100), 时间范围 2025-12-25 11:59:00 至 2025-12-25 12:00:00, 进度: 0.1% (已下载到 2025-12-25 11:59:00)"
        # 注意：消息中的花括号可能被转义为 {{ 和 }}，但这里的消息不包含花括号，所以不需要担心
        count_match = re.search(r'已下载\s+(\d+)\s+条', msg)
        progress_match = re.search(r'进度:\s+([\d.]+)%', msg)
        time_match = re.search(r'已下载到\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', msg)
        
        if count_match:
            count = int(count_match.group(1))
            progress_percent = float(progress_match.group(1)) if progress_match else -1.0  # 使用-1表示没有进度百分比
            current_time = time_match.group(1) if time_match else None
            
            # 无论是否有进度百分比，都发送进度信息
            self.progress_info.emit(count, progress_percent, current_time or "")
        else:
            # 如果没有匹配到"已下载"，但消息中包含进度百分比，也尝试发送
            # 这可能是其他格式的进度消息
            if progress_match:
                progress_percent = float(progress_match.group(1))
                # 即使没有数量，也发送进度百分比
                self.progress_info.emit(0, progress_percent, "")


class DownloadDialog(FramelessDialog):
    """"""

    def __init__(self, engine: ManagerEngine, parent: QtWidgets.QWidget | None = None) -> None:
        """"""
        super().__init__(parent)
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.engine: ManagerEngine = engine
        self.download_worker: DownloadWorker | None = None

        self.setWindowTitle("下载历史数据")
        
        # 设置窗口标志，确保对话框可以独立存在
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)  # 关闭时自动删除
        self.setFixedWidth(300)
        
        # FramelessDialog 已经使用自定义标题栏，不需要设置 WindowTitleHint 和 WindowCloseButtonHint
        # 这些标志会导致系统显示原生标题栏，与自定义标题栏重复

        self.symbol_edit: LineEdit = LineEdit()
        self.symbol_edit.setText("BTCUSDT_SPOT_OKX")  # 默认代码

        self.exchange_combo: ComboBox = ComboBox()
        for i in Exchange:
            self.exchange_combo.addItem(str(i.name))
            index = self.exchange_combo.count() - 1
            self.exchange_combo.setItemData(index, i)
            self.exchange_combo.setItemIcon(index, QtGui.QIcon())

        # 新增：默认选中 GLOBAL
        ix = self.exchange_combo.findData(Exchange.GLOBAL)
        if ix >= 0:
            self.exchange_combo.setCurrentIndex(ix)

        self.interval_combo: ComboBox = ComboBox()
        for i in Interval:
            self.interval_combo.addItem(str(i.name))
            index = self.interval_combo.count() - 1
            self.interval_combo.setItemData(index, i)
            self.interval_combo.setItemIcon(index, QtGui.QIcon())

        end_dt: datetime = datetime.now()
        start_dt: datetime = end_dt - timedelta(days=3 * 365)

        self.start_date_edit: DateEdit = DateEdit()
        self.start_date_edit.setDate(QtCore.QDate(
            start_dt.year,
            start_dt.month,
            start_dt.day
        ))

        # Add end date edit (optional)
        self.end_date_edit: DateEdit = DateEdit()
        self.end_date_edit.setDate(QtCore.QDate(
            end_dt.year,
            end_dt.month,
            end_dt.day
        ))

        # Add checkbox for using end date
        self.use_end_date_checkbox: CheckBox = CheckBox()
        self.use_end_date_checkbox.setText("指定结束日期")
        self.use_end_date_checkbox.setToolTip(
            "勾选后，使用指定的结束日期。\n"
            "不勾选则下载到当前时间。"
        )
        self.use_end_date_checkbox.toggled.connect(self.end_date_edit.setEnabled)

        # Download button
        self.download_button: PushButton = PushButton("下载")
        self.download_button.clicked.connect(self.download)
        
        # Status label (initially hidden)
        self.status_label: BodyLabel = BodyLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        self.status_label.setStyleSheet("color: blue;")
        
        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form.addRow(BodyLabel("代码"), self.symbol_edit)
        form.addRow(BodyLabel("交易所"), self.exchange_combo)
        form.addRow(BodyLabel("周期"), self.interval_combo)
        form.addRow(BodyLabel("开始日期"), self.start_date_edit)
        form.addRow(BodyLabel(""), self.use_end_date_checkbox)
        form.addRow(BodyLabel("结束日期"), self.end_date_edit)
        self.end_date_edit.setEnabled(False)  # Initially disabled
        form.addRow(self.download_button)
        form.addRow(BodyLabel("状态"), self.status_label)

        # Create container for FramelessDialog content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(form)

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def download(self) -> None:
        """开始下载（异步）"""
        # 获取参数
        symbol: str = self.symbol_edit.text()
        exchange: Exchange = Exchange(self.exchange_combo.currentData())
        interval: Interval = Interval(self.interval_combo.currentData())

        start_date = self.start_date_edit.date()
        start: datetime = datetime(start_date.year(), start_date.month(), start_date.day())
        start = start.replace(tzinfo=DB_TZ)

        # Get end date if specified
        end: datetime | None = None
        if self.use_end_date_checkbox.isChecked():
            end_date = self.end_date_edit.date()
            end = datetime(end_date.year(), end_date.month(), end_date.day(), 23, 59, 59)
            end = end.replace(tzinfo=DB_TZ)

        # 判断是否进行了智能检测：
        # 如果用户指定了结束日期（use_end_date_checkbox被勾选），则按照用户设置的日期下载，不进行智能检测
        # 如果用户没有指定结束日期（只指定了开始日期，结束日期是当前时间），则进行智能检测
        skip_existing: bool = not self.use_end_date_checkbox.isChecked()

        # 禁用控件
        self.download_button.setEnabled(False)
        self.download_button.setText("下载中...")
        
        # 禁用输入控件
        self.symbol_edit.setEnabled(False)
        self.exchange_combo.setEnabled(False)
        self.interval_combo.setEnabled(False)
        self.start_date_edit.setEnabled(False)
        self.end_date_edit.setEnabled(False)
        self.use_end_date_checkbox.setEnabled(False)

        # 存储时间范围信息，用于估算总K线数量（在创建worker之前）
        self._start_time = start.replace(tzinfo=None) if start else None
        self._end_time = end.replace(tzinfo=None) if end else datetime.now()
        self._interval = interval
        
        # 显示状态标签
        self.status_label.setVisible(True)
        self.status_label.setText("正在下载数据，请稍候...")
        self.status_label.setStyleSheet("color: blue;")

        # 创建并启动下载线程
        self.download_worker = DownloadWorker(
            self.engine, symbol, exchange, interval, start, end, skip_existing
        )
        self.download_worker.progress.connect(self.on_progress)
        self.download_worker.finished.connect(self.on_finished)
        self.download_worker.start()

    def on_progress(self, msg: str) -> None:
        """接收下载进度消息"""
        # 更新状态标签，显示实时进度信息
        if len(msg) > 300:
            display_msg = msg[:300] + "..."
        else:
            display_msg = msg
        self.status_label.setText(display_msg)
        self.status_label.setStyleSheet("color: blue;")
    

    def on_finished(self, count: int) -> None:
        """下载完成"""
        # 检查状态标签中是否已经有错误消息
        current_text = self.status_label.text()
        has_error = any(keyword in current_text for keyword in ["失败", "错误", "没有正确配置", "无法", "找不到"])
        
        # 如果下载数量为0且已有错误消息，保留错误消息不覆盖
        if count == 0 and has_error:
            # 保留当前错误消息，只改变样式为红色
            self.status_label.setStyleSheet("color: red;")
        else:
            # 更新状态标签
            self.status_label.setText(f"[完成] 下载完成！共下载 {count} 条数据")
            self.status_label.setStyleSheet("color: green;")
        
        # 恢复控件状态
        self.download_button.setEnabled(True)
        self.download_button.setText("下载")
        
        # 恢复输入控件
        self.symbol_edit.setEnabled(True)
        self.exchange_combo.setEnabled(True)
        self.interval_combo.setEnabled(True)
        self.start_date_edit.setEnabled(True)
        if self.use_end_date_checkbox.isChecked():
            self.end_date_edit.setEnabled(True)
        self.use_end_date_checkbox.setEnabled(True)
        
        # 清理线程
        if self.download_worker:
            self.download_worker.deleteLater()
            self.download_worker = None
        
        # 如果有错误，显示错误消息框；否则显示完成消息
        if count == 0 and has_error:
            MessageBox("下载失败", f"下载失败，请检查错误信息。\n当前状态：{current_text}", self).exec()
        else:
            MessageBox("下载结束", f"下载总数据量：{count}条", self).exec()
        
        # 自动关闭对话框（对话框关闭后会被删除，不需要定时器隐藏状态标签）
        self.accept()
