from datetime import datetime

from vnpy.event import Event, EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtCore, QtWidgets, QtGui
from vnpy.trader.event import EVENT_CONTRACT
from vnpy.trader.object import ContractData
from qframelesswindow import FramelessWindow
from qframelesswindow.titlebar import StandardTitleBar
from qfluentwidgets import (
    PushButton, LineEdit, SpinBox, BodyLabel, 
    MessageBox, VBoxLayout
)

from ..engine import (
    APP_NAME,
    EVENT_RECORDER_LOG,
    EVENT_RECORDER_UPDATE,
    RecorderEngine
)


class RecorderManager(FramelessWindow):
    """"""

    signal_log: QtCore.Signal = QtCore.Signal(Event)
    signal_update: QtCore.Signal = QtCore.Signal(Event)
    signal_contract: QtCore.Signal = QtCore.Signal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        super().__init__()

        # Set up Fluent-style title bar
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.titleLabel.setStyleSheet("color: white;")
        # Set title bar button colors for dark theme
        for btn in [self.titleBar.minBtn, self.titleBar.maxBtn, self.titleBar.closeBtn]:
            btn.setNormalColor(QtGui.QColor(255, 255, 255))
            btn.setHoverColor(QtGui.QColor(255, 255, 255))
            btn.setPressedColor(QtGui.QColor(255, 255, 255))

        # Set dark background for Fluent theme
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine
        self.recorder_engine: RecorderEngine | None = main_engine.get_engine(APP_NAME)
        
        # 检查引擎是否已加载
        if self.recorder_engine is None:
            # 显示友好的错误信息，而不是抛出异常
            error_msg = (
                f"数据录制功能未正确加载。\n\n"
                f"可能的原因：\n"
                f"1. 缺少必要的依赖模块（如 vnpy_sqlite）\n"
                f"2. DataRecorderApp 加载失败\n\n"
                f"请检查启动日志中的错误信息。"
            )
            
            # 创建错误对话框（使用主窗口作为父窗口）
            parent_window = None
            try:
                from PySide6.QtWidgets import QApplication
                parent_window = QApplication.activeWindow()
            except:
                pass
            
            MessageBox(
                "数据录制功能不可用",
                error_msg,
                parent=parent_window
            ).exec()
            
            # 不初始化 UI，直接返回
            # 但需要设置一个基本的窗口标题和布局，避免完全空白
            self.setWindowTitle("数据录制 - 不可用")
            self.resize(400, 200)
            
            layout = VBoxLayout(self)
            error_label = BodyLabel(error_msg)
            error_label.setWordWrap(True)
            layout.addWidget(error_label)
            return  # 提前返回，不继续初始化

        self.init_ui()
        self.register_event()
        self.recorder_engine.put_event()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("行情记录")
        self.resize(1000, 600)

        # Create widgets
        self.symbol_line: LineEdit = LineEdit()

        self.interval_spin: SpinBox = SpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(60)
        # 使用引擎的 timer_interval（引擎已在 __init__ 中检查，确保不为 None）
        if self.recorder_engine is not None:
            self.interval_spin.setValue(self.recorder_engine.timer_interval)
        else:
            # 如果引擎仍然为 None，使用默认值
            self.interval_spin.setValue(10)
        self.interval_spin.setSuffix("秒")
        self.interval_spin.valueChanged.connect(self.set_interval)

        contracts: list[ContractData] = self.main_engine.get_all_contracts()
        self.vt_symbols: list = [contract.vt_symbol for contract in contracts]

        self.symbol_completer: QtWidgets.QCompleter = QtWidgets.QCompleter(self.vt_symbols)
        self.symbol_completer.setFilterMode(QtCore.Qt.MatchContains)
        self.symbol_completer.setCompletionMode(self.symbol_completer.CompletionMode.PopupCompletion)
        self.symbol_line.setCompleter(self.symbol_completer)

        add_bar_button: PushButton = PushButton("添加")
        add_bar_button.clicked.connect(self.add_bar_recording)

        remove_bar_button: PushButton = PushButton("移除")
        remove_bar_button.clicked.connect(self.remove_bar_recording)

        add_tick_button: PushButton = PushButton("添加")
        add_tick_button.clicked.connect(self.add_tick_recording)

        remove_tick_button: PushButton = PushButton("移除")
        remove_tick_button.clicked.connect(self.remove_tick_recording)

        self.bar_recording_edit: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
        self.bar_recording_edit.setReadOnly(True)
        # 设置深色主题样式
        self.bar_recording_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgb(32, 32, 32);
                color: white;
                border: 1px solid rgb(60, 60, 60);
                border-radius: 4px;
            }
        """)

        self.tick_recording_edit: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
        self.tick_recording_edit.setReadOnly(True)
        # 设置深色主题样式
        self.tick_recording_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgb(32, 32, 32);
                color: white;
                border: 1px solid rgb(60, 60, 60);
                border-radius: 4px;
            }
        """)

        self.log_edit: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
        self.log_edit.setReadOnly(True)
        # 设置深色主题样式
        self.log_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgb(32, 32, 32);
                color: white;
                border: 1px solid rgb(60, 60, 60);
                border-radius: 4px;
            }
        """)

        # Set layout
        grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        grid.addWidget(BodyLabel("K线记录"), 0, 0)
        grid.addWidget(add_bar_button, 0, 1)
        grid.addWidget(remove_bar_button, 0, 2)
        grid.addWidget(BodyLabel("Tick记录"), 1, 0)
        grid.addWidget(add_tick_button, 1, 1)
        grid.addWidget(remove_tick_button, 1, 2)

        # Use QGridLayout with BodyLabel for proper Fluent theme inheritance
        form: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        form.addWidget(BodyLabel("本地代码"), 0, 0)
        form.addWidget(self.symbol_line, 0, 1)
        form.addWidget(BodyLabel("写入间隔"), 1, 0)
        form.addWidget(self.interval_spin, 1, 1)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addLayout(form)
        hbox.addWidget(BodyLabel("     "))
        hbox.addLayout(grid)
        hbox.addStretch()

        grid2: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        grid2.addWidget(BodyLabel("K线记录列表"), 0, 0)
        grid2.addWidget(BodyLabel("Tick记录列表"), 0, 1)
        grid2.addWidget(self.bar_recording_edit, 1, 0)
        grid2.addWidget(self.tick_recording_edit, 1, 1)
        grid2.addWidget(self.log_edit, 2, 0, 1, 2)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(grid2)

        # Create container widget for FramelessWindow content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(vbox)

        # Main layout with title bar margin
        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def register_event(self) -> None:
        """"""
        self.signal_log.connect(self.process_log_event)
        self.signal_contract.connect(self.process_contract_event)
        self.signal_update.connect(self.process_update_event)

        self.event_engine.register(EVENT_CONTRACT, self.signal_contract.emit)
        self.event_engine.register(EVENT_RECORDER_LOG, self.signal_log.emit)
        self.event_engine.register(EVENT_RECORDER_UPDATE, self.signal_update.emit)

    def process_log_event(self, event: Event) -> None:
        """"""
        timestamp: str = datetime.now().strftime("%H:%M:%S")
        msg: str = f"{timestamp}\t{event.data}"
        self.log_edit.append(msg)

    def process_update_event(self, event: Event) -> None:
        """"""
        data: dict = event.data

        self.bar_recording_edit.clear()
        bar_text: str = "\n".join(data["bar"])
        self.bar_recording_edit.setText(bar_text)

        self.tick_recording_edit.clear()
        tick_text: str = "\n".join(data["tick"])
        self.tick_recording_edit.setText(tick_text)

    def process_contract_event(self, event: Event) -> None:
        """"""
        contract: ContractData = event.data
        self.vt_symbols.append(contract.vt_symbol)

        model: QtCore.QAbstractItemModel = self.symbol_completer.model()
        model.setStringList(self.vt_symbols)

    def add_bar_recording(self) -> None:
        """"""
        vt_symbol: str = self.symbol_line.text()
        self.recorder_engine.add_bar_recording(vt_symbol)

    def add_tick_recording(self) -> None:
        """"""
        vt_symbol: str = self.symbol_line.text()
        self.recorder_engine.add_tick_recording(vt_symbol)

    def remove_bar_recording(self) -> None:
        """"""
        vt_symbol: str = self.symbol_line.text()
        self.recorder_engine.remove_bar_recording(vt_symbol)

    def remove_tick_recording(self) -> None:
        """"""
        vt_symbol: str = self.symbol_line.text()
        self.recorder_engine.remove_tick_recording(vt_symbol)

    def set_interval(self, interval: int) -> None:
        """"""
        self.recorder_engine.timer_interval = interval
