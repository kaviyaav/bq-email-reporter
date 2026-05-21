"""
BigQuery Reporting Automation — SMTP Alternative
-------------------------------------------------
Same as main.py but uses Python's built-in smtplib / Mailtrap
instead of SendGrid. Useful for local testing or when you don't
have a SendGrid account.

Entry point: email
"""

import os
import smtplib
from email.mime.text import MIMEText

import pandas_gbq
from pretty_html_table import build_table


def email(request):
    """
    HTTP-triggered Cloud Function.
    Reads from BigQuery and sends a formatted HTML email via SMTP.
    """
    # ------------------------------------------------------------------ #
    # 1. Query BigQuery
    # ------------------------------------------------------------------ #
    query = """SELECT * FROM `TestData.TestTable`"""
    df = pandas_gbq.read_gbq(query)

    # ------------------------------------------------------------------ #
    # 2. Build styled HTML table
    # ------------------------------------------------------------------ #
    output_table = build_table(df, "blue_light")

    # ------------------------------------------------------------------ #
    # 3. SMTP configuration (Mailtrap sandbox shown; replace for production)
    # ------------------------------------------------------------------ #
    smtp_host = os.environ.get("SMTP_HOST", "sandbox.smtp.mailtrap.io")
    smtp_port = int(os.environ.get("SMTP_PORT", 2525))
    smtp_username = os.environ.get("SMTP_USERNAME", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")

    sender = os.environ.get("EMAIL_SENDER", "abc@gmail.com")
    recipient = os.environ.get("EMAIL_RECIPIENT", "abcd@gmail.com")
    subject = "Reporting Mail from BigQuery"

    # ------------------------------------------------------------------ #
    # 4. Build and send the MIME email
    # ------------------------------------------------------------------ #
    msg = MIMEText(output_table, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender, recipient, msg.as_string())
            print("Email sent successfully!")
        return "Email sent successfully!", 200

    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
        return f"Failed to send email: {str(e)}", 500
