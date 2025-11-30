import streamlit as st
import pandas as pd
from sheets_client import (
    get_categories, add_category, update_category, delete_category,
    add_transaction, get_transactions, delete_transaction,
    get_month_sheet_name, get_available_months
)
from utils.categorizer import categorize_expense
from utils.charts import progress_bar, pie_chart, daily_spending
import time
from datetime import datetime

# Page Config
st.set_page_config(page_title="Budget App", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for mobile friendliness
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 1.2em;
    }
    .stTextInput>div>div>input {
        font-size: 1.2em;
    }
</style>
""", unsafe_allow_html=True)

# Main App
st.sidebar.title("Budget App")

# Month selector
try:
    available_months = get_available_months()
    if not available_months:
        available_months = [get_month_sheet_name()]
    selected_month = st.sidebar.selectbox("Select Month", available_months, index=0)
except Exception as e:
    st.error(f"Error connecting to Google Sheets: {e}")
    st.info("Make sure you've set up the Google Sheets API and added your credentials to Streamlit secrets.")
    st.stop()

page = st.sidebar.radio("Navigation", ["Dashboard", "Add Expense", "Manage Categories", "Settings"])

# Fetch Categories
@st.cache_data(ttl=60)
def get_categories_cached():
    return get_categories()

categories_data = get_categories_cached()
category_names = [c['name'] for c in categories_data]
category_map = {c['name']: i for i, c in enumerate(categories_data)}

if page == "Dashboard":
    st.title(f"Dashboard - {selected_month}")
    
    # Fetch Transactions for selected month
    transactions = get_transactions(selected_month)
    
    if transactions:
        df = pd.DataFrame(transactions)
        df['amount'] = pd.to_numeric(df['amount'])
        
        # Calculate totals
        total_spent = df['amount'].sum()
        total_planned = sum(float(c['planned_amount']) for c in categories_data)
        
        col1, col2 = st.columns(2)
        col1.metric("Total Spent", f"${total_spent:.2f}")
        col2.metric("Total Planned", f"${total_planned:.2f}", delta=f"${total_planned - total_spent:.2f}")
        
        st.subheader("Progress by Category")
        # Group by category
        category_spending = df.groupby('category')['amount'].sum().reset_index()
        
        # Import the new chart function
        from utils.charts import category_progress_chart
        st.plotly_chart(category_progress_chart(categories_data, category_spending), use_container_width=True, key="category_progress")
            
        st.subheader("Spending Distribution")
        st.plotly_chart(pie_chart(category_spending), use_container_width=True, key="pie_chart")
        
        # Recent Transactions with delete option
        st.subheader("Recent Transactions")
        
        df_sorted = df.sort_values('date', ascending=False)
        
        for idx, row in df_sorted.head(20).iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 2, 1])
            with col1:
                st.write(f"**{row['vendor']}**")
            with col2:
                st.write(f"{row['category']}")
            with col3:
                st.write(f"${row['amount']:.2f}")
            with col4:
                st.write(row['date'])
            with col5:
                if st.button("🗑️", key=f"delete_{idx}"):
                    try:
                        delete_transaction(selected_month, row['row'])
                        st.success("Deleted!")
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
    else:
        st.info("No transactions found for this month. Add some expenses!")

elif page == "Add Expense":
    st.title("Add Expense")
    
    tab_receipt, tab_ai, tab_manual = st.tabs(["📸 Receipt Photo", "🤖 AI Input", "✍️ Manual Input"])
    
    with tab_receipt:
        st.subheader("Scan Receipt")
        st.info("📱 On mobile: Use camera to snap a photo. 💻 On desktop: Upload a saved image.")
        
        # Camera input (works on mobile)
        camera_photo = st.camera_input("Take a picture of your receipt")
        
        # File uploader (works on desktop)
        uploaded_file = st.file_uploader("Or upload a receipt image", type=['jpg', 'jpeg', 'png', 'heic'])
        
        # Use whichever input is available
        image_source = camera_photo if camera_photo else uploaded_file
        
        if image_source:
            try:
                # Get the bytes
                image_bytes = image_source.getvalue()
                
                # Register HEIF opener for HEIC files (iPhone photos)
                try:
                    from pillow_heif import register_heif_opener
                    register_heif_opener()
                except ImportError:
                    pass  # HEIF support not available
                
                # Validate it's a real image
                from PIL import Image
                from io import BytesIO
                test_image = Image.open(BytesIO(image_bytes))
                test_image.verify()  # Verify it's a valid image
                
                # Display the image
                st.image(image_bytes, caption="Receipt Image", use_container_width=True)
                
                if st.button("🔍 Parse Receipt", type="primary"):
                    with st.spinner("Analyzing receipt with AI..."):
                        from utils.receipt_parser import parse_receipt_image
                        
                        # Parse receipt
                        result = parse_receipt_image(image_bytes, category_names)
                        
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                        if "raw" in result:
                            with st.expander("Show raw response"):
                                st.code(result['raw'])
                    else:
                        items = result.get('items', [])
                        if items:
                            st.session_state.receipt_items = items
                            st.success(f"✅ Found {len(items)} item(s) on receipt!")
                        else:
                            st.warning("No items found on receipt. Try manual entry instead.")
                            if "raw" in result:
                                with st.expander("Debug: Raw Model Response"):
                                    st.text(result['raw'])
            
            except Exception as e:
                st.error(f"Invalid image file: {e}")
                st.info("Please upload a valid image file (JPG, PNG, or HEIC)")
        
        # Display parsed items for review
        if 'receipt_items' in st.session_state:
            items = st.session_state.receipt_items
            
            st.write(f"**Review {len(items)} item(s):**")
            
            # Store edited items
            if 'edited_receipt_items' not in st.session_state:
                st.session_state.edited_receipt_items = items.copy()
            
            # Display each item for editing
            for idx, item in enumerate(st.session_state.edited_receipt_items):
                with st.expander(f"Item {idx + 1}: {item.get('description', 'Unknown')} - ${item.get('amount', 0):.2f}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        description = st.text_input(f"Description", value=item.get('description', ''), key=f"receipt_desc_{idx}")
                        amount = st.number_input(f"Amount", value=float(item.get('amount', 0)), key=f"receipt_amount_{idx}")
                    with col2:
                        category = st.selectbox(f"Category", category_names,
                                               index=category_names.index(item.get('category')) if item.get('category') in category_names else 0,
                                               key=f"receipt_category_{idx}")
                        item_date = st.date_input(f"Date", value=datetime.now(), key=f"receipt_date_{idx}")
                    
                    # Update item
                    st.session_state.edited_receipt_items[idx] = {
                        'description': description,
                        'amount': amount,
                        'category': category,
                        'date': item_date
                    }
            
            # Save all button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("💾 Save All", type="primary", key="save_receipt_items"):
                    try:
                        saved_count = 0
                        for item in st.session_state.edited_receipt_items:
                            add_transaction(
                                category=item['category'],
                                amount=item['amount'],
                                vendor=item['description'],  # Use description as vendor
                                notes=f"From receipt",
                                date=datetime.combine(item.get('date', datetime.now()), datetime.min.time())
                            )
                            saved_count += 1
                        
                        st.success(f"✅ Saved {saved_count} item(s)!")
                        del st.session_state.receipt_items
                        del st.session_state.edited_receipt_items
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving: {e}")
                        import traceback
                        st.code(traceback.format_exc())
            with col2:
                if st.button("❌ Cancel", key="cancel_receipt"):
                    del st.session_state.receipt_items
                    if 'edited_receipt_items' in st.session_state:
                        del st.session_state.edited_receipt_items
                    st.rerun()
    
    with tab_ai:
        st.subheader("Natural Language Input")
        text_input = st.text_area("Describe your expense(s)", placeholder="e.g., 20 at Costco for groceries and 15 for toiletries")
        
        if st.button("Parse with AI"):
            if text_input:
                with st.spinner("Parsing..."):
                    result = categorize_expense(text_input, category_names)
                    
                if "error" in result:
                    st.error(f"AI Error: {result['error']}")
                else:
                    st.session_state.ai_result = result
                    st.success(f"Parsed successfully! Found {len(result.get('expenses', []))} expense(s).")
            else:
                st.warning("Please enter some text.")
        
        if 'ai_result' in st.session_state:
            expenses = st.session_state.ai_result.get('expenses', [])
            
            if expenses:
                st.write(f"**Review {len(expenses)} expense(s):**")
                
                # Store edited expenses in session state
                if 'edited_expenses' not in st.session_state:
                    st.session_state.edited_expenses = expenses.copy()
                
                # Display each expense for editing
                for idx, expense in enumerate(st.session_state.edited_expenses):
                    with st.expander(f"Expense {idx + 1}: ${expense.get('amount', 0)} at {expense.get('vendor', 'Unknown')}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            amount = st.number_input(f"Amount", value=float(expense.get('amount', 0)), key=f"amount_{idx}")
                            vendor = st.text_input(f"Vendor", value=expense.get('vendor', ''), key=f"vendor_{idx}")
                            expense_date = st.date_input(f"Date (optional)", value=datetime.now(), key=f"date_{idx}")
                        with col2:
                            category = st.selectbox(f"Category", category_names, 
                                                   index=category_names.index(expense.get('category')) if expense.get('category') in category_names else 0,
                                                   key=f"category_{idx}")
                            notes = st.text_input(f"Notes", value=expense.get('notes', ''), key=f"notes_{idx}")
                        
                        # Update the expense in session state
                        st.session_state.edited_expenses[idx] = {
                            'amount': amount,
                            'vendor': vendor,
                            'category': category,
                            'notes': notes,
                            'date': expense_date
                        }
                
                # Save all button
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("Save All", type="primary"):
                        try:
                            saved_count = 0
                            for expense in st.session_state.edited_expenses:
                                add_transaction(
                                    category=expense['category'],
                                    amount=expense['amount'],
                                    vendor=expense['vendor'],
                                    notes=expense['notes'],
                                    date=datetime.combine(expense.get('date', datetime.now()), datetime.min.time())
                                )
                                saved_count += 1
                            
                            st.success(f"Saved {saved_count} expense(s)!")
                            del st.session_state.ai_result
                            del st.session_state.edited_expenses
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving: {e}")
                            import traceback
                            st.code(traceback.format_exc())
                with col2:
                    if st.button("Cancel"):
                        del st.session_state.ai_result
                        if 'edited_expenses' in st.session_state:
                            del st.session_state.edited_expenses
                        st.rerun()

    with tab_manual:
        st.subheader("Manual Entry")
        with st.form("manual_expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Amount", min_value=0.0, step=0.01)
                vendor = st.text_input("Vendor")
            with col2:
                category = st.selectbox("Category", category_names)
                expense_date = st.date_input("Date (optional)", value=datetime.now())
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Save Expense"):
                try:
                    add_transaction(
                        category=category,
                        amount=amount,
                        vendor=vendor,
                        notes=notes,
                        date=datetime.combine(expense_date, datetime.min.time())
                    )
                    st.success("Expense saved!")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving: {e}")

elif page == "Manage Categories":
    st.title("Manage Categories")
    
    # Sort categories
    st.subheader("Existing Categories")
    
    if not categories_data:
        st.info("No categories yet. Add your first category below!")
    else:
        # Add sorting option
        sort_by = st.radio("Sort by:", ["Name", "Planned Amount"], horizontal=True)
        
        categories_df = pd.DataFrame(categories_data)
        if sort_by == "Name":
            categories_df = categories_df.sort_values('name')
        else:
            categories_df['planned_amount'] = pd.to_numeric(categories_df['planned_amount'])
            categories_df = categories_df.sort_values('planned_amount', ascending=False)
        
        # Display categories with edit and delete options
        for idx, row in categories_df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                st.write(f"**{row['name']}**")
            with col2:
                st.write(f"Planned: ${float(row['planned_amount']):.2f}")
            with col3:
                # Edit button
                if st.button("✏️", key=f"edit_{idx}"):
                    st.session_state[f"editing_{idx}"] = True
            with col4:
                if st.button("🗑️", key=f"delete_cat_{idx}"):
                    try:
                        delete_category(row['name'])
                        st.success("Deleted!")
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            # Inline editing
            if st.session_state.get(f"editing_{idx}", False):
                with st.form(f"edit_form_{idx}"):
                    new_name = st.text_input("Category Name", value=row['name'])
                    new_planned = st.number_input("Planned Amount", value=float(row['planned_amount']), min_value=0.0, step=10.0)
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("Save"):
                            try:
                                update_category(row['name'], new_name, new_planned)
                                st.success("Updated!")
                                del st.session_state[f"editing_{idx}"]
                                st.cache_data.clear()
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            del st.session_state[f"editing_{idx}"]
                            st.rerun()
    
    st.divider()
    
    st.subheader("Add New Category")
    with st.form("add_category"):
        new_name = st.text_input("Category Name")
        new_planned = st.number_input("Planned Amount", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Add Category"):
            try:
                add_category(new_name, new_planned)
                st.success("Category added!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error adding category: {e}")

elif page == "Settings":
    st.title("Settings")
    st.write("Google Sheets Configuration")
    st.info("Your budget data is stored in Google Sheets. Each month gets its own sheet with a summary table and transaction list.")
    
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")
