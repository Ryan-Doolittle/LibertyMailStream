
# Liberty Mail Stream (LMS)

## About

Liberty Mail Stream (LMS) creates a Simple Mail Transfer Protocol (SMTP) server with the intention of facilitating easy access to mass emailing while ensuring all Personally Identifiable Information (PII), such as recipient email addresses, is stored locally.

## Login Procedure

- Users log in to the program using Google OAuth. This method of logging in is much more recognized by end users and provides more security to the user by allowing for fine-grained adjustments to permissions requested.
- No longer requires the user to create an app password for their account.

## Email Sending Limits

Gmail imposes daily limits on mass emailing. Non-compliance can result in a strike against a user's account. To prevent this, LMS enforces its own limitations to ensure compliance with Gmail policies. There are two levels of limitations depending on the account type:

- Standard Gmail Account
- Google Workspace Account

For simplicity and to focus on early development, LMS will remain limited to supporting Standard Gmail Accounts, and the documentation will reflect limits applicable to Standard accounts only.

## Features

- Rich text Editor used to create or view email templates.
- Recipients Listing (managed locally outside of the application.)
- Email Control panel for starting the mass emailing process.

## Setting Up Client ID and Secret for LMS

To set up the LMS application, you need to create a client ID and secret through the Google Cloud Platform. Here’s how you can do it:

1. **Access Google Cloud Console**: Go to the Google Cloud Console and log in or create a new account if needed.
2. **Create a New Project**: Once logged in, create a new project specifically for your LMS application.
3. **Enable APIs**: Navigate to the “APIs & Services” dashboard, search for and enable the Gmail API.
4. **Configure OAuth Consent Screen**: In the “OAuth consent screen” section, fill in the required details about your application to be shown to users during the login process.
5. **Create Credentials**: Go to the “Credentials” section, click on “Create Credentials”, and select “OAuth client ID”.
6. **Application Type**: Choose “Web application” as the application type, and configure the authorized redirect URIs as required by LMS.
7. **Obtain Client ID and Secret**: After saving, you will receive your client ID and secret. Keep these credentials secure as they will be used to configure LMS.
