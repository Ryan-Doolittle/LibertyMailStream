import time
import pandas as pd

from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QProgressBar

from ..utilities.import_cleaner import clean_email_list
from ..utilities.state import state_manager
from ..utilities.config import config




class ControlPanel(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_frame = parent
        self.email_listing = config.get("FILES", "recipients_csv")
        self.emails_df = pd.DataFrame(columns=['Status', 'Email Address'])
        self.setWindowTitle('Recipients')
        self.initUI()

        self.sending_emails = False


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
        
        # self.recipientsTable = QTableWidget()
        # self.recipientsTable.setColumnCount(2)
        # self.recipientsTable.setHorizontalHeaderLabels(['Status', 'Email Address'])
        # self.recipientsTable.verticalHeader().setVisible(False)
        # self.recipientsTable.setShowGrid(True)
        # self.recipientsTable.setColumnWidth(0, 55)
        # self.recipientsTable.horizontalHeader().setStretchLastSection(True)

        self.layout.addWidget(self.buttonBar)
        # self.layout.addWidget(self.recipientsTable)
        
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
        # self.recipientsTable.setRowCount(0)
        self.emails_df = pd.DataFrame(columns=['Status', 'Email Address'])


        temp_df = pd.read_csv(filePath, header=None, names=['Email Address'])
        temp_df['Status'] = 'Pending'
        self.emails_df = pd.concat([self.emails_df, temp_df])

        # for index, row in self.emails_df.iterrows():
        #     row_pos = self.recipientsTable.rowCount()
        #     self.recipientsTable.insertRow(row_pos)
        #     self.recipientsTable.setItem(row_pos, 0, QTableWidgetItem(row['Status']))
        #     self.recipientsTable.setItem(row_pos, 1, QTableWidgetItem(row['Email Address']))
        

    def startSendingEmails(self):
        if not self.parent_frame.gmail_service:
            QMessageBox.critical(self, "Error", "Emailer service is not initialized.")
            return

        self.sending_emails = True
        self.progressBar.show()
        QApplication.processEvents()

        subject = self.parent_frame.subjectLineEdit.text()
        raw_content = self.parent_frame.editor.toPlainText()
        content = self.parent_frame.editor.toHtml()

        if subject == None or subject == "":
            QMessageBox.critical(self, "Error", "No Subject")
            self.sending_emails = False
            return
        if raw_content == None or raw_content == "":
            QMessageBox.critical(self, "Error", "No Content")
            self.sending_emails = False
            return

        recipient_count = len(self.emails_df)

        for index, (idx, row) in enumerate(self.emails_df.iterrows()):
            if not state_manager.can_send_email():
                QMessageBox.critical(self, "Error", "Daily email limits met")
                return
            
            if row["Status"] == "sent":
                continue

            if not self.sending_emails:
                self.progressBar.hide()
                break

            recipient = row['Email Address']
            try:
                if state_manager.increment_sent():
                    success = self.parent_frame.gmail_service.send_email(recipient, subject, raw_content, content)
                    if success:
                        new_status = "Sent"
                    else:
                        new_status = "Failed"

            except Exception as e:
                print(e)
                new_status = "Failed"

            self.emails_df.at[idx, 'Status'] = new_status
            # self.recipientsTable.setItem(index, 0, QTableWidgetItem(new_status))

            progress_percentage = int((index + 1) / recipient_count * 100)
            self.progressBar.setValue(progress_percentage)
            QApplication.processEvents()
            
            if index % 15 == 0 and index > 0:
                time.sleep(20)
            else:
                time.sleep(5)

        self.progressBar.hide()
        self.sending_emails = False


    def cancelSendingEmails(self):
        self.sending_emails = False

        
    def refreshRecipientsList(self):
        self.loadEmails(self.email_listing)
