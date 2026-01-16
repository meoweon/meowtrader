from pathlib import Path

from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets, QtCore, QtGui
from vnpy.trader.object import LogData
from qframelesswindow import FramelessWindow
from qframelesswindow.titlebar import StandardTitleBar
from qfluentwidgets import PushButton, LineEdit, BodyLabel
from ..engine import APP_NAME, EVENT_RTD_LOG, BaseEngine


class RtdManager(FramelessWindow):
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
        self.rm_engine: BaseEngine = main_engine.get_engine(APP_NAME)

        self.init_ui()
        self.register_event()

    def init_ui(self) -> None:
        """
        Init widget ui components.
        """
        self.setWindowTitle("Excel RTD")
        self.resize(600, 600)

        module_path: Path = Path(__file__).parent.parent
        client_path: Path = module_path.joinpath("vnpy_rtd.py")
        self.client_line: LineEdit = LineEdit()
        self.client_line.setText(str(client_path))
        self.client_line.setReadOnly(True)

        copy_button: PushButton = PushButton("复制")
        copy_button.clicked.connect(self.copy_client_path)

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

        self.port_label: BodyLabel = BodyLabel(
            "使用Socket端口：请求回应9001、广播推送9002"
        )

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.client_line)
        hbox.addWidget(copy_button)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.log_monitor)
        vbox.addWidget(self.port_label)

        # Create container widget for FramelessWindow content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(vbox)

        # Main layout with title bar margin
        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

    def register_event(self) -> None:
        """
        Register event handler.
        """
        self.signal_log.connect(self.process_log_event)

        self.event_engine.register(EVENT_RTD_LOG, self.signal_log.emit)

    def process_log_event(self, event: Event) -> None:
        """
        Show log message in monitor.
        """
        log: LogData = event.data

        msg: str = f"{log.time}: {log.msg}"
        self.log_monitor.append(msg)

    def copy_client_path(self) -> None:
        """
        Copy path of client python file to clipboard.
        """
        self.client_line.selectAll()
        self.client_line.copy()
