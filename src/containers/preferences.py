from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFontComboBox
from PyQt5.QtGui import QFont
from ..utilities.config import config  # Ensure this import is correct

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Preferences')
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Email Delay Setting
        email_delay_layout = QHBoxLayout()
        email_delay_label = QLabel("Email Delay (seconds):", self)
        self.email_delay_input = QSpinBox(self)
        self.email_delay_input.setRange(0, 3600)
        email_delay_value = config.get("PREFERENCES", "email_delay")
        if email_delay_value is None:
            email_delay_value = "0"
        self.email_delay_input.setValue(int(email_delay_value))
        email_delay_layout.addWidget(email_delay_label)
        email_delay_layout.addWidget(self.email_delay_input)
        layout.addLayout(email_delay_layout)

        # Default Font Family Setting
        font_family_layout = QHBoxLayout()
        font_family_label = QLabel("Default Font Family:", self)
        self.font_family_input = QFontComboBox(self)
        default_font_family = config.get("PREFERENCES", "default_font_family")
        self.font_family_input.setCurrentFont(QFont(default_font_family))
        font_family_layout.addWidget(font_family_label)
        font_family_layout.addWidget(self.font_family_input)
        layout.addLayout(font_family_layout)

        # Default Font Size Setting
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Default Font Size (px):", self)
        self.font_size_input = QSpinBox(self)
        self.font_size_input.setRange(8, 48)
        font_size_value = config.get("PREFERENCES", "default_font_size")
        if font_size_value is None:
            font_size_value = "12"
        self.font_size_input.setValue(int(font_size_value))
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.font_size_input)
        layout.addLayout(font_size_layout)

        # Buttons for Save and Cancel
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_preferences)
        layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.close)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def save_preferences(self):
        config.set("PREFERENCES", "email_delay", str(self.email_delay_input.value()))
        config.set("PREFERENCES", "default_font_family", self.font_family_input.currentFont().family())
        config.set("PREFERENCES", "default_font_size", str(self.font_size_input.value()))
        self.accept()

def open_preferences(self):
    dialog = PreferencesDialog(self.parent)
    dialog.exec_()
