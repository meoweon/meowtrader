from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets, QtGui

from qfluentwidgets import (
    PushButton, ComboBox, SpinBox, BodyLabel
)
from qframelesswindow import FramelessDialog
from qframelesswindow.titlebar import StandardTitleBar

from ..engine import APP_NAME, RiskEngine


class RiskManager(FramelessDialog):
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

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine
        self.rm_engine: RiskEngine = main_engine.get_engine(APP_NAME)

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("交易风控")

        # Create widgets
        self.active_combo = ComboBox()
        self.active_combo.addItems(["停止", "启动"])

        self.flow_limit_spin = RiskManagerSpinBox()
        self.flow_clear_spin = RiskManagerSpinBox()
        self.size_limit_spin = RiskManagerSpinBox()
        self.trade_limit_spin = RiskManagerSpinBox()
        self.active_limit_spin = RiskManagerSpinBox()
        self.cancel_limit_spin = RiskManagerSpinBox()

        save_button = PushButton("保存")
        save_button.clicked.connect(self.save_setting)

        # Use QGridLayout with BodyLabel for proper Fluent theme inheritance
        form = QtWidgets.QGridLayout()
        form.addWidget(BodyLabel("风控运行状态"), 0, 0)
        form.addWidget(self.active_combo, 0, 1)
        form.addWidget(BodyLabel("委托流控上限（笔）"), 1, 0)
        form.addWidget(self.flow_limit_spin, 1, 1)
        form.addWidget(BodyLabel("委托流控清空（秒）"), 2, 0)
        form.addWidget(self.flow_clear_spin, 2, 1)
        form.addWidget(BodyLabel("单笔委托上限（数量）"), 3, 0)
        form.addWidget(self.size_limit_spin, 3, 1)
        form.addWidget(BodyLabel("总成交上限（笔）"), 4, 0)
        form.addWidget(self.trade_limit_spin, 4, 1)
        form.addWidget(BodyLabel("活动委托上限（笔）"), 5, 0)
        form.addWidget(self.active_limit_spin, 5, 1)
        form.addWidget(BodyLabel("合约撤单上限（笔）"), 6, 0)
        form.addWidget(self.cancel_limit_spin, 6, 1)
        form.addWidget(save_button, 7, 0, 1, 2)

        # Create container widget for FramelessDialog content
        container = QtWidgets.QWidget(self)
        container.setLayout(form)

        # Main layout with title bar margin
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        main_layout.addWidget(container)

        # Set Fix Size (account for title bar height)
        hint = self.sizeHint()
        self.setFixedSize(int(hint.width() * 1.2), hint.height() + self.titleBar.height())

    def save_setting(self) -> None:
        """"""
        active_text = self.active_combo.currentText()
        if active_text == "启动":
            active = True
        else:
            active = False

        setting = {
            "active": active,
            "order_flow_limit": self.flow_limit_spin.value(),
            "order_flow_clear": self.flow_clear_spin.value(),
            "order_size_limit": self.size_limit_spin.value(),
            "trade_limit": self.trade_limit_spin.value(),
            "active_order_limit": self.active_limit_spin.value(),
            "order_cancel_limit": self.cancel_limit_spin.value(),
        }

        self.rm_engine.update_setting(setting)
        self.rm_engine.save_setting()

        self.close()

    def update_setting(self) -> None:
        """"""
        setting = self.rm_engine.get_setting()
        if setting["active"]:
            self.active_combo.setCurrentIndex(1)
        else:
            self.active_combo.setCurrentIndex(0)

        self.flow_limit_spin.setValue(setting["order_flow_limit"])
        self.flow_clear_spin.setValue(setting["order_flow_clear"])
        self.size_limit_spin.setValue(setting["order_size_limit"])
        self.trade_limit_spin.setValue(setting["trade_limit"])
        self.active_limit_spin.setValue(setting["active_order_limit"])
        self.cancel_limit_spin.setValue(setting["order_cancel_limit"])

    def exec(self) -> None:
        """"""
        self.update_setting()
        super().exec()


class RiskManagerSpinBox(SpinBox):
    """"""

    def __init__(self, value: int = 0) -> None:
        """"""
        super().__init__()

        self.setMinimum(0)
        self.setMaximum(1000000)
        self.setValue(value)
