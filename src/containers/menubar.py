from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QTextEdit

import json

from ..containers.preferences import PreferencesDialog

from ..utilities.config import config




class Menubar:
    """
    Handles the menubar for the main application window, providing file management, editing options, and preferences.

    This class sets up the menu bar in the PyQt5 application, allowing users to manage documents, edit content,
    and adjust application settings like theme and toolbars.

    Attributes:
        parent (QMainWindow): The parent window to which this menu bar belongs.
        editor (QTextEdit): A reference to the text editor widget used for displaying and editing the email content.
        document_name (str): The name of the currently loaded or new document, defaulting to "Untitled".

    Args:
        parent (QMainWindow): The main application window that hosts the menubar.
        editor (QTextEdit): The text editing widget where email content is managed.
    """
    def __init__(self, parent, editor):
        self.parent = parent
        self.editor: QTextEdit = editor
        self.initUI()
        self.document_name = "Untitled"


    def initUI(self):
        """
        Initializes the user interface components of the menu bar. It sets up the file, edit, view,
        and preferences menus with all corresponding actions and their functionalities.
        """
        menubar = self.parent.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("New File", self.parent)
        new_action.triggered.connect(self.newDocument)
        file_menu.addAction(new_action)

        file_menu.addSeparator() # -----------------------

        open_action = QAction("Open", self.parent)
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)

        file_menu.addSeparator() # -----------------------

        save_action = QAction("Save", self.parent)
        save_action.triggered.connect(self.saveFile)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self.parent)
        save_as_action.triggered.connect(self.saveAsFile)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator() # -----------------------

        preferences_action = QAction("Preferences", self.parent)
        preferences_action.triggered.connect(self.open_preferences)
        file_menu.addAction(preferences_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("Undo", self.parent)
        undo_action.triggered.connect(self.parent.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self.parent)
        redo_action.triggered.connect(self.parent.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator() # -----------------------

        copy_action = QAction("Copy", self.parent)
        copy_action.triggered.connect(self.parent.editor.copy)
        edit_menu.addAction(copy_action)

        cut_action = QAction("Cut", self.parent)
        cut_action.triggered.connect(self.parent.editor.cut)
        edit_menu.addAction(cut_action)

        paste_action = QAction("Paste", self.parent)
        paste_action.triggered.connect(self.parent.editor.paste)
        edit_menu.addAction(paste_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        toggle_toolbar_action = QAction("Toggle Toolbar", self.parent, checkable=True)
        toggle_toolbar_action.setChecked(config.get_bool("PREFERENCES", "toolbar_toggle"))
        toggle_toolbar_action.triggered.connect(self.parent.toggleToolbarVisibility)
        view_menu.addAction(toggle_toolbar_action)

        control_panel_action = QAction("Toggle Recipients", self.parent, checkable=True)
        control_panel_action.setChecked(config.get_bool("PREFERENCES", "control_panel_toggle"))
        control_panel_action.triggered.connect(self.parent.toggleControlPanelVisibility)
        view_menu.addAction(control_panel_action)

        view_menu.addSeparator() # -----------------------

        toggle_night_mode_action = QAction("Night Mode", self.parent, checkable=True)

        if config.get("PREFERENCES", "Theme") == "light":
            toggle_night_mode_action.setChecked(False)
        else:
            toggle_night_mode_action.setChecked(True)

        toggle_night_mode_action.triggered.connect(self.parent.toggleNightMode)
        view_menu.addAction(toggle_night_mode_action)


    def update_title(self):
        """
        Updates the title of the main window to reflect the current document name.
        """
        self.parent.setWindowTitle(f"{self.parent.title} - {self.document_name}")


    def newDocument(self):
        """
        Clears the current document content and resets the document name to 'Untitled'. Also updates the window title.
        """
        self.parent.editor.clear()
        self.document_name = "Untitled"
        self.update_title()


    def saveFile(self):
        """
        Saves the current document to a file using JSON format, storing details like subject and body.
        The file is saved under the current document name in a predefined templates directory.
        """
        data = {
            "subject": self.parent.subjectLineEdit.text(),
            "body": {
                "html": self.editor.toHtml()
            },
            "attachments": None
        }

        with open(f"templates/{self.document_name}.json", 'w') as file:
            json.dump(data, file, indent=4)


    def saveAsFile(self):
        """
        Opens a file dialog allowing the user to specify the filename and location for saving the current document.
        The content is saved in JSON format, and the document name is updated accordingly.
        """
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self.parent, "Save File", "", "JSON Files (*.json);;All Files (*)", options=options)

        file_name_with_extension = filePath.split("/")[-1]
        self.document_name = file_name_with_extension.removesuffix(".json")

        if filePath:
            data = {
                "subject": self.parent.subjectLineEdit.text(),
                "body": {
                    "html": self.editor.toHtml()
                },
                "attachments": None
            }

            with open(filePath, 'w') as file:
                json.dump(data, file, indent=4)
        self.update_title()


    def openFile(self):
        """
        Opens a file dialog to choose a document to load. The selected file's content is loaded into the editor,
        and the document name is updated based on the file name.
        """
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self.parent, "Open File", "", "JSON Files (*.json);;All Files (*)", options=options)
        file_name_with_extension = filePath.split("/")[-1]
        self.document_name = file_name_with_extension.removesuffix(".json")
        if filePath:
            with open(filePath, 'r') as file:
                data = json.load(file)
                subject = data.get('subject', '')
                # body_text = data.get('body', {}).get('text', '')
                body_html = data.get('body', {}).get('html', '')
                
                # Updating the UI components
                self.parent.subjectLineEdit.setText(subject)
                self.editor.setHtml(body_html)
        self.update_title()

    def open_preferences(self):
        """
        Opens a preferences dialog allowing the user to adjust application settings such as theme and toolbar visibility.
        """
        dialog = PreferencesDialog(self.parent)
        dialog.exec_()