# Budget App - Complete Setup Guide

This guide will walk you through setting up the Budget App from scratch, including reserving IBM services, extracting credentials, and running the application locally.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: IBM TechZone Reservations](#step-1-ibm-techzone-reservations)
3. [Step 2: Extract Credentials](#step-2-extract-credentials)
4. [Step 3: Local Development Setup](#step-3-local-development-setup)
5. [Step 4: Verification](#step-4-verification)
6. [Troubleshooting](#troubleshooting)
7. [Optional: Streamlit Cloud Deployment](#optional-streamlit-cloud-deployment)

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
  - Check: `python3 --version`
  - Download: https://www.python.org/downloads/

- **Git** installed
  - Check: `git --version`
  - Download: https://git-scm.com/downloads

- **IBM Cloud Account** (free tier available)
  - Sign up: https://cloud.ibm.com/registration

- **IBM TechZone Access**
  - Required for reserving IBM services
  - Access: https://techzone.ibm.com

---

## Step 1: IBM TechZone Reservations

You need to reserve **TWO** environments from IBM TechZone to get all the required services.

### Reservation 1: watsonx.ai SaaS (with DB2)

**Purpose:** Provides watsonx.ai API and DB2 database

**Steps:**

1. Go to: https://techzone.ibm.com/collection/tech-zone-certified-base-images/journey-watsonx

2. Find: **"watsonx.ai/.governance SaaS"**

3. Click **"Reserve"**

4. ⚠️ **IMPORTANT:** When prompted, select **"Yes"** to install DB2

5. Fill out the reservation form:
   - **Purpose:** Education/Demo
   - **Duration:** Select appropriate timeframe (recommend 2+ weeks)
   - **Region:** Choose closest region to you
   - **Description:** (optional) "Budget app demo"

6. Submit the reservation

7. Wait for email confirmation (usually 15-30 minutes)

8. Once ready, access your environment via the link in the email

**What you get:**
- ✅ watsonx.ai project with API access
- ✅ IBM Db2 database instance
- ✅ IBM Cloud account access

---

### Reservation 2: Watson Discovery GenAI Bundle

**Purpose:** Provides Watson Speech to Text API

**Steps:**

1. Go to: https://techzone.ibm.com/collection/tech-zone-certified-base-images/journey-watsonx

2. Find: **"Watson Discovery GenAI bundle w/StudentID"**

3. Click **"Reserve"**

4. Fill out the reservation form:
   - **Purpose:** Education/Demo
   - **Duration:** Select appropriate timeframe (recommend 2+ weeks)
   - **Region:** Choose closest region to you
   - **Description:** (optional) "Budget app voice input"

5. Submit the reservation

6. Wait for email confirmation

7. Once ready, access your environment via the link in the email

**What you get:**
- ✅ Watson Speech to Text service
- ✅ Watson Discovery service (not used in this app, but included)

---

## Step 2: Extract Credentials

After your TechZone reservations are ready, you need to extract credentials from IBM Cloud.

### 2.1 watsonx.ai API Key & Project ID

#### API Key

1. Log into IBM Cloud: https://cloud.ibm.com

2. Click your **profile icon** (top right) → **Manage** → **Access (IAM)**

3. In the left sidebar, click **API keys**

4. Click **Create** button (or use an existing key)

5. Give it a name (e.g., "Budget App Key")

6. Click **Create**

7. **⚠️ IMPORTANT:** Copy the API key immediately (you won't see it again!)

8. Save this value - you'll add it to `.env` as `WATSONX_API_KEY`

#### Project ID

1. Go to watsonx.ai: https://dataplatform.cloud.ibm.com/wx/home

2. Click on your project (or create one if you don't have one yet)
   - To create: Click "New project" → "Create an empty project"
   - Give it a name (e.g., "Budget App")

3. Once in your project, click the **"Manage"** tab at the top

4. Click **"General"** in the left sidebar

5. Find the **"Project ID"** section

6. **Copy the Project ID**

7. Save this value - you'll add it to `.env` as `WATSONX_PROJECT_ID`

---

### 2.2 DB2 Credentials

1. Log into IBM Cloud: https://cloud.ibm.com

2. Click **Navigation menu** (☰ hamburger icon, top left) → **Resource list**

3. Expand **"Services and software"** section

4. Expand **"Databases"** subsection

5. Click your **Db2** instance (should be named something like "Db2-xx")

6. In the left sidebar, click **"Service credentials"**

7. If no credentials exist:
   - Click **"New credential"** button
   - Give it a name (e.g., "Budget App Credentials")
   - Click **"Add"**

8. Click **"View credentials"** (expand the credential you just created)

9. You'll see a JSON object. Copy the following values to your `.env` file:

| JSON Field | .env Variable | Example Value |
|------------|---------------|---------------|
| `database` | `DB2_DATABASE` | `bludb` |
| `hostname` | `DB2_HOSTNAME` | `b1bc1829-6f45-4cd4.databases.appdomain.cloud` |
| `port` | `DB2_PORT` | `32304` |
| `username` | `DB2_UID` | `xbx18098` |
| `password` | `DB2_PWD` | `f9ReOC94gA6lo1GF` |

**Note:** `DB2_SECURITY` should always be `"SSL"` (already set in `.env.example`)

---

### 2.3 Watson Speech to Text Credentials

1. Log into IBM Cloud: https://cloud.ibm.com

2. Click **Navigation menu** (☰) → **Resource list**

3. Expand **"Services and software"** section

4. Expand **"AI / Machine Learning"** subsection

5. Click your **"Speech to Text"** instance

6. In the left sidebar, click **"Service credentials"**

7. If no credentials exist:
   - Click **"New credential"** button
   - Give it a name (e.g., "Budget App STT")
   - Click **"Add"**

8. Click **"View credentials"** (expand the credential)

9. Copy the following values to your `.env` file:

| JSON Field | .env Variable | Example Value |
|------------|---------------|---------------|
| `apikey` | `SPEECH_TO_TEXT_API_KEY` | `0jBO5BlxbkG6X9rymhGbpo-D8jAxEIxQxEw994wfEMnK` |
| `url` | `SPEECH_TO_TEXT_URL` | `https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/...` |

**Note:** The URL varies by region:
- US South: `https://api.us-south.speech-to-text.watson.cloud.ibm.com`
- Sydney: `https://api.au-syd.speech-to-text.watson.cloud.ibm.com`
- London: `https://api.eu-gb.speech-to-text.watson.cloud.ibm.com`

---

## Step 3: Local Development Setup

### 3.1 Clone Repository

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/budget-app-demo.git

# Navigate into the directory
cd budget-app-demo
```

---

### 3.2 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

**Note:** Always activate the virtual environment before running the app or installing packages.

---

### 3.3 Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This will install:
- `streamlit` - Web framework
- `ibm-watsonx-ai` - AI models
- `ibm-watson` - Speech to text
- `ibm_db` - Database driver
- `pandas`, `plotly` - Data & charts
- And other dependencies

**macOS Note:** If you encounter issues with `ibm_db`, you may need to install GCC:
```bash
brew install gcc
pip install ibm_db
```

**Windows Note:** You may need Visual C++ Build Tools:
- Download: https://visualstudio.microsoft.com/downloads/
- Install "Build Tools for Visual Studio"

---

### 3.4 Configure .env File

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your credentials
# Use your favorite text editor:
nano .env
# or
code .env  # VS Code
# or
vim .env
```

**Fill in ALL the credentials you collected in Step 2:**

```bash
WATSONX_API_KEY="your-api-key-here"
WATSONX_PROJECT_ID="your-project-id-here"

DB2_DATABASE="bludb"
DB2_HOSTNAME="your-hostname.databases.appdomain.cloud"
DB2_PORT="32304"
DB2_UID="your-username"
DB2_PWD="your-password"
DB2_SECURITY="SSL"

SPEECH_TO_TEXT_API_KEY="your-stt-api-key"
SPEECH_TO_TEXT_URL="https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/..."
```

**⚠️ Important:** 
- Make sure there are NO spaces around the `=` sign
- Keep values in quotes
- Don't commit this file to Git (it's in `.gitignore`)

---

### 3.5 Initialize Database

Run these commands **in order**:

#### Step 1: Create Database Schema

```bash
python init_db.py
```

**Expected output:**
```
Connected to Db2.
Executing: CREATE TABLE users...
Success.
Executing: CREATE TABLE categories...
Success.
Executing: CREATE TABLE transactions...
Success.
Executing: CREATE TABLE categorization_rules...
Success.
Executing: INSERT INTO categories...
Success.
Database initialization complete.
```

This creates:
- Database tables (users, categories, transactions, categorization_rules)
- 10 default budget categories:
  - Housing ($3,000)
  - Utilities ($300)
  - Transportation ($400)
  - Groceries ($600)
  - Dining Out ($150)
  - Healthcare ($150)
  - Personal Care ($100)
  - Entertainment ($100)
  - Debt & Savings ($700)
  - Miscellaneous ($100)

#### Step 2: Create Default User

```bash
python create_default_user.py
```

**Expected output:**
```
Connected to Db2
Creating default user...
✓ Default user created successfully!

All users in database:
  - ID: default-user-001, Email: default@budgetapp.local
```

This creates a default user account for the app. (The app currently uses a single default user; multi-user support can be added later.)

---

### 3.6 Run Application

```bash
# Start the Streamlit app
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

The app will automatically open in your default browser at `http://localhost:8501`

**🎉 Success!** Your budget app is now running locally.

**To stop the app:** Press `Ctrl+C` in the terminal

**To restart:** Run `streamlit run app.py` again (make sure virtual environment is activated)

---

## Step 4: Verification

Test each feature to ensure everything is working correctly:

### ✅ Test 1: Database Connection

1. App should load without errors
2. Go to **"Dashboard"** page
3. Should show "No transactions yet" (if fresh install)
4. Go to **"Manage Categories"** page
5. Should show 10 default categories with planned amounts

**If this fails:** Check [Troubleshooting - Database Connection](#database-connection-errors)

---

### ✅ Test 2: AI Text Parsing

1. Go to **"Add Expense"** page
2. Click **"AI Input"** tab
3. In the text box, type: `50 at grocery store for food`
4. Click **"Parse with AI"**
5. Should parse correctly:
   - Amount: 50
   - Vendor: grocery store
   - Category: Groceries
   - Notes: food
6. Click **"Save All"**
7. Go to **"Dashboard"** - expense should appear in the list

**If this fails:** Check [Troubleshooting - watsonx.ai API Errors](#watsonxai-api-errors)

---

### ✅ Test 3: Voice Input

1. Go to **"Add Expense"** → **"AI Input"** tab
2. Click **"🎤 Start"** button
3. **Allow microphone access** when prompted by browser
4. Speak clearly: "Twenty dollars at the gas station"
5. Click **"⏹️ Stop"** button
6. Click **"📝 Transcribe & Parse"**
7. Should transcribe your speech and parse the expense
8. Verify the parsed data is correct
9. Click **"Save All"**

**If this fails:** Check [Troubleshooting - Speech to Text Errors](#speech-to-text-errors)

---

### ✅ Test 4: Receipt Upload

1. Go to **"Add Expense"** → **"Receipt Upload"** tab
2. Upload a receipt image (or take a photo with your phone)
3. Click **"Parse Receipt"**
4. Should extract:
   - Individual items with prices
   - Categories for each item
   - Tax amount
   - Total amount
5. Review the parsed items (edit if needed)
6. Click **"Save All Expenses"**

**Supported formats:** JPG, PNG, HEIC (iPhone photos)

**If this fails:** Check [Troubleshooting - Receipt Parsing](#receipt-parsing-fails)

---

### ✅ Test 5: Category Management

1. Go to **"Manage Categories"** page
2. Try adding a new category:
   - Click **"Add New Category"**
   - Name: "Test Category"
   - Amount: 50
   - Click **"Add Category"**
3. Should appear in the list
4. Try editing it:
   - Click **"Edit"** next to "Test Category"
   - Change amount to 75
   - Click **"Update"**
5. Try deleting it:
   - Click **"Delete"** next to "Test Category"
   - Confirm deletion

---

### ✅ Test 6: Dashboard & Charts

1. Go to **"Dashboard"** page
2. Should see:
   - Total spent vs. planned budget
   - Progress bars for each category
   - Pie chart of spending by category
   - Daily spending chart
   - List of recent transactions

**If all tests pass, your setup is complete! 🎉**

---

## Troubleshooting

### Database Connection Errors

**Error message:**
```
Error connecting to Database: [IBM][CLI Driver] SQL30081N...
```

**Solutions:**

1. **Verify credentials in `.env`:**
   - Check for typos in hostname, username, password
   - Ensure no extra spaces around values
   - Verify port number is correct (usually 32304 or 50001)
   - Make sure values are in quotes

2. **Check DB2 instance status:**
   - Log into IBM Cloud
   - Go to Resource list → Databases
   - Verify your Db2 instance is "Active" (green status)
   - If stopped, click "Start" to restart it

3. **SSL Certificate issues:**
   - Delete `db2_ssl_cert.pem` if it exists in your project folder
   - Restart the app (it will regenerate the certificate)

4. **Test connection directly:**
   ```bash
   python debug_db.py
   ```
   This will show detailed connection information

5. **Firewall/Network issues:**
   - Ensure your firewall allows outbound connections to IBM Cloud
   - If using VPN, try disconnecting temporarily
   - Check if your network blocks port 32304 or 50001

---

### watsonx.ai API Errors

**Error message:**
```
Missing Watsonx credentials
```

**Solutions:**

1. **Verify API key:**
   - Log into IBM Cloud
   - Go to Manage → Access (IAM) → API keys
   - Verify your API key is active (not deleted)
   - Try creating a new API key if needed

2. **Verify Project ID:**
   - Go to watsonx.ai: https://dataplatform.cloud.ibm.com/wx/home
   - Open your project
   - Manage → General → Copy Project ID
   - Ensure it matches the value in `.env`

3. **Check API key permissions:**
   - API key must have access to watsonx.ai service
   - May need "Editor" or "Writer" role on the project
   - Check in IAM: Manage → Access (IAM) → Users → Your user → Access policies

4. **Verify model access:**
   - Ensure your watsonx.ai project has access to:
     - Llama 3.3 70B (for text parsing)
     - Llama 3.2 90B Vision (for receipt parsing)
   - Check in watsonx.ai project settings

---

### Speech to Text Errors

**Error message:**
```
Error transcribing audio: Unauthorized
```

**Solutions:**

1. **Verify STT credentials:**
   - Log into IBM Cloud
   - Resource list → AI / Machine Learning → Speech to Text
   - Check service credentials
   - Verify API key and URL match `.env`

2. **Check service status:**
   - Ensure Speech to Text instance is "Active"
   - Try creating new service credentials if needed

3. **Verify URL region:**
   - URL must match your service region
   - Check the URL in your service credentials
   - Common URLs:
     - US South: `https://api.us-south.speech-to-text.watson.cloud.ibm.com`
     - Sydney: `https://api.au-syd.speech-to-text.watson.cloud.ibm.com`
     - London: `https://api.eu-gb.speech-to-text.watson.cloud.ibm.com`

4. **Browser microphone permissions:**
   - Ensure browser has microphone access
   - Check browser settings → Privacy → Microphone
   - Try a different browser if issues persist

---

### Module Import Errors

**Error message:**
```
ModuleNotFoundError: No module named 'ibm_db'
```

**Solutions:**

1. **Ensure virtual environment is activated:**
   ```bash
   # You should see (venv) in your prompt
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **macOS specific - install GCC:**
   ```bash
   brew install gcc
   pip install ibm_db
   ```

4. **Windows specific - install Visual C++:**
   - Download: https://visualstudio.microsoft.com/downloads/
   - Install "Build Tools for Visual Studio"
   - Restart terminal and try again

5. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.8 or higher
   ```

---

### Receipt Parsing Fails

**Error message:**
```
Error parsing receipt: Image too large
```

**Solutions:**

1. **Resize image before upload:**
   - Maximum size: 2048x2048 pixels
   - App auto-resizes, but very large images may timeout
   - Try compressing the image first

2. **Check image format:**
   - Supported: JPG, PNG, HEIC (iPhone)
   - If HEIC fails, convert to JPG first

3. **Verify watsonx.ai vision model access:**
   - Ensure your project has access to Llama 3.2 90B Vision
   - Check project settings in watsonx.ai

4. **Image quality:**
   - Ensure receipt is clearly visible
   - Good lighting, no blur
   - Text should be readable

---

### App Won't Start

**Error message:**
```
streamlit: command not found
```

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Reinstall Streamlit:**
   ```bash
   pip install streamlit
   ```

3. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.8 or higher
   ```

4. **Try running with python -m:**
   ```bash
   python -m streamlit run app.py
   ```

---

### Still Having Issues?

1. **Check all credentials are correct** in `.env`
2. **Verify IBM Cloud services are active** (not stopped or expired)
3. **Try running in a fresh virtual environment:**
   ```bash
   deactivate  # if currently in venv
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Check firewall/proxy settings** (may block IBM Cloud connections)
5. **Review error logs** in terminal for specific error messages

**Common mistakes:**
- ❌ Forgot to activate virtual environment
- ❌ Typos in `.env` file
- ❌ Using wrong region URL for services
- ❌ API key doesn't have proper permissions
- ❌ DB2 instance is stopped/inactive
- ❌ TechZone reservation expired

---

## Optional: Streamlit Cloud Deployment

Want to access your budget app from anywhere? Deploy to Streamlit Cloud for free!

### Prerequisites
- GitHub account
- Your code pushed to a GitHub repository

### Steps

#### 1. Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Budget app setup"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR-USERNAME/budget-app-demo.git

# Push to GitHub
git push -u origin main
```

**Note:** The `.env` file is in `.gitignore`, so your credentials won't be pushed to GitHub.

---

#### 2. Deploy to Streamlit Cloud

1. Go to: https://share.streamlit.io

2. Sign in with your GitHub account

3. Click **"New app"** button

4. Configure deployment:
   - **Repository:** Select your repository
   - **Branch:** main
   - **Main file path:** `app.py`

5. Click **"Advanced settings"**

---

#### 3. Add Secrets

1. In the Advanced settings, click **"Secrets"** section

2. Paste your credentials in **TOML format**:

```toml
WATSONX_API_KEY = "your-api-key"
WATSONX_PROJECT_ID = "your-project-id"

DB2_DATABASE = "bludb"
DB2_HOSTNAME = "your-hostname.databases.appdomain.cloud"
DB2_PORT = "32304"
DB2_UID = "your-username"
DB2_PWD = "your-password"
DB2_SECURITY = "SSL"

SPEECH_TO_TEXT_API_KEY = "your-stt-key"
SPEECH_TO_TEXT_URL = "https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/..."
```

**⚠️ Important:** 
- Use TOML format (no quotes around keys, use `=` not `:`)
- Values should be in quotes
- No commas between lines

---

#### 4. Deploy

1. Click **"Deploy"** button

2. Wait for deployment (usually 2-3 minutes)

3. Your app will be live at: `https://your-app-name.streamlit.app`

4. Share this URL with anyone you want to give access to

---

#### 5. Access on Mobile

**iOS (iPhone/iPad):**
1. Open the app URL in Safari
2. Tap the **Share** button (square with arrow)
3. Scroll down and tap **"Add to Home Screen"**
4. Tap **"Add"**
5. App icon will appear on your home screen

**Android:**
1. Open the app URL in Chrome
2. Tap the **Menu** button (three dots)
3. Tap **"Add to Home screen"**
4. Tap **"Add"**
5. App icon will appear on your home screen

Now you can access your budget app like a native mobile app!

---

### Streamlit Cloud Notes

**Free tier includes:**
- 1 GB RAM
- 1 CPU core
- Unlimited public apps
- Perfect for personal use

**Limitations:**
- App goes to sleep after inactivity (wakes up when accessed)
- Public apps are visible to anyone with the URL
- For private apps, upgrade to paid plan

**Updating your app:**
- Push changes to GitHub
- Streamlit Cloud auto-deploys updates
- Changes appear within 1-2 minutes

---

## Customization

### Adding Custom Categories

You can add categories through the app UI:

1. Run the app
2. Go to **"Manage Categories"** page
3. Click **"Add New Category"**
4. Enter name and planned amount
5. Click **"Add Category"**

### Modifying Default Categories

To change the default categories that are created during setup:

1. Edit `schema.sql` (lines 43-52)
2. Modify the category names and amounts
3. Drop and recreate the database:
   ```bash
   # This will delete all data!
   python init_db.py
   python create_default_user.py
   ```

### Changing Budget Amounts

To update planned amounts for existing categories:

1. Go to **"Manage Categories"** page
2. Click **"Edit"** next to any category
3. Update the planned amount
4. Click **"Update"**

---

## Next Steps

Now that your app is set up:

1. **Start tracking expenses** - Add your first expense using AI, voice, or receipt upload
2. **Customize categories** - Adjust planned amounts to match your budget
3. **Review dashboard** - Check your spending progress
4. **Deploy to cloud** (optional) - Access from anywhere
5. **Add to mobile home screen** - Quick access on your phone

**Enjoy your AI-powered budget tracking! 💰📊**

---

## Additional Resources

- **IBM watsonx.ai Documentation:** https://www.ibm.com/docs/en/watsonx-as-a-service
- **IBM Db2 Documentation:** https://www.ibm.com/docs/en/db2-on-cloud
- **Watson Speech to Text Documentation:** https://cloud.ibm.com/docs/speech-to-text
- **Streamlit Documentation:** https://docs.streamlit.io
- **IBM TechZone:** https://techzone.ibm.com

---

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review error messages in the terminal
3. Verify all IBM Cloud services are active
4. Ensure credentials in `.env` are correct
5. Try the verification tests to isolate the issue

---

**Last Updated:** December 2024