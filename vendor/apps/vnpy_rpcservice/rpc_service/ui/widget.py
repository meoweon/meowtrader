from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import LogData
from vnpy.trader.ui import QtWidgets, QtCore
from qfluentwidgets import (
    PushButton, LineEdit, BodyLabel
)
from qframelesswindow import FramelessWindow
from qframelesswindow.titlebar import StandardTitleBar
from vnpy.trader.ui import QtGui
from ..engine import APP_NAME, EVENT_RPC_LOG, RpcEngine


class RpcManager(FramelessWindow):
    """"""
    signal_log: QtCore.Signal = QtCore.Signal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """构造函数"""
        super().__init__()

        # Set up Fluent-style title bar
        self.setTitleBar(StandardTitleBar(self))
        from vnpy.trader.ui.titlebar_utils import setup_title_bar_style
        setup_title_bar_style(self.titleBar)

        # Set dark background for Fluent theme
        self.setStyleSheet("background-color: rgb(32, 32, 32);")

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.rpc_engine: RpcEngine = main_engine.get_engine(APP_NAME)

        self.init_ui()
        self.register_event()

    def init_ui(self) -> None:
        """初始化界面"""
        self.setWindowTitle("RPC服务")
        self.setFixedWidth(900)
        self.setFixedHeight(500)

        self.start_button: PushButton = PushButton("启动")
        self.start_button.clicked.connect(self.start_server)

        self.stop_button: PushButton = PushButton("停止")
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setEnabled(False)

        for button in [self.start_button, self.stop_button]:
            hint: QtCore.QSize = button.sizeHint()
            button.setFixedHeight(hint.height() * 2)
            button.setFixedWidth(hint.width() * 4)

        self.rep_line: LineEdit = LineEdit()
        self.rep_line.setText(self.rpc_engine.rep_address)
        self.rep_line.setFixedWidth(300)

        self.pub_line: LineEdit = LineEdit()
        self.pub_line.setText(self.rpc_engine.pub_address)
        self.pub_line.setFixedWidth(300)

        self.log_monitor: QtWidgets.QPlainTextEdit = QtWidgets.QPlainTextEdit()
        self.log_monitor.setReadOnly(True)
        # 设置深色主题样式
        self.log_monitor.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgb(32, 32, 32);
                color: white;
                border: 1px solid rgb(60, 60, 60);
                border-radius: 4px;
            }
        """)

        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form.addRow(BodyLabel("请求响应地址"), self.rep_line)
        form.addRow(BodyLabel("事件广播地址"), self.pub_line)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addLayout(form)
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.stop_button)
        hbox.addStretch()

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
        """注册事件"""
        self.signal_log.connect(self.process_log_event)

        self.event_engine.register(EVENT_RPC_LOG, self.signal_log.emit)

    def process_log_event(self, event: Event) -> None:
        """调用事件"""
        log: LogData = event.data
        msg: str = f"{log.time}\t{log.msg}"
        self.log_monitor.appendPlainText(msg)

    def start_server(self) -> None:
        """启动服务"""
        rep_address: str = self.rep_line.text()
        pub_address: str = self.pub_line.text()

        result: bool = self.rpc_engine.start(rep_address, pub_address)
        if result:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_server(self) -> None:
        """停止服务"""
        result: bool = self.rpc_engine.stop()
        if result:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
