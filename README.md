# bq-email-reporter

Automated BigQuery reporting pipeline that queries data on a schedule and delivers formatted HTML email reports via SendGrid and Google Cloud Functions.

---

## Overview

This project automates the process of running a BigQuery query and emailing the results as a styled HTML table. It runs entirely on GCP — a Cloud Scheduler job triggers a Cloud Function on a set schedule, which pulls data from BigQuery and sends it via SendGrid. The SendGrid API key is stored securely in Secret Manager and injected at runtime.

The SMTP alternative (`main_smtp.py`) is included for local testing or environments without a SendGrid account.

---

## Architecture

```
Cloud Scheduler (cron)
        |
        |  HTTP POST
        v
Cloud Function — EmailAlertPython
        |
        |-- BigQuery --> pandas DataFrame
        |       (SELECT * FROM TestData.TestTable)
        |
        |-- pretty_html_table --> styled HTML
        |
        └-- SendGrid API --> email delivered
```

GCP services used:

| Service | Role |
|---|---|
| BigQuery | Data source |
| Cloud Functions (1st gen) | Runs the Python function |
| Cloud Scheduler | Cron-based trigger |
| Secret Manager | Stores the SendGrid API key |
| SendGrid | Email delivery |

---

## Project Structure

```
bq-email-reporter/
├── src/
│   ├── main.py              # Cloud Function — SendGrid version
│   ├── main_smtp.py         # Cloud Function — SMTP alternative
│   └── requirements.txt     # Python dependencies
├── config/
│   └── gcp_config.md        # GCP resource configuration reference
├── docs/
│   └── screenshots/         # Setup and output screenshots
├── .github/
│   └── workflows/
│       └── lint.yml          # CI lint check
├── .gitignore
├── LICENSE
└── README.md
```

---

## Prerequisites

- Google Cloud project with billing enabled
- BigQuery dataset and table
- SendGrid account with a verified sender email
- `gcloud` CLI installed and authenticated

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/bq-email-reporter.git
cd bq-email-reporter
```

### 2. Store the SendGrid API key in Secret Manager

```bash
gcloud secrets create EMAIL_API_KEY --replication-policy="automatic"

echo -n "SG.YOUR_SENDGRID_API_KEY" | \
  gcloud secrets versions add EMAIL_API_KEY --data-file=-
```

### 3. Deploy the Cloud Function

```bash
gcloud functions deploy EmailAlertPython \
  --runtime python37 \
  --trigger-http \
  --entry-point email \
  --region us-central1 \
  --source src/
```

In the Cloud Console, bind the `EMAIL_API_KEY` secret under **Function > Edit > Security and Image Repo > Secrets** and expose it as an environment variable with the same name.

### 4. Create the Cloud Scheduler job

```bash
gcloud scheduler jobs create http EmailAlert \
  --location us-central1 \
  --schedule "*/5 * * * *" \
  --uri "https://us-central1-<PROJECT_ID>.cloudfunctions.net/EmailAlertPython" \
  --http-method POST \
  --oidc-service-account-email <SERVICE_ACCOUNT_EMAIL> \
  --time-zone "Asia/Kolkata"
```

### 5. Test manually

```bash
curl -m 70 -X POST \
  https://us-central1-<PROJECT_ID>.cloudfunctions.net/EmailAlertPython \
  -H "Authorization: bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Configuration

### Query

Edit `src/main.py` to point at your table:

```python
query = """SELECT * FROM `your_project.your_dataset.your_table`"""
```

### Schedule

Common cron expressions for the Scheduler job:

| Cron | Meaning |
|---|---|
| `*/5 * * * *` | Every 5 minutes |
| `0 9 * * 1-5` | 9:00 AM, Mon–Fri |
| `0 8 * * *` | 8:00 AM daily |

### Email table theme

`pretty_html_table` supports several colour themes:

```python
output_table = build_table(df, "blue_light")
# other options: "green_dark", "orange_light", "grey_light"
```

---

## SMTP Alternative

To use SMTP instead of SendGrid, deploy `src/main_smtp.py` as the function source. Set these environment variables on the function:

| Variable | Description |
|---|---|
| `SMTP_HOST` | SMTP server host |
| `SMTP_PORT` | SMTP port |
| `SMTP_USERNAME` | SMTP username |
| `SMTP_PASSWORD` | SMTP password |
| `EMAIL_SENDER` | Sender address |
| `EMAIL_RECIPIENT` | Recipient address |

---

## Dependencies

```
google-cloud-bigquery==3.10.0
google-cloud-bigquery[pandas]==3.10.0
pretty_html_table==0.9.8
sendgrid==6.10.0
pandas-gbq==0.13.1
```

---
