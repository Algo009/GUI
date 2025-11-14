"""Main application view following MVCS view guidelines."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QTimer, Signal, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import logging

logger = logging.getLogger(__name__)


class MainWindowView(QWidget):
    """Main window view responsible for building and managing the UI."""

    # ========================================
    # 区域1：信号定义区
    # ========================================
    menu_changed = Signal(str)
    save_requested = Signal()
    settings_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._menu_buttons: Dict[str, QPushButton] = {}
        self._menu_pages: Dict[str, QWidget] = {}
        self._menu_animation: QPropertyAnimation | None = None
        self._feedback_animation: QSequentialAnimationGroup | None = None

        self._build_ui()
        self._connect_signals()
        self._apply_styles()

        self._select_menu("home")
        self.set_form_enabled(True)
        logger.debug("%s 初始化完成", self.__class__.__name__)

    # ========================================
    # 区域2：UI构建主入口
    # ========================================
    def _build_ui(self) -> None:
        """构建用户界面 - 主入口"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_body())

        logger.debug("UI构建完成")

    # ========================================
    # 区域3：UI区域创建方法
    # ========================================
    def _create_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("headerBar")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(16)

        self.title_label = QLabel("PyDracula - Modern GUI")
        self.title_label.setObjectName("titleLabel")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        self.subtitle_label = QLabel("Theme inspired by Dracula palette")
        self.subtitle_label.setObjectName("subtitleLabel")

        text_wrapper = QWidget()
        text_layout = QVBoxLayout(text_wrapper)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)

        self.feedback_label = QLabel()
        self.feedback_label.setObjectName("feedbackLabel")
        self.feedback_label.hide()
        self.feedback_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._feedback_opacity = QGraphicsOpacityEffect(self.feedback_label)
        self.feedback_label.setGraphicsEffect(self._feedback_opacity)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(text_wrapper, stretch=2)
        layout.addWidget(self.feedback_label, stretch=2)
        layout.addWidget(self.status_label, stretch=1)

        return header

    def _create_body(self) -> QWidget:
        body = QWidget()
        body.setObjectName("contentArea")

        layout = QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._create_left_menu())
        layout.addWidget(self._create_content())

        return body

    def _create_left_menu(self) -> QWidget:
        self.left_menu = QFrame()
        self.left_menu.setObjectName("leftMenu")
        self.left_menu.setMinimumWidth(220)
        self.left_menu.setMaximumWidth(220)

        layout = QVBoxLayout(self.left_menu)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.toggle_menu_button = QPushButton("☰")
        self.toggle_menu_button.setObjectName("toggleMenuButton")
        self.toggle_menu_button.setToolTip("Toggle menu")
        self.toggle_menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.toggle_menu_button)

        def build_menu_button(name: str, text: str, icon_path: str | None = None, register: bool = True) -> QPushButton:
            button = QPushButton(text)
            button.setObjectName(f"menuButton_{name}")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)
            if icon_path:
                icon_file = Path(icon_path)
                if icon_file.exists():
                    button.setIcon(QIcon(str(icon_file)))
            layout.addWidget(button)
            if register:
                self._menu_buttons[name] = button
            return button

        build_menu_button("home", "Home")
        build_menu_button("widgets", "Widgets")
        build_menu_button("create", "Create")

        self.save_button = build_menu_button("save", "Save", register=False)
        self.save_button.setCheckable(False)
        self.save_button.setObjectName("saveButton")

        layout.addStretch(1)

        self.settings_button = QPushButton("Settings")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.settings_button)

        return self.left_menu

    def _create_content(self) -> QWidget:
        content = QWidget()
        content.setObjectName("mainContent")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stackedPages")

        self.home_page = self._build_home_page()
        self.widgets_page = self._build_widgets_page()
        self.create_page = self._build_create_page()

        self._menu_pages = {
            "home": self.home_page,
            "widgets": self.widgets_page,
            "create": self.create_page,
        }
        for page in self._menu_pages.values():
            self.stacked_widget.addWidget(page)

        self.loading_indicator = QLabel("Loading…")
        self.loading_indicator.setObjectName("loadingIndicator")
        self.loading_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_indicator.hide()

        layout.addWidget(self.stacked_widget)
        layout.addWidget(self.loading_indicator)

        return content

    def _build_home_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("homePage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        hero = QLabel("Welcome back!")
        hero.setObjectName("homeHeroLabel")
        hero_font = QFont()
        hero_font.setPointSize(18)
        hero_font.setBold(True)
        hero.setFont(hero_font)

        body = QLabel(
            "Use the navigation menu to explore widgets or create new content."
        )
        body.setObjectName("homeBodyLabel")
        body.setWordWrap(True)

        layout.addWidget(hero)
        layout.addWidget(body)
        layout.addStretch(1)

        return page

    def _build_widgets_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("widgetsPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        description = QLabel("Available widgets")
        description.setObjectName("widgetsDescription")
        description_font = QFont()
        description_font.setPointSize(12)
        description.setFont(description_font)

        self.widgets_table = QTableWidget(0, 3)
        self.widgets_table.setObjectName("widgetsTable")
        self.widgets_table.setHorizontalHeaderLabels(["Name", "Category", "Status"])
        self.widgets_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(description)
        layout.addWidget(self.widgets_table)

        return page

    def _build_create_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("createPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        info = QLabel("Create something new")
        info.setObjectName("createInfoLabel")
        info_font = QFont()
        info_font.setPointSize(12)
        info.setFont(info_font)

        layout.addWidget(info)
        layout.addStretch(1)

        return page

    # ========================================
    # 区域4：样式加载方法
    # ========================================
    def _apply_styles(self) -> None:
        """应用QSS样式"""
        project_root = Path(__file__).resolve().parent.parent
        qss_dir = project_root / "resources" / "qss"

        style_parts: List[str] = []
        common_qss = qss_dir / "common.qss"
        main_qss = qss_dir / "main_window.qss"

        for qss_file in (common_qss, main_qss):
            if qss_file.exists():
                try:
                    style_parts.append(qss_file.read_text(encoding="utf-8"))
                    logger.debug("QSS加载成功: %s", qss_file)
                except OSError as exc:
                    logger.error("QSS加载失败 %s: %s", qss_file, exc)

        if style_parts:
            self.setStyleSheet("\n\n".join(style_parts))
        else:
            logger.warning("未找到任何QSS样式文件")

    # ========================================
    # 区域5：信号连接方法
    # ========================================
    def _connect_signals(self) -> None:
        """连接内部信号"""
        self.toggle_menu_button.clicked.connect(self.toggle_menu)
        self.settings_button.clicked.connect(self.settings_requested.emit)
        self.save_button.clicked.connect(self.save_requested.emit)

        for name, button in self._menu_buttons.items():
            button.clicked.connect(lambda checked=False, menu=name: self._on_menu_clicked(menu))

    # ========================================
    # 区域6：数据接口方法
    # ========================================
    def get_table_data(self) -> List[Dict[str, Any]]:
        """获取表格数据"""
        data: List[Dict[str, Any]] = []
        for row in range(self.widgets_table.rowCount()):
            record = {
                "name": self.widgets_table.item(row, 0).text() if self.widgets_table.item(row, 0) else "",
                "category": self.widgets_table.item(row, 1).text() if self.widgets_table.item(row, 1) else "",
                "status": self.widgets_table.item(row, 2).text() if self.widgets_table.item(row, 2) else "",
            }
            data.append(record)
        return data

    def set_table_data(self, data: List[Dict[str, Any]]) -> None:
        """设置表格数据"""
        self.widgets_table.setRowCount(len(data))
        for row, record in enumerate(data):
            self.widgets_table.setItem(row, 0, QTableWidgetItem(record.get("name", "")))
            self.widgets_table.setItem(row, 1, QTableWidgetItem(record.get("category", "")))
            self.widgets_table.setItem(row, 2, QTableWidgetItem(record.get("status", "")))

    def clear_table(self) -> None:
        """清空表格数据"""
        self.widgets_table.setRowCount(0)

    # ========================================
    # 区域7：UI状态控制方法
    # ========================================
    def set_form_enabled(self, enabled: bool) -> None:
        """设置表单启用状态"""
        for button in self._menu_buttons.values():
            button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)

    def set_loading_visible(self, visible: bool) -> None:
        """设置加载指示器可见性"""
        self.loading_indicator.setVisible(visible)
        self.stacked_widget.setVisible(not visible)

    def set_toolbar_enabled(self, enabled: bool) -> None:
        """设置工具栏启用状态"""
        self.toggle_menu_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)

    # ========================================
    # 区域8：UI动画控制方法
    # ========================================
    def toggle_menu(self) -> None:
        """切换左侧菜单展开/收起"""
        current_width = self.left_menu.width()
        expanded = 220
        collapsed = 72
        target = collapsed if current_width > collapsed else expanded

        self._menu_animation = QPropertyAnimation(self.left_menu, b"minimumWidth")
        self._menu_animation.setDuration(250)
        self._menu_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._menu_animation.setStartValue(current_width)
        self._menu_animation.setEndValue(target)
        self._menu_animation.finished.connect(lambda: self.left_menu.setMaximumWidth(target))
        self._menu_animation.start()

    def animate_panel_slide(self, left_width: int, right_width: int) -> None:
        """面板滑动动画（保留扩展接口）"""
        logger.debug("animate_panel_slide called with left=%s right=%s", left_width, right_width)

    def show_success_animation(self, message: str = "Saved successfully!") -> None:
        """显示成功动画"""
        self.feedback_label.setText(message)
        self.feedback_label.show()

        fade_in = QPropertyAnimation(self._feedback_opacity, b"opacity")
        fade_in.setDuration(200)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)

        fade_out = QPropertyAnimation(self._feedback_opacity, b"opacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        self._feedback_animation = QSequentialAnimationGroup()
        self._feedback_animation.addAnimation(fade_in)
        self._feedback_animation.addPause(1200)
        self._feedback_animation.addAnimation(fade_out)
        self._feedback_animation.finished.connect(self.feedback_label.hide)
        self._feedback_animation.start()

    # ========================================
    # 区域9：用户反馈方法
    # ========================================
    def show_message(self, title: str, message: str, msg_type: str = "info") -> None:
        """显示消息对话框"""
        if msg_type == "info":
            QMessageBox.information(self, title, message)
        elif msg_type == "warning":
            QMessageBox.warning(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
        elif msg_type == "success":
            QMessageBox.information(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    def show_confirmation(self, title: str, message: str) -> bool:
        """显示确认对话框"""
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def show_status_message(self, message: str, duration: int = 3000) -> None:
        """显示状态栏消息"""
        self.status_label.setText(message)
        if duration:
            QTimer.singleShot(duration, lambda: self.status_label.setText("Ready"))

    # ========================================
    # 区域10：辅助方法区
    # ========================================
    def _on_menu_clicked(self, menu: str) -> None:
        """菜单按钮点击处理"""
        self._select_menu(menu)
        self.menu_changed.emit(menu)
        logger.debug("Menu changed: %s", menu)

    def _select_menu(self, menu: str) -> None:
        """选择菜单并更新界面"""
        for name, button in self._menu_buttons.items():
            is_selected = name == menu
            button.setChecked(is_selected)
            button.setProperty("selected", is_selected)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

        if menu in self._menu_pages:
            self.stacked_widget.setCurrentWidget(self._menu_pages[menu])
            page_title = menu.replace("_", " ").title()
            self.subtitle_label.setText(f"Currently viewing: {page_title}")

    def _format_currency(self, value: float) -> str:
        """格式化货币显示"""
        return f"¥{value:,.2f}"

    def _validate_input_format(self, text: str) -> bool:
        """验证输入格式（仅格式检查，不含业务验证）"""
        return bool(text.strip())
