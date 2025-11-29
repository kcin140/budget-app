# Budget App

A private budget-tracking mobile-friendly app using Streamlit, IBM Db2, and IBM watsonx.ai.

## Features

- 📊 **Dashboard** with spending charts and progress tracking
- 🤖 **AI-powered expense parsing** - enter expenses in natural language
- 📝 **Multiple expenses at once** - "20 at Costco for groceries and 15 for toiletries"
- 🗑️ **Delete transactions** - remove accidental entries
- ✏️ **Manage categories** - add, edit, delete, and sort categories
- 📱 **Mobile-friendly** - works great on phones

## Local Setup

1.  **Install Requirements**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Create a `.env` file with your credentials:
    ```bash
    DB2_DATABASE="bludb"
    DB2_HOSTNAME="your-db2-hostname"
    DB2_PORT="32304"
    DB2_UID="your-username"
    DB2_PWD="your-password"
    DB2_SECURITY="SSL"
    WATSONX_API_KEY="your-api-key"
    WATSONX_PROJECT_ID="your-project-id"
    ```

3.  **Database Setup**
    Run the schema in your Db2 console:
    ```bash
    python init_db.py
    ```

4.  **Create Default User**
    ```bash
    python create_default_user.py
    ```

5.  **Run the App**
    ```bash
    streamlit run app.py
    ```

## Deployment to Streamlit Community Cloud

### Prerequisites
- GitHub account
- Streamlit Community Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Steps

1.  **Push to GitHub**
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/budget-app.git
    git push -u origin main
    ```

2.  **Deploy on Streamlit Cloud**
    - Go to [share.streamlit.io](https://share.streamlit.io)
    - Click "New app"
    - Select your GitHub repository
    - Set main file path: `app.py`
    - Click "Advanced settings" and add your secrets:
      ```toml
      DB2_DATABASE = "bludb"
      DB2_HOSTNAME = "your-hostname"
      DB2_PORT = "32304"
      DB2_UID = "your-username"
      DB2_PWD = "your-password"
      DB2_SECURITY = "SSL"
      WATSONX_API_KEY = "your-api-key"
      WATSONX_PROJECT_ID = "your-project-id"
      ```
    - Click "Deploy"

3.  **Access on Mobile**
    - Open the deployed URL in your phone's browser
    - **iOS**: Tap Share → "Add to Home Screen"
    - **Android**: Tap Menu (⋮) → "Add to Home screen"

## Notes

- The app uses a single default user (no authentication required)
- All data is stored in your IBM Db2 database
- The SSL certificate is embedded in the code for Db2 connection
