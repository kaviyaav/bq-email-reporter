# GCP Infrastructure Configuration

## Cloud Function

| Setting         | Value                                      |
|-----------------|--------------------------------------------|
| Function Name   | `EmailAlertPython`                         |
| Generation      | 1st gen                                    |
| Region          | `us-central1`                              |
| Runtime         | Python 3.7                                 |
| Entry Point     | `email`                                    |
| Trigger Type    | HTTP (HTTPS required)                      |
| Trigger URL     | `https://us-central1-<YOUR_PROJECT_ID>.cloudfunctions.net/EmailAlertPython` |

---

## Cloud Scheduler Job

| Setting          | Value                                         |
|------------------|-----------------------------------------------|
| Job Name         | `EmailAlert`                                  |
| Region           | `us-central1`                                 |
| Description      | Triggers Email Alert Cloud Function           |
| Frequency (cron) | `*/5 * * * *` — every 5 minutes              |
| Timezone         | `Asia/Kolkata` (IST)                          |
| Target Type      | HTTP                                          |
| HTTP Method      | `POST`                                        |
| URL              | Cloud Function Trigger URL (above)            |
| Auth Header      | OIDC token                                    |
| Service Account  | App Engine default service account            |
| HTTP Headers     | `Content-Type: application/json`              |
|                  | `User-Agent: Google-Cloud-Scheduler`          |
| Body             | `{}`                                          |

> **Note:** Adjust the cron frequency for production.  
> `0 9 * * 1-5` would run at 09:00 IST on every weekday.

---

## Secret Manager

The SendGrid API key is stored securely in GCP Secret Manager.

| Setting              | Value                        |
|----------------------|------------------------------|
| Secret Name          | `EMAIL_API_KEY`              |
| Encryption           | Google-managed key           |
| Reference Method     | Exposed as environment variable |
| Environment Variable | `EMAIL_API_KEY`              |

### Steps to create the secret

```bash
# Create the secret
gcloud secrets create EMAIL_API_KEY --replication-policy="automatic"

# Add the SendGrid API key as the first version
echo -n "SG.YOUR_API_KEY_HERE" | \
  gcloud secrets versions add EMAIL_API_KEY --data-file=-
```

### Bind the secret to the Cloud Function

In the Cloud Function → **Security and Image Repo** tab:
1. Under **Secrets**, click **+ ADD A SECRET REFERENCE**.
2. Select `EMAIL_API_KEY`.
3. Set **Reference method** to *Exposed as environment variable*.
4. Set the environment variable name to `EMAIL_API_KEY`.

---

## BigQuery Dataset

| Setting       | Value             |
|---------------|-------------------|
| Dataset       | `TestData`        |
| Table         | `TestTable`       |
| Query         | `SELECT * FROM \`TestData.TestTable\`` |

Replace with your actual project, dataset, and table.

---

## Deployment Commands

```bash
# Deploy the Cloud Function
gcloud functions deploy EmailAlertPython \
  --runtime python37 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point email \
  --region us-central1 \
  --source src/

# Test the function manually
curl -m 70 -X POST \
  https://us-central1-<YOUR_PROJECT_ID>.cloudfunctions.net/EmailAlertPython \
  -H "Authorization: bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{}'
```
