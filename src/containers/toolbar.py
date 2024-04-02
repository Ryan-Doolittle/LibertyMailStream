from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QWidgetAction

from PyQt5.QtGui import QIcon, QFont, QTextListFormat, QTextCursor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QTextListFormat
from PyQt5.QtGui import QTextCursor


from ..utilities.resource_path import resource_path



class Toolbar(QToolBar):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor: QTextEdit = editor
        self.setWindowTitle('Toolbar')
        self.initUI()


    def initUI(self):
        # Font Selector
        self.fontBox = QComboBox(self)
        self.fontBox.addItems(["Courier New", "Helvetica", "Arial", "SansSerif", "Times", "Monospace"])
        self.fontBox.activated.connect(lambda: self.setFont(self.fontBox.currentText()))

        # Font Size Selector
        self.fontSizeBox = QSpinBox(self)
        self.fontSizeBox.setMinimum(1)
        self.fontSizeBox.setMaximum(100)
        self.fontSizeBox.setValue(12)  # Default value
        self.fontSizeBox.valueChanged.connect(lambda: self.setFontSize(self.fontSizeBox.value()))

        # Adding Widgets to Toolbar
        self.addWidget(self.fontBox)
        self.addWidget(self.fontSizeBox)

        # Create a color picker tool button
        self.colorPickerButton = QToolButton(self)
        self.colorPickerButton.setAutoFillBackground(True)
        self.updateButtonColor(self.editor.textColor())  # Initialize with the current text color
        self.colorPickerButton.setFixedSize(24, 24)  # Makes the button square
        self.colorPickerButton.clicked.connect(self.setTextColor)

        # Background Color Picker Button
        self.bgColorPickerButton = QToolButton(self)
        self.bgColorPickerButton.setAutoFillBackground(True)
        self.updateButtonColor(self.editor.textBackgroundColor())  # Initialize with the current text background color
        self.bgColorPickerButton.setFixedSize(24, 24)  # Makes the button square
        self.bgColorPickerButton.clicked.connect(self.setTextBackgroundColor)

        # Wrap the tool button in a QWidgetAction to add it to the toolbar
        colorPickerAction = QWidgetAction(self)
        colorPickerAction.setDefaultWidget(self.colorPickerButton)
        self.addAction(colorPickerAction)

        # Wrap the tool button in a QWidgetAction to add it to the toolbar
        backgroundColorPickerAction = QWidgetAction(self)
        backgroundColorPickerAction.setDefaultWidget(self.bgColorPickerButton)
        self.addAction(backgroundColorPickerAction)

        # Heading Styles Actions
        self.addSeparator()
        self.addHeadingAction("H1", 24)  # Assuming 24pt for H1
        self.addHeadingAction("H2", 18)  # Assuming 18pt for H2
        self.addHeadingAction("H3", 14)  # Assuming 14pt for H3

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
        action = QAction(QIcon(iconPath), title, self)
        action.triggered.connect(function)
        self.addAction(action)


    def addAlignmentAction(self, title, iconPath, alignment):
        action = QAction(QIcon(iconPath), title, self)
        action.triggered.connect(lambda: self.editor.setAlignment(alignment))
        self.addAction(action)


    def setFontSize(self, size):
        self.editor.setFontPointSize(size)


    def setFont(self, fontName):
        self.editor.setCurrentFont(QFont(fontName))


    def toggleBoldText(self):
        currentState = self.editor.fontWeight() == QFont.Bold
        self.editor.setFontWeight(QFont.Bold if not currentState else QFont.Normal)


    def toggleItalicText(self):
        currentState = self.editor.fontItalic()
        self.editor.setFontItalic(not currentState)


    def toggleUnderlineText(self):
        currentState = self.editor.fontUnderline()
        self.editor.setFontUnderline(not currentState)


    def setTextBackgroundColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.editor.setTextBackgroundColor(color)
            # Optionally, update the button's background color to reflect the chosen color
            self.bgColorPickerButton.setStyleSheet(f"background-color: {color.name()};")


    def setTextColor(self):
        color = QColorDialog.getColor(self.editor.textColor())
        if color.isValid():
            self.editor.setTextColor(color)
            self.updateButtonColor(color)


    def updateButtonColor(self, color):
        # Update the button's background color to reflect the chosen color
        self.colorPickerButton.setStyleSheet(f"background-color: {color.name()}; border: none;")


    def setList(self, listStyle):
        cursor = self.editor.textCursor()
        listFormat = QTextListFormat()
        listFormat.setStyle(listStyle)
        cursor.createList(listFormat)


    def insertHyperlink(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setLabelText("Enter URL:")
        dialog.setWindowTitle("Insert Hyperlink")
        
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: #f0f0f0; /* Light gray background */
            }
            QLabel, QLineEdit {
                color: #333; /* Darker text for better contrast */
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
        action = QAction(title, self)
        action.triggered.connect(lambda: self.toggleHeadingStyle(size, QFont.Bold if size > 12 else QFont.Normal))
        self.addAction(action)


    def toggleHeadingStyle(self, size, weight):
        cursor = self.editor.textCursor()
        # If no text is selected, work with the current line/block
        if not cursor.hasSelection():
            cursor.select(QTextCursor.LineUnderCursor)

        currentFormat = cursor.charFormat()
        currentFont = currentFormat.font()

        # Decide whether to apply heading style or revert to normal based on current formatting
        if currentFont.pointSize() == size and currentFont.weight() == weight:
            # Revert to normal text: Set font size to default (e.g., 12pt) and weight to normal
            currentFont.setPointSize(12)  # Assuming 12 is the default size for normal text
            currentFont.setWeight(QFont.Normal)
        else:
            # Apply the heading style
            currentFont.setPointSize(size)
            currentFont.setWeight(weight)

        # Apply the changes
        currentFormat.setFont(currentFont)
        cursor.mergeCharFormat(currentFormat)
        self.editor.mergeCurrentCharFormat(currentFormat)
