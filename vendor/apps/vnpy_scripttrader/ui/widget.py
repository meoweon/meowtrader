from pathlib import Path

from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets, QtCore, QtGui
from vnpy.trader.object import LogData
from qframelesswindow import FramelessWindow
from qframelesswindow.titlebar import StandardTitleBar
from qfluentwidgets import PushButton, LineEdit
from ..engine import APP_NAME, EVENT_SCRIPT_LOG, BaseEngine


class ScriptManager(FramelessWindow):
    """"""
    signal_log: QtCore.Signal = QtCore.Signal(Event)

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

        self.script_engine: BaseEngine = main_engine.get_engine(APP_NAME)

        self.script_path: str = ""

        self.init_ui()
        self.register_event()

        self.script_engine.init()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("脚本策略")

        start_button: PushButton = PushButton("启动")
        start_button.clicked.connect(self.start_script)

        stop_button: PushButton = PushButton("停止")
        stop_button.clicked.connect(self.stop_script)

        select_button: PushButton = PushButton("打开")
        select_button.clicked.connect(self.select_script)

        self.strategy_line: LineEdit = LineEdit()

        self.log_monitor: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
        self.log_monitor.setReadOnly(True)
        # 设置深色主题样式
        self.log_monitor.setStyleSheet("""
            QTextEdit {
                background-color: rgb(32, 32, 32);
                color: white;
                border: 1px solid rgb(60, 60, 60);
                border-radius: 4px;
            }
        """)

        clear_button: PushButton = PushButton("清空")
        clear_button.clicked.connect(self.log_monitor.clear)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.strategy_line)
        hbox.addWidget(select_button)
        hbox.addWidget(start_button)
        hbox.addWidget(stop_button)
        hbox.addStretch()
        hbox.addWidget(clear_button)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.log_monitor)

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

        self.event_engine.register(EVENT_SCRIPT_LOG, self.signal_log.emit)

    def show(self) -> None:
        """"""
        super().show()

    def process_log_event(self, event: Event) -> None:
        """"""
        log: LogData = event.data
        msg: str = f"{log.time}\t{log.msg}"
        self.log_monitor.append(msg)

    def start_script(self) -> None:
        """"""
        if self.script_path:
            self.script_engine.start_strategy(self.script_path)

    def stop_script(self) -> None:
        """"""
        self.script_engine.stop_strategy()

    def select_script(self) -> None:
        """"""
        cwd: str = str(Path.cwd())

        path, type_ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "载入策略脚本",
            cwd,
            "Python File(*.py)"
        )

        if path:
            self.script_path = path
            self.strategy_line.setText(path)
