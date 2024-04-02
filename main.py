import os
import sys
import qdarktheme

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog

from src.containers.login_screen import EmailerLoginDialog
from src.containers.main_window import LibertyMailstream
from src.utilities.config import config
from src.utilities.oauth import GmailService




if __name__ == "__main__":
    if config.get("FOLDERS","templates_folder") not in os.listdir("."):
        os.mkdir(config.get("FOLDERS","templates_folder"))

    if config.get("FILES","recipients_csv") not in os.listdir("."):
        with open(config.get("FILES","recipients_csv"), "w") as file:
            file.write("")

    qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    gmail_service = GmailService()
    login_dialog = EmailerLoginDialog(gmail_service)
    if login_dialog.exec_() == QDialog.Accepted:
        gmail_service.build_service()
        window = LibertyMailstream(gmail_service)
        window.show()
        sys.exit(app.exec_())
