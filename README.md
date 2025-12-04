# Budget App

> 🚀 **New User?** See [SETUP.md](SETUP.md) for complete setup instructions including IBM TechZone reservations and credential configuration.

A private budget-tracking mobile-friendly app using Streamlit, IBM watsonx.ai, Watson Speech-to-Text, and IBM Db2.

## Features

- 📊 **Monthly Dashboard** with spending charts and progress tracking
- 🤖 **AI-Powered Categorization** - Natural language expense parsing
- 🎤 **Voice Input** - Speak your expenses hands-free
- 📸 **Receipt Scanning** - Upload photos for automatic parsing
- 📱 **Mobile-Friendly** - Works great on phones
- 🗓️ **Monthly Tracking** - Organized by month with summaries
- ✏️ **Manage Categories** - Add, edit, delete budget categories

### 📸 Receipt Scanning

- **Visual Recognition**: Upload photos or take pictures of receipts directly in the app
- **AI Parsing**: Uses Llama 3.2 Vision to extract line items, prices, and descriptions
- **Smart Categorization**: Automatically maps receipt items to your budget categories
- **HEIC Support**: Works seamlessly with iPhone photos

### 🤖 AI-Powered Features

- **Natural Language**: "50 at grocery store and 20 at gas station"
- **Multiple Expenses**: Parse several expenses at once
- **Voice Input**: Speak expenses using Watson Speech to Text
- **Smart Categories**: AI understands context and categorizes correctly

### 🗣️ Voice Input

- **Hands-Free**: Record expenses while shopping or driving
- **Watson Speech to Text**: Enterprise-grade speech recognition
- **Instant Parsing**: Transcription automatically parsed by AI
- **Mobile-Friendly**: Works great on phone browsers

## Quick Start

**Prerequisites:**
- Python 3.8+
- IBM Cloud account (free tier available)
- Access to IBM TechZone

**Setup Steps:**
1. Reserve IBM TechZone environments (watsonx.ai + Watson STT)
2. Extract credentials from IBM Cloud
3. Clone this repository
4. Configure `.env` file with your credentials
5. Initialize database
6. Run the app

📖 **See [SETUP.md](SETUP.md) for detailed step-by-step instructions.**

## Tech Stack

- **Frontend**: Streamlit
- **Database**: IBM Db2 on Cloud
- **AI (Text)**: IBM watsonx.ai (Llama 3.3 70B)
- **AI (Vision)**: IBM watsonx.ai (Llama 3.2 90B Vision)
- **Speech**: IBM Watson Speech to Text
- **Charts**: Plotly

## How It Works

### Data Structure

**Categories Table:**
- Stores all budget categories and their planned amounts
- 10 default categories included (Housing, Utilities, Transportation, etc.)
- Fully customizable through the app UI

**Transactions Table:**
- All expenses with amount, vendor, category, notes, and timestamp
- Linked to categories for automatic budget tracking
- Monthly summaries and analytics

**Users Table:**
- Multi-user support (currently uses default user)
- Can be extended for authentication

### AI Processing Pipeline

```
User Input → watsonx.ai → Structured Data → Db2 Storage
     ↓
Voice/Text/Image → AI Parsing → Category Assignment → Dashboard
```

## Documentation

- **[SETUP.md](SETUP.md)** - Complete setup guide with IBM TechZone reservations
- **[IBM_TECHNOLOGY_OVERVIEW.md](IBM_TECHNOLOGY_OVERVIEW.md)** - Technical details about IBM services
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Streamlit Cloud deployment guide
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Development roadmap and architecture

## Default Budget Categories

The app comes with 10 universal budget categories (total: $5,600/month):

| Category | Default Amount | Description |
|----------|----------------|-------------|
| Housing | $3,000 | Mortgage/Rent, HOA, Property Tax |
| Utilities | $300 | Electric, Water, Gas, Internet, Phone |
| Transportation | $400 | Gas, Car Insurance, Maintenance |
| Groceries | $600 | All grocery shopping |
| Dining Out | $150 | Restaurants, Coffee, Fast Food |
| Healthcare | $150 | Medical, Dental, Vision, Prescriptions |
| Personal Care | $100 | Toiletries, Cleaning, Gym |
| Entertainment | $100 | Subscriptions, Hobbies, Activities |
| Debt & Savings | $700 | Debt Payments, Savings, Investments |
| Miscellaneous | $100 | Gifts, Pet Care, Other |

**Note:** All categories and amounts are fully customizable through the app UI.

## Usage Examples

### Adding Expenses with AI

**Text Input:**
```
"50 at grocery store and 20 at gas station"
```
→ Creates 2 expenses, automatically categorized

**Voice Input:**
1. Click 🎤 Start
2. Say: "Thirty dollars at the pharmacy for medicine"
3. Click ⏹️ Stop
4. Click 📝 Transcribe & Parse
→ Transcribed and categorized automatically

**Receipt Upload:**
1. Take photo of receipt or upload image
2. Click "Parse Receipt"
→ All items extracted and categorized

### Managing Budget

**View Dashboard:**
- See total spending vs. planned budget
- Progress bars for each category
- Pie chart of spending distribution
- Daily spending trends

**Manage Categories:**
- Add new categories
- Edit planned amounts
- Delete unused categories
- Reorder categories

## Mobile Access

### Local Development
Open `http://localhost:8501` on your phone (same network)

### Deployed App
1. Deploy to Streamlit Cloud (see [SETUP.md](SETUP.md))
2. Access from anywhere via URL
3. Add to home screen:
   - **iOS**: Safari → Share → "Add to Home Screen"
   - **Android**: Chrome → Menu → "Add to Home screen"

## Development

### Project Structure

```
budget-app-demo/
├── app.py                      # Main Streamlit application
├── db_client.py                # Database connection and queries
├── init_db.py                  # Database initialization script
├── create_default_user.py      # User creation script
├── schema.sql                  # Database schema and seed data
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── .env.example                # Environment variables template
├── utils/
│   ├── categorizer.py          # AI expense categorization
│   ├── receipt_parser.py       # Receipt image parsing
│   ├── speech_to_text.py       # Voice transcription
│   └── charts.py               # Dashboard visualizations
├── SETUP.md                    # Complete setup guide
├── DEPLOYMENT.md               # Deployment instructions
└── IBM_TECHNOLOGY_OVERVIEW.md  # Technical documentation
```

### Running Tests

```bash
# Test database connection
python debug_db.py

# Test AI parsing (requires credentials)
python -c "from utils.categorizer import categorize_expense; print(categorize_expense('20 at store', ['Groceries']))"
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Troubleshooting

Common issues and solutions:

**Database Connection Failed:**
- Verify DB2 credentials in `.env`
- Check DB2 instance is active in IBM Cloud
- See [SETUP.md - Troubleshooting](SETUP.md#troubleshooting)

**AI Parsing Errors:**
- Verify watsonx.ai API key and project ID
- Check API key has proper permissions
- Ensure project has access to Llama models

**Voice Input Not Working:**
- Check browser microphone permissions
- Verify Watson STT credentials
- Try a different browser

**Receipt Upload Fails:**
- Ensure image is under 2048x2048 pixels
- Check supported formats (JPG, PNG, HEIC)
- Verify watsonx.ai vision model access

For detailed troubleshooting, see [SETUP.md - Troubleshooting](SETUP.md#troubleshooting)

## IBM Technology

This app showcases four IBM technologies:

1. **IBM watsonx.ai** - AI-powered expense parsing and receipt analysis
2. **IBM Db2 on Cloud** - Reliable, scalable database storage
3. **IBM Watson Speech to Text** - Voice input transcription
4. **IBM Cloud** - Secure, enterprise-grade infrastructure

For technical details, see [IBM_TECHNOLOGY_OVERVIEW.md](IBM_TECHNOLOGY_OVERVIEW.md)

## License

MIT

## Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Powered by [IBM watsonx.ai](https://www.ibm.com/watsonx)
- Database by [IBM Db2](https://www.ibm.com/cloud/db2-on-cloud)
- Speech by [IBM Watson](https://www.ibm.com/cloud/watson-speech-to-text)

---

**Ready to get started?** → [SETUP.md](SETUP.md)
