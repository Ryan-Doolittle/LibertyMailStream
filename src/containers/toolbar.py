from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolBar, QAction, QFontComboBox, QSpinBox, QTextEdit, QColorDialog, QInputDialog, QToolButton, QWidgetAction
from PyQt5.QtGui import QIcon, QFont, QTextListFormat, QTextCursor, QTextCharFormat

from ..utilities.resource_path import resource_path
from ..utilities.config import config


class Toolbar(QToolBar):
    """
    A toolbar for a text editor within a PyQt application, providing formatting tools, color pickers,
    and list management.

    This class enables easy access to common text editing functions like font style and size adjustments,
    text alignment, and list formatting. It also includes color pickers for text and background colors,
    and actions for inserting hyperlinks.

    Attributes:
        parent (QWidget): The parent widget, typically the main application window.
        editor (QTextEdit): The text editor widget where these formatting actions will be applied.
    
    Args:
        parent (QWidget): The parent window that hosts this toolbar.
        editor (QTextEdit): The text editing widget controlled by this toolbar.
    """
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor: QTextEdit = editor
        default_font_family = config.get("PREFERENCES", "default_font_family")
        default_font_size = int(config.get("PREFERENCES", "default_font_size"))

        # Set the default font and size
        self.editor.setFont(QFont(default_font_family, default_font_size))
        self.setWindowTitle('Toolbar')
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface of the toolbar, adding various widgets and actions like font selectors,
        color pickers, and text formatting buttons.
        """
        # Font Selector
        self.fontBox = QFontComboBox(self)
        default_font_family = config.get("PREFERENCES", "default_font_family")
        self.fontBox.setCurrentFont(QFont(default_font_family))
        self.fontBox.activated.connect(lambda: self.setFont(self.fontBox.currentFont().family()))

        # Font Size Selector
        self.fontSizeBox = QSpinBox(self)
        self.fontSizeBox.setMinimum(1)
        self.fontSizeBox.setMaximum(100)
        default_font_size = int(config.get("PREFERENCES", "default_font_size"))
        self.fontSizeBox.setValue(default_font_size)
        self.fontSizeBox.valueChanged.connect(lambda: self.setFontSize(self.fontSizeBox.value()))

        # Adding Widgets to Toolbar
        self.addWidget(self.fontBox)
        self.addWidget(self.fontSizeBox)

        # Color Picker for Text Color
        self.colorPickerButton = QToolButton(self)
        self.colorPickerButton.setAutoFillBackground(True)
        self.updateButtonColor(self.editor.textColor())
        self.colorPickerButton.setFixedSize(24, 24)
        self.colorPickerButton.clicked.connect(self.setTextColor)

        # Color Picker for Background Color
        self.bgColorPickerButton = QToolButton(self)
        self.bgColorPickerButton.setAutoFillBackground(True)
        self.updateButtonColor(self.editor.textBackgroundColor())
        self.bgColorPickerButton.setFixedSize(24, 24)
        self.bgColorPickerButton.clicked.connect(self.setTextBackgroundColor)

        # Actions for color pickers
        colorPickerAction = QWidgetAction(self)
        colorPickerAction.setDefaultWidget(self.colorPickerButton)
        self.addAction(colorPickerAction)

        backgroundColorPickerAction = QWidgetAction(self)
        backgroundColorPickerAction.setDefaultWidget(self.bgColorPickerButton)
        self.addAction(backgroundColorPickerAction)

        # Heading Styles
        self.addSeparator()
        self.addHeadingAction("H1", 24)
        self.addHeadingAction("H2", 18)
        self.addHeadingAction("H3", 14)

        # Text Style Actions
        self.addSeparator()
        self.addTextAction("Bold", resource_path("img/icons/bold.png"), self.toggleBoldText)
        self.addTextAction("Italic", resource_path("img/icons/italic.png"), self.toggleItalicText)
        self.addTextAction("Underline", resource_path("img/icons/underline.png"), self.toggleUnderlineText)

        # Alignment Actions
        self.addSeparator()
        self.addAlignmentAction("Align Left", resource_path("img/icons/align_left.png"), Qt.AlignLeft)
        self.addAlignmentAction("Align Center", resource_path("img/icons/align_center.png"), Qt.AlignCenter)
        self.addAlignmentAction("Align Right", resource_path("img/icons/align_right.png"), Qt.AlignRight)

        # List Actions
        self.addSeparator()
        self.addTextAction("Ordered List", resource_path("img/icons/ol.png"), lambda: self.setList(QTextListFormat.ListDecimal))
        self.addTextAction("Unordered List", resource_path("img/icons/ul.png"), lambda: self.setList(QTextListFormat.ListDisc))
        self.addTextAction("Insert Hyperlink", resource_path("img/icons/hyperlink.png"), self.insertHyperlink)

    def addTextAction(self, title, iconPath, function):
        """
        Adds a text formatting action to the toolbar with an icon.

        Args:
            title (str): The title of the action.
            iconPath (str): The file path to the icon representing the action.
            function (function): The function to execute when the action is triggered.
        """
        action = QAction(QIcon(iconPath), title, self)
        action.triggered.connect(function)
        self.addAction(action)

    def addAlignmentAction(self, title, iconPath, alignment):
        """
        Adds a text alignment action to the toolbar.

        Args:
            title (str): The title of the action.
            iconPath (str): The file path to the icon.
            alignment (Qt.AlignmentFlag): The alignment to apply to the text.
        """
        action = QAction(QIcon(iconPath), title, self)
        action.triggered.connect(lambda: self.editor.setAlignment(alignment))
        self.addAction(action)

    def setFont(self, fontName):
        """
        Sets the font family of the selected text or the current cursor position in the text editor.

        Args:
            fontName (str): The name of the font to apply.
        """
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            currentFormat = cursor.charFormat()
            currentFormat.setFontFamily(fontName)
            cursor.setCharFormat(currentFormat)
        else:
            newFormat = QTextCharFormat()
            newFormat.setFontFamily(fontName)
            self.editor.mergeCurrentCharFormat(newFormat)
        self.editor.setFocus()


    def setFontSize(self, size):
        """
        Sets the font size of the selected text or the current cursor position in the text editor.

        Args:
            size (int): The size of the font to apply.
        """
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            currentFormat = cursor.charFormat()
            currentFormat.setFontPointSize(size)
            cursor.setCharFormat(currentFormat)
        else:
            newFormat = QTextCharFormat()
            newFormat.setFontPointSize(size)
            self.editor.mergeCurrentCharFormat(newFormat)
        self.editor.setFocus()

    def toggleBoldText(self):
        """
        Toggles the bold styling of the selected text or the current cursor position in the text editor.
        """
        cursor = self.editor.textCursor()
        currentFormat = cursor.charFormat()
        currentFormat.setFontWeight(QFont.Bold if currentFormat.fontWeight() != QFont.Bold else QFont.Normal)
        cursor.setCharFormat(currentFormat)

    def toggleItalicText(self):
        """
        Toggles the italic styling of the selected text or the current cursor position.
        """
        cursor = self.editor.textCursor()
        currentFormat = cursor.charFormat()
        currentFormat.setFontItalic(not currentFormat.fontItalic())
        cursor.setCharFormat(currentFormat)

    def toggleUnderlineText(self):
        """
        Toggles the underline styling of the selected text or the current cursor position.
        """
        cursor = self.editor.textCursor()
        currentFormat = cursor.charFormat()
        currentFormat.setFontUnderline(not currentFormat.fontUnderline())
        cursor.setCharFormat(currentFormat)

    def setTextBackgroundColor(self):
        """
        Opens a color dialog to select a background color and applies it to the selected text.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            self.editor.setTextBackgroundColor(color)
            self.bgColorPickerButton.setStyleSheet(f"background-color: {color.name()};")

    def setTextColor(self):
        """
        Opens a color dialog to select a text color and applies it to the selected text.
        """
        color = QColorDialog.getColor(self.editor.textColor())
        if color.isValid():
            self.editor.setTextColor(color)
            self.updateButtonColor(color)


    def updateButtonColor(self, color):
        """
        Updates the background color of the color picker button to reflect the current text color.

        Args:
            color (QColor): The color to apply to the button's background.
        """
        self.colorPickerButton.setStyleSheet(f"background-color: {color.name()}; border: none;")


    def setList(self, listStyle):
        """
        Applies the specified list style to the current selection in the text editor.

        Args:
            listStyle (QTextListFormat.Style): The list style to apply.
        """
        cursor = self.editor.textCursor()
        listFormat = QTextListFormat()
        listFormat.setStyle(listStyle)
        cursor.createList(listFormat)


    def insertHyperlink(self):
        """
        Opens a dialog to input a URL and inserts a hyperlink at the current cursor position in the text editor.
        """
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setLabelText("Enter URL:")
        dialog.setWindowTitle("Insert Hyperlink")
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: #f0f0f0;
            }
            QLabel, QLineEdit {
                color: #333;
            }
        """)
        ok = dialog.exec_()
        url = dialog.textValue()
        if ok and url:
            text = self.editor.textCursor().selectedText()
            if not text:
                text = url
            self.editor.insertHtml(f'<a href="{url}">{text}</a>')


    def addHeadingAction(self, title, size):
        """
        Adds a heading style action to the toolbar.

        Args:
            title (str): The text of the action.
            size (int): The font size to apply when this heading style is activated.
        """
        action = QAction(title, self)
        action.triggered.connect(lambda: self.toggleHeadingStyle(size, QFont.Bold if size > 12 else QFont.Normal))
        self.addAction(action)


    def toggleHeadingStyle(self, size, weight):
        """
        Toggles a heading style based on the specified font size and weight at the current cursor position or selection.

        Args:
            size (int): The font size for the heading style.
            weight (int): The weight (boldness) of the font.
        """
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.LineUnderCursor)
        currentFormat = cursor.charFormat()
        currentFont = currentFormat.font()
        if currentFont.pointSize() == size and currentFont.weight() == weight:
            currentFont.setPointSize(12)
            currentFont.setWeight(QFont.Normal)
        else:
            currentFont.setPointSize(size)
            currentFont.setWeight(weight)
        currentFormat.setFont(currentFont)
        cursor.mergeCharFormat(currentFormat)
        self.editor.mergeCurrentCharFormat(currentFormat)
