import csv
import re



def is_valid_email(email):
    """
    Validates an email address using a regular expression to ensure it meets a basic standard of email format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email address is valid according to the regex pattern, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def clean_email_list(input_file_path, output_file_path):
    """
    Reads a list of email addresses from a CSV file, validates each email, and writes unique and valid emails
    to another CSV file.

    This function ensures that the output file contains only unique and properly formatted email addresses,
    sorted alphabetically.

    Args:
        input_file_path (str): The path to the CSV file containing the list of email addresses.
        output_file_path (str): The path to the CSV file where the cleaned list of email addresses will be saved.

    Notes:
        The input CSV is expected to contain one email address per row.
    """
    unique_emails = set()

    with open(input_file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            if len(row) == 0:
                continue
            email = row[0].strip()
            if is_valid_email(email):
                unique_emails.add(email)

    with open(output_file_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        for email in sorted(unique_emails):
            writer.writerow([email])
