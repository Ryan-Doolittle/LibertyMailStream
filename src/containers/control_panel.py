import time
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal

from ..utilities.import_cleaner import clean_email_list
from ..utilities.state import state_manager
from ..utilities.config import config


class EmailSenderThread(QThread):
    update_progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, emails_df, parent_frame):
        super().__init__()
        self.emails_df = emails_df
        self.parent_frame = parent_frame
        self.keep_running = True

    def run(self):
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
        self.keep_running = False
        print("Stopping email sending process...")


class ControlPanel(QToolBar):
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
        if not self.parent_frame.gmail_service:
            QMessageBox.critical(self, "Error", "Emailer service is not initialized.")
            return

        self.email_sender_thread = EmailSenderThread(self.emails_df, self.parent_frame)
        self.email_sender_thread.error_occurred.connect(self.displayError)
        self.email_sender_thread.update_progress.connect(self.updateEmailStatus)
        self.email_sender_thread.finished.connect(self.emailSendingFinished)
        self.email_sender_thread.start()

    def updateEmailStatus(self, index, status):
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