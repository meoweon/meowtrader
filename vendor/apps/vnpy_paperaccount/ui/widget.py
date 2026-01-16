from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets, QtGui
from qfluentwidgets import (
    PushButton, SpinBox, CheckBox, BodyLabel
)
from qframelesswindow import FramelessWindow
from qframelesswindow.titlebar import StandardTitleBar

from ..engine import (
    PaperEngine,
    APP_NAME,
)


class PaperManager(FramelessWindow):
    """"""

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

        self.paper_engine: PaperEngine = main_engine.get_engine(APP_NAME)

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("模拟交易")
        self.setFixedHeight(200)
        self.setFixedWidth(500)

        interval_spin: SpinBox = SpinBox()
        interval_spin.setMinimum(1)
        interval_spin.setValue(self.paper_engine.timer_interval)
        interval_spin.setSuffix(" 秒")
        interval_spin.valueChanged.connect(self.paper_engine.set_timer_interval)

        slippage_spin: SpinBox = SpinBox()
        slippage_spin.setMinimum(0)
        slippage_spin.setValue(self.paper_engine.trade_slippage)
        slippage_spin.setSuffix(" 跳")
        slippage_spin.valueChanged.connect(self.paper_engine.set_trade_slippage)

        instant_check: CheckBox = CheckBox()
        instant_check.setChecked(self.paper_engine.instant_trade)
        instant_check.stateChanged.connect(self.paper_engine.set_instant_trade)

        clear_button: PushButton = PushButton("清空所有持仓")
        clear_button.clicked.connect(self.paper_engine.clear_position)

        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form.addRow(BodyLabel("市价委托和停止委托的成交滑点"), slippage_spin)
        form.addRow(BodyLabel("模拟交易持仓盈亏的计算频率"), interval_spin)
        form.addRow(BodyLabel("下单后立即使用当前盘口撮合"), instant_check)
        form.addRow(clear_button)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addStretch()
        vbox.addLayout(form)
        vbox.addStretch()

        # Create container widget for FramelessWindow content
        container: QtWidgets.QWidget = QtWidgets.QWidget(self)
        container.setLayout(vbox)

        # Main layout with title bar margin
        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)
