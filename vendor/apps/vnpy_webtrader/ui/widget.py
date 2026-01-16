import sys
from pathlib import Path

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets, QtCore
from vnpy.trader.utility import load_json, save_json, get_file_path
from qfluentwidgets import (
    PushButton, LineEdit, BodyLabel
)
from qframelesswindow import FramelessWindow
from qframelesswindow.titlebar import StandardTitleBar
from vnpy.trader.ui import QtGui

from ..engine import APP_NAME, WebEngine


class WebManager(FramelessWindow):
    """网页服务器管理界面"""

    setting_filename: str = "web_trader_setting.json"
    setting_filepath: Path = get_file_path(setting_filename)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
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
        self.web_engine: WebEngine = main_engine.get_engine(APP_NAME)

        self.init_ui()

    def init_ui(self) -> None:
        """初始化界面"""
        self.setWindowTitle("Web服务")

        setting: dict = load_json(self.setting_filepath)
        username: str = setting.get("username", "vnpy")
        password: str = setting.get("password", "vnpy")
        req_address: str = setting.get("req_address", "tcp://127.0.0.1:2014")
        sub_address: str = setting.get("sub_address", "tcp://127.0.0.1:4102")
        host: str = setting.get("host", "127.0.0.1")
        port: str = setting.get("port", "8000")

        self.username_line: LineEdit = LineEdit()
        self.username_line.setText(username)
        self.password_line: LineEdit = LineEdit()
        self.password_line.setText(password)
        self.req_line: LineEdit = LineEdit()
        self.req_line.setText(req_address)
        self.sub_line: LineEdit = LineEdit()
        self.sub_line.setText(sub_address)
        self.host_line: LineEdit = LineEdit()
        self.host_line.setText(host)
        self.port_line: LineEdit = LineEdit()
        self.port_line.setText(port)

        self.start_button: PushButton = PushButton("启动")
        self.start_button.clicked.connect(self.start)

        self.end_button: PushButton = PushButton("停止")
        self.end_button.clicked.connect(self.end)

        self.text_edit: QtWidgets.QPlainTextEdit = QtWidgets.QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        # 设置深色主题样式
        self.text_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgb(32, 32, 32);
                color: white;
                border: 1px solid rgb(60, 60, 60);
                border-radius: 4px;
            }
        """)

        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form.addRow(BodyLabel("用户名"), self.username_line)
        form.addRow(BodyLabel("密码"), self.password_line)
        form.addRow(BodyLabel("请求地址"), self.req_line)
        form.addRow(BodyLabel("订阅地址"), self.sub_line)
        form.addRow(BodyLabel("监听地址"), self.host_line)
        form.addRow(BodyLabel("监听端口"), self.port_line)
        form.addRow(self.start_button)
        form.addRow(self.end_button)

        self.end_button.setEnabled(False)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addLayout(form)
        hbox.addWidget(self.text_edit)

        # Create container widget for FramelessWindow content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(hbox)

        # Main layout with title bar margin
        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

        self.resize(1000, 500)

    def start(self) -> None:
        """启动引擎"""
        username: str = self.username_line.text()
        password: str = self.password_line.text()
        req_address: str = self.req_line.text()
        sub_address: str = self.sub_line.text()
        host: str = self.host_line.text()
        port: str = self.port_line.text()

        # 保存配置
        setting: dict = {
            "username": username,
            "password": password,
            "req_address": req_address,
            "sub_address": sub_address,
            "host": host,
            "port": port
        }
        save_json(self.setting_filepath, setting)

        # 启动RPC
        self.web_engine.start_server(req_address, sub_address)
        self.start_button.setDisabled(True)

        # 初始化Web服务子进程
        self.process: QtCore.QProcess = QtCore.QProcess(self)
        self.process.setProcessChannelMode(self.process.MergedChannels)

        self.process.readyReadStandardOutput.connect(self.data_ready)
        self.process.readyReadStandardError.connect(self.data_ready)
        self.process.started.connect(self.web_started)
        self.process.finished.connect(self.web_finished)

        # 启动子进程
        cmd: list = [
            "-m"
            "uvicorn",
            "vnpy_webtrader.web:app",
            f"--host={host}",
            f"--port={port}"
        ]
        self.process.start(sys.executable, cmd)

    def end(self) -> None:
        """终止引擎"""
        self.process.kill()

    def web_started(self) -> None:
        """Web进程启动"""
        self.text_edit.appendPlainText("Web服务器启动")

        for w in [
            self.username_line,
            self.password_line,
            self.req_line,
            self.sub_line,
            self.host_line,
            self.port_line,
            self.start_button
        ]:
            w.setEnabled(False)

        self.end_button.setEnabled(True)

    def web_finished(self) -> None:
        """Web进程结束"""
        self.text_edit.appendPlainText("Web服务器停止")

        for w in [
            self.username_line,
            self.password_line,
            self.req_line,
            self.sub_line,
            self.host_line,
            self.port_line,
            self.start_button
        ]:
            w.setEnabled(True)

        self.end_button.setEnabled(False)

    def data_ready(self) -> None:
        """更新进程有数据可读"""
        text: bytes = bytes(self.process.readAll())

        try:
            text: str = text.decode("UTF8")
        except UnicodeDecodeError:
            text: str = text.decode("GBK")

        self.text_edit.appendPlainText(text)
