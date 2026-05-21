"""
BigQuery Reporting Automation — Cloud Function
----------------------------------------------
Queries a BigQuery table, formats the result as an HTML table,
and emails it via SendGrid.

Entry point: email
"""

import os

from google.cloud import bigquery
from pretty_html_table import build_table
import pandas_gbq
import sendgrid
from sendgrid.helpers.mail import Mail


def email(request):
    """
    HTTP-triggered Cloud Function.
    Reads from BigQuery and sends a formatted HTML table via SendGrid.

    Args:
        request: Flask Request object (body not used).

    Returns:
        A string status message.
    """
    # ------------------------------------------------------------------ #
    # 1. Query BigQuery
    # ------------------------------------------------------------------ #
    query = """SELECT * FROM `TestData.TestTable`"""

    # Option A — pandas_gbq (used here)
    df = pandas_gbq.read_gbq(query)

    # Option B — BigQuery client (uncomment if preferred)
    # client = bigquery.Client()
    # query_job = client.query(query)
    # df = query_job.to_dataframe()

    # ------------------------------------------------------------------ #
    # 2. Build a styled HTML table
    # ------------------------------------------------------------------ #
    output_table = build_table(df, "blue_light")

    # ------------------------------------------------------------------ #
    # 3. Send via SendGrid
    # ------------------------------------------------------------------ #
    message = Mail(
        from_email="arunsrinivas1998@gmail.com",
        to_emails="arunsrinivas1998@gmail.com",
        subject="Big Query Reporting",
        html_content="Please find the results of the Query below<br>" + output_table,
    )

    try:
        # API key is stored in GCP Secret Manager and exposed as an
        # environment variable (EMAIL_API_KEY) on the Cloud Function.
        sg = sendgrid.SendGridAPIClient(os.environ.get("EMAIL_API_KEY"))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return f"Email sent successfully. Status: {response.status_code}", 200

    except Exception as e:
        print(str(e))
        return f"Failed to send email: {str(e)}", 500
