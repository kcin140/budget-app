# Streamlit Cloud Deployment Secrets

Copy your actual credentials to your Streamlit Cloud app settings under **"Secrets"**.

Go to: https://share.streamlit.io → Your App → Settings → Secrets

---

```toml
# WatsonX AI Configuration
WATSONX_API_KEY = "your-watsonx-api-key-here"
WATSONX_PROJECT_ID = "your-watsonx-project-id-here"

# DB2 Configuration
DB2_DATABASE = "your-db2-database-name"
DB2_HOSTNAME = "your-db2-hostname.databases.appdomain.cloud"
DB2_PORT = "32304"
DB2_UID = "your-db2-username"
DB2_PWD = "your-db2-password"
DB2_SECURITY = "SSL"
```

---

## Deployment Steps

1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Click "New app"
4. Select your repository: `kcin140/budget-app`
5. Set main file path: `app.py`
6. Click "Advanced settings" → "Secrets"
7. Paste your actual credentials in TOML format (see above template)
8. Click "Deploy"

## Important Notes

- The secrets are stored securely in Streamlit Cloud
- Never commit actual credentials to GitHub
- The `.env` file is gitignored for local development
- Use `.env.example` as a template for your local `.env` file
