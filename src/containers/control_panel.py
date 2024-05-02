import time
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal

from ..utilities.import_cleaner import clean_email_list
from ..utilities.state import state_manager
from ..utilities.config import config


class EmailSenderThread(QThread):
    """
    A class derived from QThread that handles the background sending of emails.
    
    Attributes:
        update_progress (pyqtSignal): Signal emitted during the sending process to update the progress.
        finished (pyqtSignal): Signal emitted when the email sending process is complete.
        error_occurred (pyqtSignal): Signal emitted in case of an error during the email sending process.
    
    Args:
        emails_df (pd.DataFrame): DataFrame containing the email addresses and their sending status.
        parent_frame (QWidget): The parent GUI component that contains UI elements like subject line and content editor.
    """
    update_progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, emails_df, parent_frame):
        super().__init__()
        self.emails_df = emails_df
        self.parent_frame = parent_frame
        self.keep_running = True

    def run(self):
        """
        Starts the process of sending emails. This method checks for unsent emails in the DataFrame and sends them.
        It also updates the status of each email sent and handles the interruption if the user decides to stop the process.
        """
        print("Starting email sending process.")
        recipient_count = len(self.emails_df)
        for index, (idx, row) in enumerate(self.emails_df.iterrows()):
            if not self.keep_running:
                print("Email sending cancelled by user.")
                break

            if row["Status"] == "Sent":
                print(f"Skipping already sent email to: {row['Email Address']}")
                continue

            if not state_manager.can_send_email():
                self.error_occurred.emit("Daily email limits met")
                print("Daily email limit reached, stopping send.")
                break

            recipient = row['Email Address']
            subject = self.parent_frame.subjectLineEdit.text()
            raw_content = self.parent_frame.editor.toPlainText()
            content = self.parent_frame.editor.toHtml()
            
            if not subject or not raw_content:
                self.error_occurred.emit("Subject or content cannot be empty.")
                return

            try:
                if state_manager.increment_sent():

                    success = self.parent_frame.gmail_service.send_email(recipient, subject, raw_content, content)
                    new_status = "Sent" if success else "Failed"
                    print(f"Email sent to {recipient}: {new_status}")
            except Exception as e:
                new_status = "Failed"
                self.error_occurred.emit(str(e))
                print(f"Error sending email to {recipient}: {e}")

            self.emails_df.at[idx, 'Status'] = new_status
            self.update_progress.emit(index, new_status)
            time.sleep(int(config.get("PREFERENCES","email_delay")))

        print("Email sending process completed.")
        self.finished.emit()

    def stop(self):
        """
        Stops the email sending process by setting the keep_running flag to False.
        """
        self.keep_running = False
        print("Stopping email sending process...")


class ControlPanel(QToolBar):
    """
    A class representing the control panel in the GUI, which includes buttons and a table to manage email sending tasks.
    
    Args:
        parent (QWidget): The parent widget that this ControlPanel belongs to.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_frame = parent
        self.email_listing = config.get("FILES", "recipients_csv")
        self.emails_df = pd.DataFrame(columns=['Status', 'Email Address'])
        self.setWindowTitle('Recipients')
        self.initUI()
        self.email_sender_thread = None
        
    def displayError(self, message):
            QMessageBox.critical(self, "Error", message)

    def initUI(self):
        """
        Initializes the user interface components of the control panel, including buttons and the email recipient table.
        """
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        
        self.buttonBar = QWidget()
        self.buttonBarLayout = QHBoxLayout()
        self.buttonBar.setLayout(self.buttonBarLayout)
        
        self.addButton = QPushButton("Start")
        self.removeButton = QPushButton("Cancel")
        self.refreshButton = QPushButton("Refresh")
        
        self.addButton.clicked.connect(self.startSendingEmails)
        self.removeButton.clicked.connect(self.cancelSendingEmails)
        self.refreshButton.clicked.connect(self.refreshRecipientsList)

        self.buttonBarLayout.addWidget(self.addButton)
        self.buttonBarLayout.addWidget(self.removeButton)
        self.buttonBarLayout.addWidget(self.refreshButton)
        
        self.recipientsTable = QTableWidget()
        self.recipientsTable.setColumnCount(2)
        self.recipientsTable.setHorizontalHeaderLabels(['Status', 'Email Address'])
        self.recipientsTable.verticalHeader().setVisible(False)
        self.recipientsTable.setShowGrid(True)
        self.recipientsTable.setColumnWidth(0, 55)
        self.recipientsTable.horizontalHeader().setStretchLastSection(True)

        self.layout.addWidget(self.buttonBar)
        self.layout.addWidget(self.recipientsTable)
        
        self.widget.setLayout(self.layout)
        self.addWidget(self.widget)
        
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.layout.addWidget(self.progressBar)
        self.progressBar.hide()

        self.loadEmails(self.email_listing)


    def loadEmails(self, filePath):
        """
        Loads emails from a specified CSV file, cleans them using an external utility, and updates the GUI table.
        
        Args:
            filePath (str): The path to the CSV file containing email addresses.
        """
        clean_email_list(filePath, filePath)
        self.recipientsTable.setRowCount(0)
        self.emails_df = pd.DataFrame(columns=['Status', 'Email Address'])


        temp_df = pd.read_csv(filePath, header=None, names=['Email Address'])
        temp_df['Status'] = 'Pending'
        self.emails_df = pd.concat([self.emails_df, temp_df])

        for index, row in self.emails_df.iterrows():
            row_pos = self.recipientsTable.rowCount()
            self.recipientsTable.insertRow(row_pos)
            self.recipientsTable.setItem(row_pos, 0, QTableWidgetItem(row['Status']))
            self.recipientsTable.setItem(row_pos, 1, QTableWidgetItem(row['Email Address']))
        

    def startSendingEmails(self):
        """
        Initializes and starts the EmailSenderThread to send emails. It also connects signals to appropriate slots
        for error handling and progress updates.
        """
        if not self.parent_frame.gmail_service:
            QMessageBox.critical(self, "Error", "Emailer service is not initialized.")
            return

        self.email_sender_thread = EmailSenderThread(self.emails_df, self.parent_frame)
        self.email_sender_thread.error_occurred.connect(self.displayError)
        self.email_sender_thread.update_progress.connect(self.updateEmailStatus)
        self.email_sender_thread.finished.connect(self.emailSendingFinished)
        self.email_sender_thread.start()

    def updateEmailStatus(self, index, status):
        """
        Updates the status of an email in the GUI table and the progress bar.
        
        Args:
            index (int): The index of the email in the table.
            status (str): The new status of the email ('Sent' or 'Failed').
        """
        self.recipientsTable.setItem(index, 0, QTableWidgetItem(status))
        progress_percentage = int((index + 1) / len(self.emails_df) * 100)
        self.progressBar.setValue(progress_percentage)

    def emailSendingFinished(self):
        self.progressBar.hide()

    def cancelSendingEmails(self):
        if self.email_sender_thread:
            self.email_sender_thread.stop()

    def refreshRecipientsList(self):
        self.loadEmails(self.email_listing)