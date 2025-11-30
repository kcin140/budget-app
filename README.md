# Budget App

A private budget-tracking mobile-friendly app using Streamlit, Google Sheets, and IBM watsonx.ai.

## Features

- 📊 **Monthly Dashboard** with spending charts and progress tracking
- 🤖 **AI-powered expense parsing** - enter expenses in natural language
- 📝 **Multiple expenses at once** - "20 at Costco for groceries and 15 for toiletries"
- � **Monthly sheets** - each month gets its own sheet with summary table
- �🗑️ **Delete transactions** - remove accidental entries
- ✏️ **Manage categories** - add, edit, delete, and sort categories
- 📱 **Mobile-friendly** - works great on phones

## Quick Start

### 1. Setup Google Sheets

Follow the detailed guide in [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)

**Summary:**
1. Create Google Cloud project
2. Enable Google Sheets API
3. Create service account and download JSON key
4. Create a Google Spreadsheet
5. Share it with the service account email

### 2. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo 'SPREADSHEET_ID="your-spreadsheet-id"' > .env
echo 'WATSONX_API_KEY="your-key"' >> .env
echo 'WATSONX_PROJECT_ID="your-project"' >> .env

# Place service_account.json in project root

# Run the app
streamlit run app.py
```

### 3. Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy your app
4. Add secrets (see [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) for format)

### 4. Access on Mobile

- Open deployed URL in phone browser
- **iOS**: Safari → Share → "Add to Home Screen"
- **Android**: Chrome → Menu → "Add to Home screen"

## How It Works

### Data Structure

**Categories Sheet:**
- Stores all budget categories and their planned amounts

**Monthly Sheets (e.g., "2024-11"):**
- **Summary Table** (top): Shows planned vs actual spending per category
- **Transaction List** (below): All expenses for that month

### Monthly Summary Example

```
Expenses
                Planned    Actual    Diff.
Totals          $5,777     $750      +$5,027

Grocery (Costco)  $200      $50      +$150
Eating Out        $200      $120     +$80
...
```

## Tech Stack

- **Frontend**: Streamlit
- **Database**: Google Sheets
- **AI**: IBM watsonx.ai (Llama 3.3 70B)
- **Charts**: Plotly

## License

MIT
