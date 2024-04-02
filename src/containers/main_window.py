from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QApplication

from PyQt5.QtGui import QIcon

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer

from ..utilities.resource_path import resource_path
from ..utilities.config import config

from .control_panel import ControlPanel
from .toolbar import Toolbar
from .menubar import Menubar

import qdarktheme



class LibertyMailstream(QMainWindow):
    def __init__(self, gmail_service):
        super().__init__()
        self.gmail_service = gmail_service
        self.title = "Liberty Mail Stream"
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(resource_path('img\icons\logo.png')))
        self.setMinimumSize(512, 256)
        self.setWindowSize()
        self.init_main_window()
        
    def init_main_window(self):
        stylesheet = qdarktheme.load_stylesheet(theme=config.get("PREFERENCES", "Theme"))
        QApplication.instance().setStyleSheet(stylesheet)

        # Main layout container
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.layout = QVBoxLayout()
        self.mainWidget.setLayout(self.layout)

        # Subject input field
        self.subjectLineEdit = QLineEdit()
        self.subjectLineEdit.setPlaceholderText("Subject")
        self.layout.addWidget(self.subjectLineEdit)

        # Editor
        self.editor = QTextEdit()
        self.layout.addWidget(self.editor)

        # Initialize the menubar and toolbar with the editor
        self.menubar = Menubar(self, self.editor)
        self.toolbar = Toolbar(self, self.editor)
        self.addToolBar(self.getToolbarArea("toolbar_location"), self.toolbar)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.topLevelChanged.connect(self.on_topLevelChanged)


        # Recipients Toolbar
        self.control_panel = ControlPanel(self)
        self.control_panel.setObjectName("control_panel")
        self.addToolBar(self.getToolbarArea("control_panel_location"), self.control_panel)
        self.control_panel.topLevelChanged.connect(self.on_topLevelChanged)


        self.toolbar.setVisible(config.get_bool("PREFERENCES", "toolbar_toggle"))
        self.control_panel.setVisible(config.get_bool("PREFERENCES", "control_panel_toggle"))

    def resizeEvent(self, event):
        newSize = event.size()
        config.set_window_size(newSize.width(), newSize.height())
        super().resizeEvent(event)

    def setWindowSize(self):
        width = config.get("PREFERENCES", "window_width")
        height = config.get("PREFERENCES", "window_height")
        self.resize(int(width), int(height))

    def on_topLevelChanged(self, floating):
        toolbar = self.sender()
        toolbar_name = toolbar.objectName()
        if floating:
            print(f"{toolbar_name} was undocked")
        else:
            area_name = self.getAreaName(toolbar)
            config.set("PREFERENCES", f"{toolbar_name}_location", area_name)


    def getAreaName(self, toolbar):
        area = self.toolBarArea(toolbar)
        area_name = {
            Qt.LeftToolBarArea: "left", 
            Qt.RightToolBarArea: "right",
            Qt.TopToolBarArea: "top", 
            Qt.BottomToolBarArea: "bottom"
        }.get(area, "floating")
        return area_name


    def getToolbarArea(self, location_name="right"):
        toolbar_area = {
            "left": Qt.LeftToolBarArea, 
            "right": Qt.RightToolBarArea,
            "top": Qt.TopToolBarArea, 
            "bottom": Qt.BottomToolBarArea
        }.get(config.get("PREFERENCES", location_name), "floating")
        return toolbar_area


    def toggleToolbarVisibility(self, state):
        config.set("PREFERENCES", "toolbar_toggle", f"{state}")
        self.toolbar.setVisible(state)


    def toggleControlPanelVisibility(self, state):
        config.set("PREFERENCES", "control_panel_toggle", f"{state}")
        self.control_panel.setVisible(state)


    def toggleNightMode(self, state):
        theme = "light"
        if state:
            theme = "dark"

        stylesheet = qdarktheme.load_stylesheet(theme=theme)
        QApplication.instance().setStyleSheet(stylesheet)
        config.set("PREFERENCES", "Theme", theme)
