import imaplib
import email
import json
import smtplib
import datetime
import socket
from email.mime.text import MIMEText
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()


# --- Credential Setup ---
EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def send_report(full_content):
    """Sends the final summary report via SMTP."""
    msg = MIMEText(full_content)
    msg['Subject'] = "Weekly Inbox Automation Report"
    msg['From'] = EMAIL
    msg['To'] = EMAIL
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        print("Report sent to your inbox.")
    except Exception as e:
        print(f"Failed to send email report: {e}")

def run_automation():
    config = load_config()
    socket.setdefaulttimeout(30)
    
    # Initialize Counters
    total_found = 0
    opened_count = 0
    deleted_count = 0
    report_items = []

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        # Filter: Last 7 days
        since_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(UNSEEN SINCE {since_date})')
        
        id_list = messages[0].split()
        ids_to_process = id_list
        total_found = len(id_list)
        
        print(f"--- Found {total_found} unread. Processing {len(ids_to_process)} recent emails ---")

        for num in ids_to_process:
            # PEEK prevents the email from being marked 'Read' prematurely
            res, msg_data = mail.fetch(num, '(BODY.PEEK[])')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode Subject
                    subject_header = decode_header(msg.get("subject", ""))[0]
                    subject = subject_header[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(subject_header[1] or 'utf-8', errors='ignore')
                    
                    sender = msg.get("from", "").lower()
                    
                    # Extract Body Text
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors='ignore')
                    else:
                        body = msg.get_payload(decode=True).decode(errors='ignore')
                    
                    content = (subject + " " + body).lower()
                    
                    # Safety Check: Skip emails mentioning fraud/security alerts
                    safety_list = config.get("safety_keywords", [])
                    if any(k in content for k in safety_list):
                        mail.store(num, '-FLAGS', '\\Seen')
                        continue

                    action_taken = False

                    # 1. Check OPEN Rules
                    for rule in config.get("open_rules", []):
                        if rule.get("domain") and rule["domain"] in sender:
                            if any(k in content for k in rule.get("keywords", [])):
                                mail.store(num, '+FLAGS', '\\Seen')
                                report_items.append(f"✅ OPENED: {subject} (Rule: {rule['name']})")
                                opened_count += 1
                                action_taken = True
                                break

                    # 2. Check DELETE Rules
                    if not action_taken:
                        for rule in config.get("delete_rules", []):
                            domain_match = rule.get("domain") in sender if rule.get("domain") else True
                            if domain_match and any(k in content for k in rule.get("keywords", [])):
                                mail.store(num, '+FLAGS', '\\Deleted')
                                report_items.append(f"🗑️ DELETED: {subject} (Rule: {rule['name']})")
                                deleted_count += 1
                                action_taken = True
                                break

                    # 3. SAFETY RESET: If no match, force it back to Unread
                    if not action_taken:
                        mail.store(num, '-FLAGS', '\\Seen')

        mail.expunge()
        mail.logout()

        # 4. Construct Summary
        summary_header = (
            f"--- INBOX AUTOMATION SUMMARY ---\n"
            f"Total Unread Found: {total_found}\n"
            f"Emails Processed: {len(ids_to_process)}\n"
            f"Emails Opened: {opened_count}\n"
            f"Emails Deleted: {deleted_count}\n"
            f"---------------------------------\n\n"
        )
        
        full_report_body = summary_header + "\n".join(report_items)
        
        # Only send report if actions were actually taken
        if opened_count > 0 or deleted_count > 0:
            send_report(full_report_body)
            print(f"Finished: {opened_count + deleted_count} actions taken.")
        else:
            print(f"Finished: Scanned emails, but no rules matched. No report sent.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_automation()