import csv
import re



def is_valid_email(email):
    # Simple regex for validating an email address
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def clean_email_list(input_file_path, output_file_path):
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
