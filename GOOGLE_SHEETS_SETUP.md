# Google Sheets Setup Guide

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Name it something like "Budget App"

## Step 2: Enable Google Sheets API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Google Sheets API"
3. Click **Enable**

## Step 3: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Name it "budget-app-service"
4. Click **Create and Continue**
5. Skip the optional steps, click **Done**

## Step 4: Create Service Account Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Click **Create** - this downloads a JSON file
6. **Save this file as `service_account.json` in your project folder** (for local development)

## Step 5: Create Your Budget Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "Budget Tracker" (or whatever you like)
4. Copy the **Spreadsheet ID** from the URL:
   - URL looks like: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit`
   - Copy the long ID between `/d/` and `/edit`

## Step 6: Share Spreadsheet with Service Account

1. Open your spreadsheet
2. Click **Share** button
3. Paste the service account email (from the JSON file, looks like `budget-app-service@project-name.iam.gserviceaccount.com`)
4. Give it **Editor** access
5. Click **Share**

## Step 7: Configure Local Environment

Create a `.env` file with:

```bash
SPREADSHEET_ID="your-spreadsheet-id-here"
WATSONX_API_KEY="your-watsonx-key"
WATSONX_PROJECT_ID="your-watsonx-project"
```

## Step 8: Test Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Step 9: Deploy to Streamlit Cloud

1. Push code to GitHub (the `service_account.json` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy your app
4. In **Secrets**, add:

```toml
SPREADSHEET_ID = "your-spreadsheet-id"
WATSONX_API_KEY = "your-key"
WATSONX_PROJECT_ID = "your-project"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id-from-json"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "budget-app-service@project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

**Note**: Copy all the fields from your `service_account.json` file into the `[gcp_service_account]` section.

## Done!

Your app will now:
- Store categories in a "Categories" sheet
- Create a new sheet for each month (e.g., "2024-11", "2024-12")
- Each monthly sheet has a summary table at the top
- Transactions are listed below the summary
