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
    """
    Main application window for Liberty Mail Stream, a GUI-based email client using PyQt5.

    This class sets up the main window and integrates various components like a control panel, toolbar,
    menubar, and an email editing area. It provides features such as theme customization, window resizing,
    and docking panel management.

    Attributes:
        gmail_service: Instance used for Gmail service operations, handling email interactions.

    Args:
        gmail_service: A GmailService object for handling email operations.
    """
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
        """
        Initializes the main components of the window including layout, menubar, toolbar, and control panel.
        It sets the stylesheet based on user preferences and adds functionality for editor and subject input.
        """
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
        """
        Handles the resize event to adjust configuration settings based on the new window size.

        Args:
            event: The event object containing information about the resize event.
        """
        newSize = event.size()
        config.set_window_size(newSize.width(), newSize.height())
        super().resizeEvent(event)


    def setWindowSize(self):
        """
        Sets the initial window size based on preferences stored in the configuration.
        """
        width = config.get("PREFERENCES", "window_width")
        height = config.get("PREFERENCES", "window_height")
        self.resize(int(width), int(height))


    def on_topLevelChanged(self, floating):
        """
        Handles the event when a toolbar's docking state changes, updating the configuration accordingly.

        Args:
            floating: A boolean indicating whether the toolbar is floating or docked.
        """
        toolbar = self.sender()
        toolbar_name = toolbar.objectName()
        if floating:
            print(f"{toolbar_name} was undocked")
        else:
            area_name = self.getAreaName(toolbar)
            config.set("PREFERENCES", f"{toolbar_name}_location", area_name)


    def getAreaName(self, toolbar):
        """
        Determines the docking area of a toolbar and returns its name as a string.

        Args:
            toolbar: The toolbar whose area is being determined.
        """
        area = self.toolBarArea(toolbar)
        area_name = {
            Qt.LeftToolBarArea: "left", 
            Qt.RightToolBarArea: "right",
            Qt.TopToolBarArea: "top", 
            Qt.BottomToolBarArea: "bottom"
        }.get(area, "floating")
        return area_name


    def getToolbarArea(self, location_name="right"):
        """
        Retrieves the docking area for a toolbar based on a location name.

        Args:
            location_name (str, optional): The name of the location where the toolbar should be docked. Defaults to "right".
        """
        toolbar_area = {
            "left": Qt.LeftToolBarArea, 
            "right": Qt.RightToolBarArea,
            "top": Qt.TopToolBarArea, 
            "bottom": Qt.BottomToolBarArea
        }.get(config.get("PREFERENCES", location_name), "floating")
        return toolbar_area


    def toggleToolbarVisibility(self, state):
        """
        Toggles the visibility of the toolbar.

        Args:
            state: A boolean representing the desired visibility state.
        """
        config.set("PREFERENCES", "toolbar_toggle", f"{state}")
        self.toolbar.setVisible(state)


    def toggleControlPanelVisibility(self, state):
        """
        Toggles the visibility of the control panel.

        Args:
            state: A boolean representing the desired visibility state.
        """
        config.set("PREFERENCES", "control_panel_toggle", f"{state}")
        self.control_panel.setVisible(state)


    def toggleNightMode(self, state):
        """
        Toggles the application theme between light and dark modes based on the provided state.

        Args:
            state: A boolean indicating whether the dark mode should be enabled or not.
        """
        theme = "light"
        if state:
            theme = "dark"

        stylesheet = qdarktheme.load_stylesheet(theme=theme)
        QApplication.instance().setStyleSheet(stylesheet)
        config.set("PREFERENCES", "Theme", theme)
