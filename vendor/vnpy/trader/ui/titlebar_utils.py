"""
统一的标题栏样式工具函数
用于所有 FramelessWindow 和 FramelessDialog
"""
from PySide6.QtGui import QColor
from qframelesswindow.titlebar import StandardTitleBar


def setup_title_bar_style(title_bar: StandardTitleBar) -> None:
    """
    统一设置标题栏样式（深色主题）
    
    适用于所有 FramelessWindow 和 FramelessDialog
    
    Args:
        title_bar: StandardTitleBar 实例
    """
    # 设置标题栏背景色和边框
    title_bar.setStyleSheet("""
        StandardTitleBar {
            background-color: rgb(32, 32, 32);
            border-bottom: 1px solid rgb(60, 60, 60);
        }
    """)
    
    # 设置标题文字样式
    title_bar.titleLabel.setStyleSheet("""
        QLabel {
            background: transparent;
            color: white;
            font: 13px 'Segoe UI';
            padding: 0 4px;
        }
    """)
    
    # 设置窗口控制按钮颜色（白色，适配深色主题）
    white_color = QColor(255, 255, 255)
    for btn in [title_bar.minBtn, title_bar.maxBtn, title_bar.closeBtn]:
        btn.setNormalColor(white_color)
        btn.setHoverColor(white_color)
        btn.setPressedColor(white_color)
