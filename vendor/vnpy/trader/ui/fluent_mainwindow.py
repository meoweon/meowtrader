"""
Fluent Design style main window for VeighNa Trader.
Based on PySide6-Fluent-Widgets FluentWindow architecture.
"""

from types import ModuleType
import webbrowser
from functools import partial
from importlib import import_module
from typing import TypeVar

import vnpy
from vnpy.event import EventEngine

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PySide6.QtGui import QIcon

from qfluentwidgets import (
    FluentWindow, FluentIcon, NavigationItemPosition,
    Action, MessageBox, TabWidget, CardWidget, 
    SubtitleLabel, BodyLabel, PushButton, RoundMenu
)

from .widget import (
    BaseMonitor,
    TickMonitor,
    OrderMonitor,
    TradeMonitor,
    PositionMonitor,
    AccountMonitor,
    LogMonitor,
    ActiveOrderMonitor,
    ConnectDialog,
    ContractManager,
    TradingWidget,
    AboutDialog,
    GlobalDialog
)
from ..engine import MainEngine, BaseApp
from ..utility import get_icon_path, TRADER_DIR
from ..locale import _


WidgetType = TypeVar("WidgetType", bound="QWidget")


class TradingInterface(QWidget):
    """
    Trading interface containing the trading panel and market depth monitors.
    This is the main trading view combining multiple monitors.
    """
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine, parent=None):
        super().__init__(parent)
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.setObjectName("trading_interface")
        
        self.init_ui()
    
    def init_ui(self):
        # Create trading widget (left side)
        self.trading_widget = TradingWidget(self.main_engine, self.event_engine)
        
        # Create tick monitor (market data)
        self.tick_monitor = TickMonitor(self.main_engine, self.event_engine)
        
        # Layout: trading panel on left, tick monitor on right
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.trading_widget)
        splitter.addWidget(self.tick_monitor)
        splitter.setStretchFactor(0, 0)  # Trading widget doesn't stretch
        splitter.setStretchFactor(1, 1)  # Tick monitor stretches
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(splitter)
        
        # Connect tick monitor double click to trading widget
        self.tick_monitor.itemDoubleClicked.connect(self.trading_widget.update_with_cell)


class OrderInterface(QWidget):
    """
    Order management interface containing order and active order monitors.
    """
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine, parent=None):
        super().__init__(parent)
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.setObjectName("order_interface")
        
        self.init_ui()
    
    def init_ui(self):
        # Create tab widget for different order views
        self.tab_widget = TabWidget(self)
        
        # Order monitor (all orders)
        self.order_monitor = OrderMonitor(self.main_engine, self.event_engine)
        self.tab_widget.addTab(self.order_monitor, _("全部委托"))
        
        # Active order monitor
        self.active_monitor = ActiveOrderMonitor(self.main_engine, self.event_engine)
        self.tab_widget.addTab(self.active_monitor, _("活动委托"))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.tab_widget)


class TradeInterface(QWidget):
    """
    Trade record interface containing trade monitor.
    """
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine, parent=None):
        super().__init__(parent)
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.setObjectName("trade_interface")
        
        self.init_ui()
    
    def init_ui(self):
        self.trade_monitor = TradeMonitor(self.main_engine, self.event_engine)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.trade_monitor)


class PositionInterface(QWidget):
    """
    Position management interface containing position and account monitors.
    """
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine, parent=None):
        super().__init__(parent)
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.setObjectName("position_interface")
        
        self.init_ui()
    
    def init_ui(self):
        # Create tab widget
        self.tab_widget = TabWidget(self)
        
        # Position monitor
        self.position_monitor = PositionMonitor(self.main_engine, self.event_engine)
        self.tab_widget.addTab(self.position_monitor, _("持仓"))
        
        # Account monitor
        self.account_monitor = AccountMonitor(self.main_engine, self.event_engine)
        self.tab_widget.addTab(self.account_monitor, _("资金"))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.tab_widget)


class LogInterface(QWidget):
    """
    Log display interface.
    """
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine, parent=None):
        super().__init__(parent)
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.setObjectName("log_interface")
        
        self.init_ui()
    
    def init_ui(self):
        self.log_monitor = LogMonitor(self.main_engine, self.event_engine)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.log_monitor)


class SettingsInterface(QWidget):
    """
    Settings interface for gateway connections and global configuration.
    Displays gateways grouped by category with descriptions.
    """
    
    # Gateway 分类显示名称和顺序
    CATEGORY_ORDER = [
        ("crypto", "🌐 加密货币交易所"),
        ("cn_futures", "📈 国内期货"),
        ("cn_stock", "📊 国内股票/期权"),
        ("cn_gold", "🥇 国内贵金属"),
        ("global", "🌍 国际/外盘"),
        ("datafeed", "📡 数据服务"),
        ("special", "⚙️ 特殊接口"),
    ]
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine, parent=None):
        super().__init__(parent)
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.setObjectName("settings_interface")
        
        # 已加载的 Gateway 名称列表
        self.loaded_gateways = set(self.main_engine.get_all_gateway_names())
        
        self.init_ui()
    
    def init_ui(self):
        # 使用滚动区域
        from PySide6.QtWidgets import QScrollArea
        
        # 设置整个 SettingsInterface 的背景色
        self.setStyleSheet("""
            SettingsInterface {
                background-color: rgb(32, 32, 32);
            }
        """)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        # 设置滚动区域背景色，与 Fluent 深色主题一致
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: rgb(32, 32, 32);
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: rgb(32, 32, 32);
            }
        """)
        
        content = QWidget()
        content.setObjectName("settings_content")
        # 确保内容区域也有深色背景
        content.setStyleSheet("background-color: rgb(32, 32, 32);")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title = SubtitleLabel(_("交易接口连接"))
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # 获取所有已加载的 Gateway 并按分类组织
        gateway_by_category = self._get_gateways_by_category()
        
        # 按顺序显示每个分类
        for category_key, category_name in self.CATEGORY_ORDER:
            gateways = gateway_by_category.get(category_key, [])
            if not gateways:
                continue
            
            # 分类标题
            category_label = SubtitleLabel(category_name)
            category_label.setStyleSheet("font-size: 14px; color: #888; margin-top: 10px;")
            layout.addWidget(category_label)
            
            # 该分类下的 Gateway
            for gw_name, gw_display, gw_desc in gateways:
                card = self._create_gateway_card(gw_name, gw_display, gw_desc)
                layout.addWidget(card)
        
        layout.addSpacing(30)
        
        # 全局配置
        settings_label = SubtitleLabel(_("⚙️ 全局配置"))
        settings_label.setStyleSheet("font-size: 14px; color: #888;")
        layout.addWidget(settings_label)
        
        settings_card = CardWidget(self)
        settings_card.setFixedHeight(60)
        settings_layout = QHBoxLayout(settings_card)
        settings_layout.setContentsMargins(15, 10, 15, 10)
        settings_info = BodyLabel(_("修改全局配置参数（数据库、邮件等）"))
        settings_btn = PushButton(_("配置"))
        settings_btn.setFixedWidth(80)
        settings_btn.clicked.connect(self.edit_global_setting)
        settings_layout.addWidget(settings_info)
        settings_layout.addStretch()
        settings_layout.addWidget(settings_btn)
        layout.addWidget(settings_card)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _get_gateways_by_category(self) -> dict[str, list[tuple[str, str, str]]]:
        """获取按分类组织的 Gateway 列表"""
        # 从 product_engine 导入 GATEWAY_MAP
        try:
            from meowtrader.core.engine.product_engine import GATEWAY_MAP
        except ImportError:
            GATEWAY_MAP = {}
        
        result: dict[str, list[tuple[str, str, str]]] = {}
        
        for gw_name in self.loaded_gateways:
            if gw_name in GATEWAY_MAP:
                info = GATEWAY_MAP[gw_name]
                display_name = info[2] if len(info) > 2 else gw_name
                category = info[3] if len(info) > 3 else "other"
                description = info[4] if len(info) > 4 else ""
            else:
                display_name = gw_name
                category = "other"
                description = ""
            
            if category not in result:
                result[category] = []
            result[category].append((gw_name, display_name, description))
        
        return result
    
    def _create_gateway_card(self, gw_name: str, display_name: str, description: str) -> CardWidget:
        """创建 Gateway 卡片"""
        card = CardWidget(self)
        card.setFixedHeight(70)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(15)
        
        # 左侧：名称和描述
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = BodyLabel(display_name)
        name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(name_label)
        
        if description:
            desc_label = BodyLabel(description)
            desc_label.setStyleSheet("font-size: 11px; color: #888;")
            info_layout.addWidget(desc_label)
        
        card_layout.addLayout(info_layout)
        card_layout.addStretch()
        
        # 右侧：连接按钮
        connect_btn = PushButton(_("连接"))
        connect_btn.setFixedWidth(80)
        connect_btn.clicked.connect(partial(self.connect_gateway, gw_name))
        card_layout.addWidget(connect_btn)
        
        return card
    
    def connect_gateway(self, gateway_name: str):
        dialog = ConnectDialog(self.main_engine, gateway_name)
        dialog.exec()
    
    def edit_global_setting(self):
        dialog = GlobalDialog()
        dialog.exec()


class FluentMainWindow(FluentWindow):
    """
    Fluent Design style main window for VeighNa Trader.
    Uses navigation interface instead of dock widgets.
    """
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        super().__init__()
        
        self.main_engine = main_engine
        self.event_engine = event_engine
        
        self.window_title = _("量霸 Trader 内测版 - {}   [{}]").format(
            vnpy.__version__, TRADER_DIR
        )
        
        self.widgets: dict[str, QWidget] = {}
        self.monitors: dict[str, BaseMonitor] = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.window_title)
        self.setWindowIcon(QIcon(get_icon_path(__file__, "lbkj.ico")))
        self.resize(1400, 900)
        
        # Set navigation panel width (default is 322, make it narrower)
        self.navigationInterface.setExpandWidth(150)
        
        # Initialize navigation interfaces
        self.init_navigation()
        
        # Set default interface
        self.switchTo(self.trading_interface)
    
    def init_navigation(self):
        """Initialize the navigation interface with all sub-interfaces."""
        # Create interfaces
        self.trading_interface = TradingInterface(
            self.main_engine, self.event_engine, self
        )
        self.order_interface = OrderInterface(
            self.main_engine, self.event_engine, self
        )
        self.trade_interface = TradeInterface(
            self.main_engine, self.event_engine, self
        )
        self.position_interface = PositionInterface(
            self.main_engine, self.event_engine, self
        )
        self.log_interface = LogInterface(
            self.main_engine, self.event_engine, self
        )
        self.settings_interface = SettingsInterface(
            self.main_engine, self.event_engine, self
        )
        
        # Store monitors for saving settings
        self.monitors["tick"] = self.trading_interface.tick_monitor
        self.monitors["order"] = self.order_interface.order_monitor
        self.monitors["active"] = self.order_interface.active_monitor
        self.monitors["trade"] = self.trade_interface.trade_monitor
        self.monitors["position"] = self.position_interface.position_monitor
        self.monitors["account"] = self.position_interface.account_monitor
        self.monitors["log"] = self.log_interface.log_monitor
        
        # Connect position monitor double click to trading widget
        self.position_interface.position_monitor.itemDoubleClicked.connect(
            self.trading_interface.trading_widget.update_with_cell
        )
        
        # Add navigation items
        self.addSubInterface(
            self.trading_interface,
            FluentIcon.SHOPPING_CART,
            _("交易")
        )
        self.addSubInterface(
            self.order_interface,
            FluentIcon.DOCUMENT,
            _("委托")
        )
        self.addSubInterface(
            self.trade_interface,
            FluentIcon.HISTORY,
            _("成交")
        )
        self.addSubInterface(
            self.position_interface,
            FluentIcon.PIE_SINGLE,
            _("持仓")
        )
        self.addSubInterface(
            self.log_interface,
            FluentIcon.MESSAGE,
            _("日志")
        )
        
        # Add separator before apps
        self.navigationInterface.addSeparator()
        
        # Add app navigation items
        all_apps = self.main_engine.get_all_apps()
        for app in all_apps:
            self.add_app_interface(app)
        
        # Add bottom navigation items
        self.addSubInterface(
            self.settings_interface,
            FluentIcon.SETTING,
            _("设置"),
            NavigationItemPosition.BOTTOM
        )
        
        # Add help menu at bottom
        self.navigationInterface.addItem(
            routeKey="help",
            icon=FluentIcon.HELP,
            text=_("帮助"),
            onClick=self.show_help_menu,
            position=NavigationItemPosition.BOTTOM
        )
    
    def add_app_interface(self, app: BaseApp):
        """Add an app as a navigation item."""
        def open_app():
            self.open_widget(app)
        
        # Use app icon if available, otherwise use default
        try:
            icon = QIcon(app.icon_name) if app.icon_name else FluentIcon.APPLICATION
        except:
            icon = FluentIcon.APPLICATION
        
        self.navigationInterface.addItem(
            routeKey=app.app_name,
            icon=icon,
            text=app.display_name,
            onClick=open_app,
            position=NavigationItemPosition.SCROLL
        )
    
    def open_widget(self, app: BaseApp):
        """Open app widget."""
        widget = self.widgets.get(app.app_name, None)
        if not widget:
            ui_module: ModuleType = import_module(app.app_module + ".ui")
            widget_class = getattr(ui_module, app.widget_name)
            widget = widget_class(self.main_engine, self.event_engine)
            self.widgets[app.app_name] = widget
        
        widget.show()
        widget.raise_()
        widget.activateWindow()
    
    def show_help_menu(self):
        """Show help menu."""
        menu = RoundMenu(parent=self)
        
        # Query contracts
        contract_action = Action(FluentIcon.SEARCH, _("查询合约"))
        contract_action.triggered.connect(self.open_contract_manager)
        menu.addAction(contract_action)
        
        menu.addSeparator()
        
        # Test email
        email_action = Action(FluentIcon.MAIL, _("测试邮件"))
        email_action.triggered.connect(self.send_test_email)
        menu.addAction(email_action)
        
        # Forum
        forum_action = Action(FluentIcon.GLOBE, _("社区论坛"))
        forum_action.triggered.connect(self.open_forum)
        menu.addAction(forum_action)
        
        menu.addSeparator()
        
        # About
        about_action = Action(FluentIcon.INFO, _("关于"))
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        # Show menu at cursor position
        menu.exec(self.cursor().pos())
    
    def open_contract_manager(self):
        """Open contract manager widget."""
        widget = self.widgets.get("contract", None)
        if not widget:
            widget = ContractManager(self.main_engine, self.event_engine)
            self.widgets["contract"] = widget
        widget.show()
        widget.raise_()
    
    def send_test_email(self):
        """Send test email."""
        self.main_engine.send_email("MeowTrader", "testing", None)
    
    def open_forum(self):
        """Open forum website."""
        webbrowser.open("http://www.liangbax.com/liang-ba/")
    
    def show_about(self):
        """Show about dialog."""
        widget = self.widgets.get("about", None)
        if not widget:
            widget = AboutDialog(self.main_engine, self.event_engine)
            self.widgets["about"] = widget
        widget.exec()
    
    def closeEvent(self, event):
        """Handle close event."""
        w = MessageBox(
            _("退出"),
            _("确认退出？"),
            self
        )
        
        if w.exec():
            # Save all monitor settings
            for monitor in self.monitors.values():
                monitor.save_setting()
            
            # Close all widgets
            for widget in self.widgets.values():
                widget.close()
            
            # Close main engine
            self.main_engine.close()
            
            event.accept()
        else:
            event.ignore()
