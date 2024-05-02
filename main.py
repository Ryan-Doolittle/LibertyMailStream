"""
This script sets up and runs a PyQt5 application for managing email communications using the Gmail API. It ensures
necessary directories and files exist, applies a dark theme, and manages user authentication via a login dialog.

It uses configurations for paths and settings, handles high-DPI display settings, and executes the application with
a login prompt followed by the main email application window.
"""

import os
import sys
import qdarktheme

from PyQt5.QtWidgets import QApplication, QDialog

from src.containers.login_screen import EmailerLoginDialog
from src.containers.main_window import LibertyMailstream
from src.utilities.config import config
from src.utilities.oauth import GmailService

if __name__ == "__main__":
    # Ensure the templates folder exists
    if config.get("FOLDERS", "templates_folder") not in os.listdir("."):
        os.mkdir(config.get("FOLDERS", "templates_folder"))

    # Ensure the recipients CSV file exists
    if config.get("FILES", "recipients_csv") not in os.listdir("."):
        with open(config.get("FILES", "recipients_csv"), "w") as file:
            file.write("")

    # Enable high DPI scaling for better display on high-resolution screens
    qdarktheme.enable_hi_dpi()

    # Create a Qt application instance
    app = QApplication(sys.argv)

    # Initialize the Gmail service
    gmail_service = GmailService()

    # Create and display the login dialog
    login_dialog = EmailerLoginDialog(gmail_service)
    if login_dialog.exec_() == QDialog.Accepted:
        # If login is successful, build the Gmail service
        gmail_service.build_service()

    # Initialize and display the main application window
    window = LibertyMailstream(gmail_service)
    window.show()

    # Start the Qt event loop
    sys.exit(app.exec_())
