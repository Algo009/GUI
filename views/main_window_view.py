"""Main application view following MVCS view guidelines."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class MainWindowView(QWidget):
    """Main window view responsible for building and managing the UI."""

    # ========================================
    # 区域1：信号定义区
    # ========================================
    menu_changed = Signal(str)
    save_requested = Signal()
    settings_requested = Signal()
    exit_requested = Signal()
    window_control_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self._menu_buttons: Dict[str, QPushButton] = {}
        self._menu_animation: QPropertyAnimation | None = None
        self._extra_left_animation: QPropertyAnimation | None = None
        self._extra_right_animation: QPropertyAnimation | None = None
        self._feedback_animation: QSequentialAnimationGroup | None = None
        self._feedback_opacity: QGraphicsOpacityEffect | None = None
        self._default_status_text = "By: Wanderson M. Pimenta"

        project_root = Path(__file__).resolve().parent.parent
        self._project_root = project_root
        self._icons_dir = project_root / "images" / "icons"
        self._images_dir = project_root / "images" / "images"

        self._build_ui()
        self._connect_signals()
        self._apply_styles()

        self._select_menu("home")
        self.set_form_enabled(True)
        self.show_status_message("Ready")
        logger.debug("%s 初始化完成", self.__class__.__name__)

    # ========================================
    # 区域2：UI构建主入口
    # ========================================
    def _build_ui(self) -> None:
        """构建用户界面 - 主入口"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.styleSheet = QFrame()
        self.styleSheet.setObjectName("styleSheet")
        style_layout = QVBoxLayout(self.styleSheet)
        style_layout.setContentsMargins(10, 10, 10, 10)
        style_layout.setSpacing(0)

        self.bgApp = QFrame()
        self.bgApp.setObjectName("bgApp")
        bg_layout = QHBoxLayout(self.bgApp)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)

        bg_layout.addWidget(self._create_left_menu())
        bg_layout.addWidget(self._create_extra_left_box())
        bg_layout.addWidget(self._create_content_box())

        style_layout.addWidget(self.bgApp)
        main_layout.addWidget(self.styleSheet)

        logger.debug("UI构建完成")

    # ========================================
    # 区域3：UI区域创建方法
    # ========================================
    def _create_left_menu(self) -> QFrame:
        self.leftMenuBg = QFrame()
        self.leftMenuBg.setObjectName("leftMenuBg")
        self.leftMenuBg.setMinimumWidth(240)
        self.leftMenuBg.setMaximumWidth(240)

        layout = QVBoxLayout(self.leftMenuBg)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top logo and titles
        self.topLogoInfo = QFrame()
        self.topLogoInfo.setObjectName("topLogoInfo")
        top_logo_layout = QHBoxLayout(self.topLogoInfo)
        top_logo_layout.setContentsMargins(15, 10, 15, 10)
        top_logo_layout.setSpacing(10)

        self.topLogo = QLabel()
        self.topLogo.setObjectName("topLogo")
        self.topLogo.setFixedSize(42, 42)
        logo_pixmap = self._load_pixmap("PyDracula_vertical.png", QSize(42, 42))
        if not logo_pixmap.isNull():
            self.topLogo.setPixmap(logo_pixmap)
            self.topLogo.setScaledContents(True)

        text_container = QFrame()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        title_font = QFont()
        title_font.setFamily("Segoe UI Semibold")
        title_font.setPointSize(12)

        description_font = QFont()
        description_font.setFamily("Segoe UI")
        description_font.setPointSize(8)

        self.titleLeftApp = QLabel("PyDracula")
        self.titleLeftApp.setObjectName("titleLeftApp")
        self.titleLeftApp.setFont(title_font)

        self.titleLeftDescription = QLabel("Modern GUI / Flat Style")
        self.titleLeftDescription.setObjectName("titleLeftDescription")
        self.titleLeftDescription.setFont(description_font)

        text_layout.addWidget(self.titleLeftApp)
        text_layout.addWidget(self.titleLeftDescription)
        text_layout.addStretch(1)

        top_logo_layout.addWidget(self.topLogo)
        top_logo_layout.addWidget(text_container)
        top_logo_layout.addStretch(1)

        layout.addWidget(self.topLogoInfo)

        # Menu buttons
        self.leftMenuFrame = QFrame()
        self.leftMenuFrame.setObjectName("leftMenuFrame")
        menu_layout = QVBoxLayout(self.leftMenuFrame)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)

        self.toggleBox = QFrame()
        self.toggleBox.setObjectName("toggleBox")
        toggle_layout = QVBoxLayout(self.toggleBox)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)

        self.toggleButton = QPushButton("Hide")
        self.toggleButton.setObjectName("toggleButton")
        self.toggleButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggleButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggleButton.setMinimumHeight(45)
        self._apply_icon(self.toggleButton, "icon_menu.png")
        toggle_layout.addWidget(self.toggleButton)

        menu_layout.addWidget(self.toggleBox)

        self.topMenu = QFrame()
        self.topMenu.setObjectName("topMenu")
        top_menu_layout = QVBoxLayout(self.topMenu)
        top_menu_layout.setContentsMargins(0, 0, 0, 0)
        top_menu_layout.setSpacing(0)

        def build_menu_button(name: str, text: str, icon: str, checkable: bool = True) -> QPushButton:
            button = QPushButton(text)
            button.setObjectName(name)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(45)
            button.setCheckable(checkable)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self._apply_icon(button, icon)
            top_menu_layout.addWidget(button)
            return button

        self.btn_home = build_menu_button("btn_home", "Home", "cil-home.png")
        self.btn_widgets = build_menu_button("btn_widgets", "Widgets", "cil-gamepad.png")
        self.btn_new = build_menu_button("btn_new", "New", "cil-file.png")
        self.btn_save = build_menu_button("btn_save", "Save", "cil-save.png", checkable=False)
        self.btn_exit = build_menu_button("btn_exit", "Exit", "cil-x.png", checkable=False)

        self._menu_buttons = {
            "home": self.btn_home,
            "widgets": self.btn_widgets,
            "new": self.btn_new,
        }

        menu_layout.addWidget(self.topMenu, stretch=1)

        self.bottomMenu = QFrame()
        self.bottomMenu.setObjectName("bottomMenu")
        bottom_layout = QVBoxLayout(self.bottomMenu)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)

        self.toggleLeftBox = QPushButton("Settings")
        self.toggleLeftBox.setObjectName("toggleLeftBox")
        self.toggleLeftBox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggleLeftBox.setMinimumHeight(45)
        self.toggleLeftBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._apply_icon(self.toggleLeftBox, "icon_settings.png")
        bottom_layout.addWidget(self.toggleLeftBox)

        menu_layout.addWidget(self.bottomMenu, 0, Qt.AlignmentFlag.AlignBottom)

        layout.addWidget(self.leftMenuFrame, 1)

        return self.leftMenuBg

    def _create_extra_left_box(self) -> QFrame:
        self.extraLeftBox = QFrame()
        self.extraLeftBox.setObjectName("extraLeftBox")
        self.extraLeftBox.setMinimumWidth(0)
        self.extraLeftBox.setMaximumWidth(0)

        layout = QVBoxLayout(self.extraLeftBox)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.extraTopBg = QFrame()
        self.extraTopBg.setObjectName("extraTopBg")
        self.extraTopBg.setMaximumHeight(50)
        top_layout = QVBoxLayout(self.extraTopBg)
        top_layout.setContentsMargins(10, 0, 10, 0)
        top_layout.setSpacing(0)

        self.extraTopLayout = QGridLayout()
        self.extraTopLayout.setContentsMargins(0, 0, 0, 0)
        self.extraTopLayout.setHorizontalSpacing(10)
        self.extraTopLayout.setVerticalSpacing(0)

        self.extraIcon = QLabel()
        self.extraIcon.setObjectName("extraIcon")
        self.extraIcon.setFixedSize(20, 20)
        self._apply_icon(self.extraIcon, "icon_settings.png", size=QSize(18, 18))

        self.extraLabel = QLabel("Settings")
        self.extraLabel.setObjectName("extraLabel")

        self.extraCloseColumnBtn = QPushButton()
        self.extraCloseColumnBtn.setObjectName("extraCloseColumnBtn")
        self.extraCloseColumnBtn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.extraCloseColumnBtn.setFixedSize(28, 28)
        self._apply_icon(self.extraCloseColumnBtn, "cil-x.png", QSize(18, 18))

        self.extraTopLayout.addWidget(self.extraIcon, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.extraTopLayout.addWidget(self.extraLabel, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        self.extraTopLayout.addWidget(self.extraCloseColumnBtn, 0, 2, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        top_layout.addLayout(self.extraTopLayout)
        layout.addWidget(self.extraTopBg)

        self.extraContent = QFrame()
        self.extraContent.setObjectName("extraContent")
        content_layout = QVBoxLayout(self.extraContent)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.extraTopMenu = QFrame()
        self.extraTopMenu.setObjectName("extraTopMenu")
        extra_menu_layout = QVBoxLayout(self.extraTopMenu)
        extra_menu_layout.setContentsMargins(0, 0, 0, 0)
        extra_menu_layout.setSpacing(0)

        def build_extra_button(name: str, text: str, icon: str) -> QPushButton:
            button = QPushButton(text)
            button.setObjectName(name)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(45)
            self._apply_icon(button, icon)
            extra_menu_layout.addWidget(button)
            return button

        self.btn_message = build_extra_button("btn_message", "Messages", "cil-envelope-open.png")
        self.btn_print = build_extra_button("btn_print", "Print", "cil-print.png")
        self.btn_logout = build_extra_button("btn_logout", "Logout", "cil-account-logout.png")

        content_layout.addWidget(self.extraTopMenu, 0, Qt.AlignmentFlag.AlignTop)

        self.extraCenter = QFrame()
        self.extraCenter.setObjectName("extraCenter")
        extra_center_layout = QVBoxLayout(self.extraCenter)
        extra_center_layout.setContentsMargins(10, 10, 10, 10)
        extra_center_layout.setSpacing(6)

        self.extraText = QTextEdit()
        self.extraText.setObjectName("textEdit")
        self.extraText.setReadOnly(True)
        self.extraText.setPlainText(
            "Change theme or configure additional options here.\n"
            "Use the controls above to explore auxiliary actions."
        )
        extra_center_layout.addWidget(self.extraText)

        content_layout.addWidget(self.extraCenter)

        self.extraBottom = QFrame()
        self.extraBottom.setObjectName("extraBottom")
        content_layout.addWidget(self.extraBottom)

        layout.addWidget(self.extraContent)

        return self.extraLeftBox

    def _create_content_box(self) -> QFrame:
        self.contentBox = QFrame()
        self.contentBox.setObjectName("contentBox")
        content_layout = QVBoxLayout(self.contentBox)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top bar
        self.contentTopBg = QFrame()
        self.contentTopBg.setObjectName("contentTopBg")
        self.contentTopBg.setMaximumHeight(50)
        top_layout = QHBoxLayout(self.contentTopBg)
        top_layout.setContentsMargins(0, 0, 10, 0)
        top_layout.setSpacing(0)

        self.leftBox = QFrame()
        self.leftBox.setObjectName("leftBox")
        left_layout = QHBoxLayout(self.leftBox)
        left_layout.setContentsMargins(20, 0, 0, 0)
        left_layout.setSpacing(0)

        self.titleRightInfo = QLabel("Home")
        self.titleRightInfo.setObjectName("titleRightInfo")
        info_font = QFont()
        info_font.setFamily("Segoe UI Semibold")
        info_font.setPointSize(12)
        self.titleRightInfo.setFont(info_font)
        left_layout.addWidget(self.titleRightInfo)

        top_layout.addWidget(self.leftBox)

        self.rightButtons = QFrame()
        self.rightButtons.setObjectName("rightButtons")
        right_layout = QHBoxLayout(self.rightButtons)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)

        self.settingsTopBtn = QPushButton()
        self.settingsTopBtn.setObjectName("settingsTopBtn")
        self.settingsTopBtn.setFixedSize(28, 28)
        self._apply_icon(self.settingsTopBtn, "icon_settings.png", QSize(20, 20))

        self.minimizeAppBtn = QPushButton()
        self.minimizeAppBtn.setObjectName("minimizeAppBtn")
        self.minimizeAppBtn.setFixedSize(28, 28)
        self._apply_icon(self.minimizeAppBtn, "icon_minimize.png", QSize(20, 20))

        self.maximizeRestoreAppBtn = QPushButton()
        self.maximizeRestoreAppBtn.setObjectName("maximizeRestoreAppBtn")
        self.maximizeRestoreAppBtn.setFixedSize(28, 28)
        self._apply_icon(self.maximizeRestoreAppBtn, "icon_restore.png", QSize(20, 20))

        self.closeAppBtn = QPushButton()
        self.closeAppBtn.setObjectName("closeAppBtn")
        self.closeAppBtn.setFixedSize(28, 28)
        self._apply_icon(self.closeAppBtn, "icon_close.png", QSize(20, 20))

        for button in (
            self.settingsTopBtn,
            self.minimizeAppBtn,
            self.maximizeRestoreAppBtn,
            self.closeAppBtn,
        ):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            right_layout.addWidget(button)

        top_layout.addWidget(self.rightButtons, 0, Qt.AlignmentFlag.AlignRight)

        content_layout.addWidget(self.contentTopBg)

        # Content area with stacked pages and right box
        self.contentBottom = QFrame()
        self.contentBottom.setObjectName("contentBottom")
        bottom_layout = QVBoxLayout(self.contentBottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)

        self.content = QFrame()
        self.content.setObjectName("content")
        central_layout = QHBoxLayout(self.content)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self.pagesContainer = QFrame()
        self.pagesContainer.setObjectName("pagesContainer")
        pages_layout = QVBoxLayout(self.pagesContainer)
        pages_layout.setContentsMargins(20, 20, 20, 20)
        pages_layout.setSpacing(10)

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.setObjectName("stackedWidget")

        self.home_page = self._build_home_page()
        self.widgets_page = self._build_widgets_page()
        self.new_page = self._build_new_page()

        self.stackedWidget.addWidget(self.home_page)
        self.stackedWidget.addWidget(self.widgets_page)
        self.stackedWidget.addWidget(self.new_page)

        pages_layout.addWidget(self.stackedWidget)

        self.loadingLabel = QLabel("Loading…")
        self.loadingLabel.setObjectName("loadingLabel")
        self.loadingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loadingLabel.hide()
        pages_layout.addWidget(self.loadingLabel)

        central_layout.addWidget(self.pagesContainer)

        self.extraRightBox = QFrame()
        self.extraRightBox.setObjectName("extraRightBox")
        self.extraRightBox.setMinimumWidth(0)
        self.extraRightBox.setMaximumWidth(0)
        extra_right_layout = QVBoxLayout(self.extraRightBox)
        extra_right_layout.setContentsMargins(0, 0, 0, 0)
        extra_right_layout.setSpacing(0)

        self.themeSettingsTopDetail = QFrame()
        self.themeSettingsTopDetail.setObjectName("themeSettingsTopDetail")
        self.themeSettingsTopDetail.setMaximumHeight(3)
        extra_right_layout.addWidget(self.themeSettingsTopDetail)

        self.contentSettings = QFrame()
        self.contentSettings.setObjectName("contentSettings")
        content_settings_layout = QVBoxLayout(self.contentSettings)
        content_settings_layout.setContentsMargins(0, 0, 0, 0)
        content_settings_layout.setSpacing(0)

        self.topMenus = QFrame()
        self.topMenus.setObjectName("topMenus")
        top_menus_layout = QVBoxLayout(self.topMenus)
        top_menus_layout.setContentsMargins(0, 0, 0, 0)
        top_menus_layout.setSpacing(0)

        self.btn_adjustments = QPushButton("Adjustments")
        self.btn_adjustments.setObjectName("btn_adjustments")
        self.btn_adjustments.setMinimumHeight(45)
        self._apply_icon(self.btn_adjustments, "cil-equalizer.png")

        self.btn_more = QPushButton("More")
        self.btn_more.setObjectName("btn_more")
        self.btn_more.setMinimumHeight(45)
        self._apply_icon(self.btn_more, "cil-layers.png")

        for button in (self.btn_adjustments, self.btn_more):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            top_menus_layout.addWidget(button)

        content_settings_layout.addWidget(self.topMenus, 0, Qt.AlignmentFlag.AlignTop)
        extra_right_layout.addWidget(self.contentSettings)

        central_layout.addWidget(self.extraRightBox)

        bottom_layout.addWidget(self.content)

        self.bottomBar = QFrame()
        self.bottomBar.setObjectName("bottomBar")
        bottom_bar_layout = QHBoxLayout(self.bottomBar)
        bottom_bar_layout.setContentsMargins(10, 0, 10, 0)
        bottom_bar_layout.setSpacing(0)

        self.creditsLabel = QLabel(self._default_status_text)
        self.creditsLabel.setObjectName("creditsLabel")
        self.creditsLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bottom_bar_layout.addWidget(self.creditsLabel)

        self.version = QLabel("v1.0.3")
        self.version.setObjectName("version")
        bottom_bar_layout.addWidget(self.version, 0, Qt.AlignmentFlag.AlignRight)

        self.frame_size_grip = QFrame()
        self.frame_size_grip.setObjectName("frame_size_grip")
        self.frame_size_grip.setFixedWidth(20)
        bottom_bar_layout.addWidget(self.frame_size_grip, 0, Qt.AlignmentFlag.AlignRight)

        bottom_layout.addWidget(self.bottomBar)

        content_layout.addWidget(self.contentTopBg)
        content_layout.addWidget(self.contentBottom)

        return self.contentBox

    def _build_home_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("home")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        hero = QLabel("PyDracula APP - Theme with colors based on Dracula for Python.")
        hero.setObjectName("homeLabel")
        hero.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_font = QFont()
        hero_font.setFamily("Segoe UI")
        hero_font.setPointSize(16)
        hero.setFont(hero_font)

        image = QLabel()
        image.setObjectName("homeImage")
        pixmap = self._load_pixmap("PyDracula.png")
        if not pixmap.isNull():
            image.setPixmap(pixmap)
            image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("PyDracula - Modern GUI")
        subtitle.setObjectName("homeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(24)
        subtitle_font.setBold(True)
        subtitle.setFont(subtitle_font)

        layout.addStretch(1)
        layout.addWidget(hero)
        layout.addWidget(image, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        layout.addStretch(1)

        return page

    def _build_widgets_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("widgets")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        label = QLabel("Available widgets")
        label.setObjectName("widgetsLabel")
        label_font = QFont()
        label_font.setPointSize(14)
        label.setFont(label_font)
        layout.addWidget(label)

        self.tableWidget = QTableWidget(0, 3)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Category", "Status"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setFrameShape(QFrame.Shape.NoFrame)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget.setAlternatingRowColors(True)

        layout.addWidget(self.tableWidget)

        return page

    def _build_new_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("new_page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        label = QLabel("Create something new")
        label.setObjectName("createLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_font = QFont()
        label_font.setPointSize(14)
        label.setFont(label_font)
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)

        return page

    # ========================================
    # 区域4：样式加载方法
    # ========================================
    def _apply_styles(self) -> None:
        """应用QSS样式"""
        qss_dir = self._project_root / "resources" / "qss"
        style_parts: List[str] = []

        icons_path = self._icons_dir.as_posix() + "/"
        images_path = self._images_dir.as_posix() + "/"

        for qss_file in (qss_dir / "common.qss", qss_dir / "main_window.qss"):
            if qss_file.exists():
                try:
                    qss_text = qss_file.read_text(encoding="utf-8")
                    qss_text = qss_text.replace(":/images/images/images/", images_path)
                    qss_text = qss_text.replace(":/images/images/", images_path)
                    qss_text = qss_text.replace(":/icons/images/icons/", icons_path)
                    style_parts.append(qss_text)
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
        self.toggleButton.clicked.connect(self.toggle_menu)
        self.toggleLeftBox.clicked.connect(self.toggle_extra_left_box)
        self.extraCloseColumnBtn.clicked.connect(self.toggle_extra_left_box)

        self.settingsTopBtn.clicked.connect(self._on_settings_clicked)
        self.btn_save.clicked.connect(self.save_requested.emit)
        self.btn_exit.clicked.connect(self.exit_requested.emit)

        for name, button in self._menu_buttons.items():
            button.clicked.connect(lambda checked=False, menu=name: self._on_menu_clicked(menu))

        self.minimizeAppBtn.clicked.connect(lambda: self._emit_window_control("minimize"))
        self.maximizeRestoreAppBtn.clicked.connect(lambda: self._emit_window_control("maximize"))
        self.closeAppBtn.clicked.connect(lambda: self._emit_window_control("close"))

        self.btn_adjustments.clicked.connect(lambda: self.show_message("Adjustments", "Adjustments panel coming soon."))
        self.btn_more.clicked.connect(lambda: self.show_message("More", "Additional tools will be added."))
        self.btn_message.clicked.connect(lambda: self.show_message("Messages", "No new messages."))
        self.btn_print.clicked.connect(lambda: self.show_message("Print", "Print service unavailable."))
        self.btn_logout.clicked.connect(lambda: self.show_message("Logout", "Logout handled by controller."))

    # ========================================
    # 区域6：数据接口方法
    # ========================================
    def get_table_data(self) -> List[Dict[str, Any]]:
        """获取表格数据"""
        data: List[Dict[str, Any]] = []
        for row in range(self.tableWidget.rowCount()):
            record = {
                "name": self._item_text(row, 0),
                "category": self._item_text(row, 1),
                "status": self._item_text(row, 2),
            }
            data.append(record)
        return data

    def set_table_data(self, data: List[Dict[str, Any]]) -> None:
        """设置表格数据"""
        self.tableWidget.setRowCount(len(data))
        for row, record in enumerate(data):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(record.get("name", "")))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(record.get("category", "")))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(record.get("status", "")))

    def clear_table(self) -> None:
        """清空表格数据"""
        self.tableWidget.setRowCount(0)

    # ========================================
    # 区域7：UI状态控制方法
    # ========================================
    def set_form_enabled(self, enabled: bool) -> None:
        """设置表单启用状态"""
        for button in self._menu_buttons.values():
            button.setEnabled(enabled)
        self.btn_save.setEnabled(enabled)
        self.btn_exit.setEnabled(enabled)
        self.toggleButton.setEnabled(enabled)
        self.toggleLeftBox.setEnabled(enabled)
        self.settingsTopBtn.setEnabled(enabled)
        self.minimizeAppBtn.setEnabled(enabled)
        self.maximizeRestoreAppBtn.setEnabled(enabled)
        self.closeAppBtn.setEnabled(enabled)

    def set_loading_visible(self, visible: bool) -> None:
        """设置加载指示器可见性"""
        self.loadingLabel.setVisible(visible)
        self.stackedWidget.setVisible(not visible)

    def set_toolbar_enabled(self, enabled: bool) -> None:
        """设置工具栏启用状态"""
        for button in (self.settingsTopBtn, self.minimizeAppBtn, self.maximizeRestoreAppBtn, self.closeAppBtn):
            button.setEnabled(enabled)

    # ========================================
    # 区域8：UI动画控制方法
    # ========================================
    def toggle_menu(self) -> None:
        """切换左侧菜单展开/收起"""
        current_width = self.leftMenuBg.width()
        expanded = 240
        collapsed = 60
        target = collapsed if current_width > collapsed else expanded

        self.leftMenuBg.setMaximumWidth(240)
        animation = QPropertyAnimation(self.leftMenuBg, b"minimumWidth")
        animation.setDuration(300)
        animation.setStartValue(current_width)
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def finalize() -> None:
            self.leftMenuBg.setMinimumWidth(target)
            self.leftMenuBg.setMaximumWidth(target)

        animation.finished.connect(finalize)
        animation.start()
        self._menu_animation = animation

    def toggle_extra_left_box(self) -> None:
        """切换额外左侧菜单"""
        current_width = self.extraLeftBox.width()
        expanded = 240
        collapsed = 0
        target = collapsed if current_width > collapsed else expanded

        animation = QPropertyAnimation(self.extraLeftBox, b"minimumWidth")
        animation.setDuration(300)
        animation.setStartValue(current_width)
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def finalize() -> None:
            self.extraLeftBox.setMinimumWidth(target)
            self.extraLeftBox.setMaximumWidth(target)

        animation.finished.connect(finalize)
        animation.start()
        self._extra_left_animation = animation

    def toggle_extra_right_box(self) -> None:
        """切换右侧设置面板"""
        current_width = self.extraRightBox.width()
        expanded = 240
        collapsed = 0
        target = collapsed if current_width > collapsed else expanded

        animation = QPropertyAnimation(self.extraRightBox, b"minimumWidth")
        animation.setDuration(300)
        animation.setStartValue(current_width)
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def finalize() -> None:
            self.extraRightBox.setMinimumWidth(target)
            self.extraRightBox.setMaximumWidth(target)

        animation.finished.connect(finalize)
        animation.start()
        self._extra_right_animation = animation

    def show_success_animation(self, message: str = "Saved successfully!") -> None:
        """显示成功动画"""
        self.creditsLabel.setText(message)
        if self._feedback_opacity is None:
            self._feedback_opacity = QGraphicsOpacityEffect(self.creditsLabel)
            self.creditsLabel.setGraphicsEffect(self._feedback_opacity)

        fade_in = QPropertyAnimation(self._feedback_opacity, b"opacity")
        fade_in.setDuration(200)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)

        fade_out = QPropertyAnimation(self._feedback_opacity, b"opacity")
        fade_out.setDuration(400)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        def reset_text() -> None:
            self.creditsLabel.setGraphicsEffect(None)
            self.creditsLabel.setText(self._default_status_text)
            self._feedback_opacity = None

        animation_group = QSequentialAnimationGroup()
        animation_group.addAnimation(fade_in)
        animation_group.addPause(1200)
        animation_group.addAnimation(fade_out)
        animation_group.finished.connect(reset_text)
        animation_group.start()
        self._feedback_animation = animation_group

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
        self.creditsLabel.setText(message)
        if duration:
            QTimer.singleShot(duration, lambda: self.creditsLabel.setText(self._default_status_text))

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

        index_map = {"home": 0, "widgets": 1, "new": 2}
        if menu in index_map:
            self.stackedWidget.setCurrentIndex(index_map[menu])

        page_title = menu.replace("_", " ").title()
        self.titleRightInfo.setText(page_title)

    def _emit_window_control(self, action: str) -> None:
        """发射窗口控制信号"""
        self.window_control_requested.emit(action)

    def _on_settings_clicked(self) -> None:
        """设置按钮点击处理"""
        self.toggle_extra_right_box()
        self.settings_requested.emit()

    def _apply_icon(self, widget: QPushButton | QLabel, icon_name: str, size: QSize | None = None) -> None:
        """为控件应用图标，如果资源存在"""
        icon_path = self._icons_dir / icon_name
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            if isinstance(widget, QPushButton):
                widget.setIcon(icon)
                widget.setIconSize(size or QSize(20, 20))
            elif isinstance(widget, QLabel):
                pixmap = QPixmap(str(icon_path))
                if size:
                    pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                widget.setPixmap(pixmap)

    def _item_text(self, row: int, column: int) -> str:
        item = self.tableWidget.item(row, column)
        return item.text() if item else ""

    def _load_pixmap(self, file_name: str, size: QSize | None = None) -> QPixmap:
        """加载位图资源"""
        image_path = self._images_dir / file_name
        if not image_path.exists():
            return QPixmap()
        pixmap = QPixmap(str(image_path))
        if size is not None and not pixmap.isNull():
            pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return pixmap

    def _format_currency(self, value: float) -> str:
        """格式化货币显示"""
        return f"¥{value:,.2f}"

    def _validate_input_format(self, text: str) -> bool:
        """验证输入格式（仅格式检查，不含业务验证）"""
        return bool(text.strip())
