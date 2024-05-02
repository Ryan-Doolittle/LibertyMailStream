import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

from ..utilities.resource_path import resource_path
from ..utilities.config import config

from ..utilities.oauth import GmailService



class EmailerLoginDialog(QDialog):
    """
    A dialog window for the OAuth2 authentication with Google for email services.
    
    This class provides a GUI for users to authenticate themselves using Google's OAuth2 service,
    ensuring secure access to their email functionalities.
    
    Attributes:
        email (str): Email address of the user. Initialized to None and updated upon successful login.
        oauth2_handler (GmailService): Handler for OAuth2 authentication process.
    
    Args:
        oauth2_handler (GmailService): An instance of GmailService to handle OAuth2 authentication.
    """
    def __init__(self, oauth2_handler) -> None:
        super().__init__()
        self.email: str = None
        self.oauth2_handler:GmailService = oauth2_handler
        
        self.initUI()


    def initUI(self) -> None:
        """
        Initializes the user interface components of the login dialog. It sets up the layout, logo, and login button.
        """
        self.setWindowTitle("LMS")
        self.setWindowIcon(QIcon(resource_path('img/icons/logo.png')))
        
        layout = QVBoxLayout()

        logoLabel = QLabel()
        logoPixmap = QPixmap(resource_path('img/icons/logo.png'))
        logoLabel.setPixmap(logoPixmap)
        logoLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(logoLabel)

        login_button = QPushButton("Sign in with Google")
        login_button.clicked.connect(self.initiate_oauth2_flow)
        layout.addWidget(login_button)

        self.setLayout(layout)


    def initiate_oauth2_flow(self):
        """
        Initiates the OAuth2 flow for authentication. It retrieves the client ID and secret from configuration,
        calls the GmailService to authenticate, and handles the user response based on the authentication success.
        """
        client_id = config.get("TEMP_SECRET_STORAGE", "google_client_id")
        print(client_id)
        success = self.oauth2_handler.authenticate(
            client_id,
            config.get("TEMP_SECRET_STORAGE", "google_client_secret")
        )
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed", "OAuth2 Authentication failed. Please try again.")
