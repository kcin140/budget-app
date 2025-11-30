import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_client():
    """Get authenticated Google Sheets client"""
    try:
        # Try Streamlit secrets first (for deployment)
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except:
        # Fall back to local JSON file
        creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
    
    return gspread.authorize(creds)

def get_spreadsheet():
    """Get the budget spreadsheet"""
    client = get_sheets_client()
    
    # Try to get from secrets/env
    try:
        sheet_id = st.secrets.get("SPREADSHEET_ID")
    except:
        sheet_id = os.environ.get("SPREADSHEET_ID")
    
    if not sheet_id:
        raise ValueError("SPREADSHEET_ID not found in secrets or environment")
    
    return client.open_by_key(sheet_id)

# ===== CATEGORY FUNCTIONS =====

def get_categories():
    """Get all categories from the Categories sheet"""
    spreadsheet = get_spreadsheet()
    
    try:
        sheet = spreadsheet.worksheet("Categories")
    except:
        # Create Categories sheet if it doesn't exist
        sheet = spreadsheet.add_worksheet(title="Categories", rows=100, cols=2)
        sheet.update('A1:B1', [['Category', 'Planned Amount']])
    
    data = sheet.get_all_records()
    return [{'name': row['Category'], 'planned_amount': row['Planned Amount']} for row in data]

def add_category(name, planned_amount):
    """Add a new category"""
    spreadsheet = get_spreadsheet()
    sheet = spreadsheet.worksheet("Categories")
    sheet.append_row([name, planned_amount])

def update_category(old_name, new_name, planned_amount):
    """Update a category"""
    spreadsheet = get_spreadsheet()
    sheet = spreadsheet.worksheet("Categories")
    
    # Find the row
    cell = sheet.find(old_name)
    if cell:
        sheet.update(f'A{cell.row}:B{cell.row}', [[new_name, planned_amount]])

def delete_category(name):
    """Delete a category"""
    spreadsheet = get_spreadsheet()
    sheet = spreadsheet.worksheet("Categories")
    
    # Find and delete the row
    cell = sheet.find(name)
    if cell:
        sheet.delete_rows(cell.row)

# ===== MONTHLY SHEET FUNCTIONS =====

def get_month_sheet_name(date=None):
    """Get sheet name for a given month (e.g., '2024-11')"""
    if date is None:
        date = datetime.now()
    return date.strftime('%Y-%m')

def ensure_monthly_sheet(month_name=None):
    """Create monthly sheet if it doesn't exist, with summary table"""
    if month_name is None:
        month_name = get_month_sheet_name()
    
    spreadsheet = get_spreadsheet()
    
    try:
        sheet = spreadsheet.worksheet(month_name)
        return sheet
    except:
        # Create new sheet
        sheet = spreadsheet.add_worksheet(title=month_name, rows=1000, cols=10)
        
        # Set up summary table headers
        sheet.update('A1:A1', [['Expenses']])
        sheet.update('B2:D2', [['Planned', 'Actual', 'Diff.']])
        sheet.update('A3:A3', [['Totals']])
        
        # Add transaction headers (starting at row 35)
        sheet.update('A35:E35', [['Date', 'Vendor', 'Category', 'Amount', 'Notes']])
        
        # Format summary section
        sheet.format('A1:D1', {'textFormat': {'bold': True, 'fontSize': 14}})
        sheet.format('A2:D2', {'textFormat': {'bold': True}})
        sheet.format('A3:D3', {'textFormat': {'bold': True}})
        sheet.format('A35:E35', {'textFormat': {'bold': True}})
        
        return sheet

def update_monthly_summary(month_name=None):
    """Update the summary table for a month"""
    if month_name is None:
        month_name = get_month_sheet_name()
    
    spreadsheet = get_spreadsheet()
    sheet = spreadsheet.worksheet(month_name)
    
    # Get categories
    categories = get_categories()
    
    # Get transactions for this month
    transactions = get_transactions(month_name)
    
    # Calculate actual spending per category
    actual_by_category = {}
    for trans in transactions:
        cat = trans['category']
        actual_by_category[cat] = actual_by_category.get(cat, 0) + trans['amount']
    
    # Build summary rows
    summary_rows = []
    total_planned = 0
    total_actual = 0
    
    for cat in categories:
        name = cat['name']
        planned = float(cat['planned_amount'])
        actual = actual_by_category.get(name, 0)
        diff = planned - actual
        
        total_planned += planned
        total_actual += actual
        
        summary_rows.append([name, f'${planned:.0f}', f'${actual:.0f}', f'+${diff:.0f}' if diff >= 0 else f'-${abs(diff):.0f}'])
    
    # Update totals
    total_diff = total_planned - total_actual
    sheet.update('B3:D3', [[f'${total_planned:.0f}', f'${total_actual:.0f}', f'+${total_diff:.0f}' if total_diff >= 0 else f'-${abs(total_diff):.0f}']])
    
    # Update category rows (starting at row 4)
    if summary_rows:
        sheet.update(f'A4:D{4+len(summary_rows)-1}', summary_rows)

# ===== TRANSACTION FUNCTIONS =====

def add_transaction(category, amount, vendor, notes='', date=None):
    """Add a transaction to the appropriate monthly sheet"""
    if date is None:
        date = datetime.now()
    
    month_name = get_month_sheet_name(date)
    sheet = ensure_monthly_sheet(month_name)
    
    # Find next empty row in transaction section (starting from row 36)
    values = sheet.col_values(1)  # Get column A
    next_row = len([v for v in values if v]) + 1
    if next_row < 36:
        next_row = 36
    
    # Add transaction
    date_str = date.strftime('%Y-%m-%d')
    sheet.update(f'A{next_row}:E{next_row}', [[date_str, vendor, category, amount, notes]])
    
    # Update summary
    update_monthly_summary(month_name)

def get_transactions(month_name=None):
    """Get all transactions for a month"""
    if month_name is None:
        month_name = get_month_sheet_name()
    
    try:
        spreadsheet = get_spreadsheet()
        sheet = spreadsheet.worksheet(month_name)
        
        # Get all values starting from row 36
        all_values = sheet.get_all_values()
        
        transactions = []
        for row in all_values[35:]:  # Skip to row 36 (index 35)
            if row[0]:  # If date exists
                transactions.append({
                    'date': row[0],
                    'vendor': row[1],
                    'category': row[2],
                    'amount': float(row[3]) if row[3] else 0,
                    'notes': row[4] if len(row) > 4 else '',
                    'row': all_values.index(row) + 1  # Store row number for deletion
                })
        
        return transactions
    except:
        return []

def delete_transaction(month_name, row_number):
    """Delete a transaction"""
    spreadsheet = get_spreadsheet()
    sheet = spreadsheet.worksheet(month_name)
    sheet.delete_rows(row_number)
    
    # Update summary
    update_monthly_summary(month_name)

def get_available_months():
    """Get list of all month sheets"""
    spreadsheet = get_spreadsheet()
    sheets = spreadsheet.worksheets()
    
    # Filter for month sheets (YYYY-MM format)
    import re
    month_pattern = re.compile(r'^\d{4}-\d{2}$')
    months = [s.title for s in sheets if month_pattern.match(s.title)]
    
    return sorted(months, reverse=True)  # Most recent first
