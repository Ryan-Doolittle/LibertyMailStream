from email.mime.multipart import MIMEMultipart
import os
import base64
import threading
from threading import Event
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    REDIRECT_URI = 'http://localhost:8080/'
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self.auth_code = None
        self.auth_code_event = Event()  # Initialize the event here.

    def authenticate(self, client_id, client_secret):
        flow = InstalledAppFlow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.REDIRECT_URI)
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        webbrowser.open_new(auth_url)

        def AuthHandlerFactory(service):
            """
            Factory function to create a custom AuthHandler that can access the GmailService instance.
            """
            class CustomAuthHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    query = urlparse(self.path).query
                    query_components = parse_qs(query)
                    if 'code' in query_components:
                        service.auth_code = query_components['code'][0]
                        service.auth_code_event.set()  # Signal that the code is obtained.
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b'Authentication successful. You may close this window.')
                    else:
                        self.send_error(401)  # Send an error response.
            return CustomAuthHandler
        
        httpd = HTTPServer(('', 8080), AuthHandlerFactory(self))
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        self.auth_code_event.wait()  # Wait for the auth code event to be set by the AuthHandler.
        flow.fetch_token(code=self.auth_code)
        self.credentials = flow.credentials

        httpd.shutdown()
        server_thread.join()

        return self.credentials is not None

    def build_service(self):
        if not self.credentials:
            raise Exception("No credentials available. Please authenticate first.")
        self.service = build('gmail', 'v1', credentials=self.credentials)

    def send_email(self, to, subject, plain_text, html):
        if not self.service:
            raise Exception("Service not initialized. Please authenticate and build the service first.")

        message = MIMEMultipart('alternative')
        message['to'] = to
        message['subject'] = subject

        part1 = MIMEText(plain_text, 'plain')
        part2 = MIMEText(html, 'html')

        message.attach(part1)
        message.attach(part2)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        try:
            self.service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            return True
        except:
            return False