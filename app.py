import streamlit as st
import pandas as pd
from db_client import get_db_connection, execute_query
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

# Database Connection
conn = get_db_connection()
if not conn:
    st.error("Db2 connection failed. Please check your .env file.")
    st.stop()

# Use a default user ID (no authentication required)
DEFAULT_USER_ID = "default-user-001"

# Main App
user_id = DEFAULT_USER_ID
st.sidebar.title("Budget App")
page = st.sidebar.radio("Navigation", ["Dashboard", "Add Expense", "Manage Categories", "Settings"])

# Fetch Categories
@st.cache_data(ttl=60)
def get_categories():
    # We need to pass conn to the function or recreate it, but conn is global here.
    # Streamlit cache might have issues with connection objects.
    # Better to fetch fresh data.
    # Since we can't pickle the connection object easily for cache, we might need to reconnect inside cached func
    # or just not cache the connection but cache the data.
    # For simplicity, let's just run the query.
    return execute_query(conn, "SELECT * FROM categories")

categories_data = get_categories()
categories_df = pd.DataFrame(categories_data)
category_names = [c['name'] for c in categories_data] if categories_data else []
category_map = {c['name']: c['id'] for c in categories_data} if categories_data else {}

if page == "Dashboard":
    st.title("Dashboard")
    
    # Fetch Transactions
    transactions = execute_query(conn, "SELECT * FROM transactions WHERE user_id = ?", (user_id,))
    df = pd.DataFrame(transactions)
    
    if not df.empty:
        # Merge with categories to get names
        df['category_name'] = df['category_id'].map({v: k for k, v in category_map.items()})
        
        # Calculate totals
        # Ensure amount is numeric (Db2 might return Decimal)
        df['amount'] = pd.to_numeric(df['amount'])
        total_spent = df['amount'].sum()
        
        categories_df['planned_amount'] = pd.to_numeric(categories_df['planned_amount'])
        total_planned = categories_df['planned_amount'].sum() if not categories_df.empty else 0
        
        col1, col2 = st.columns(2)
        col1.metric("Total Spent", f"${total_spent:.2f}")
        col2.metric("Total Planned", f"${total_planned:.2f}", delta=f"${total_planned - total_spent:.2f}")
        
        st.subheader("Progress by Category")
        # Group by category
        category_spending = df.groupby('category_name')['amount'].sum().reset_index()
        
        for index, row in categories_df.iterrows():
            cat_name = row['name']
            planned = row['planned_amount']
            spent = category_spending[category_spending['category_name'] == cat_name]['amount'].sum() if not category_spending.empty and cat_name in category_spending['category_name'].values else 0
            
            st.write(f"**{cat_name}** (${spent:.2f} / ${planned:.2f})")
            st.plotly_chart(progress_bar(planned, spent), use_container_width=True, key=f"progress_{cat_name}")
            
        st.subheader("Spending Distribution")
        st.plotly_chart(pie_chart(category_spending.rename(columns={'category_name': 'category'})), use_container_width=True, key="pie_chart")
        
        st.subheader("Daily Spending")
        st.plotly_chart(daily_spending(df), use_container_width=True, key="daily_spending")
        
        # Recent Transactions with delete option
        st.subheader("Recent Transactions")
        
        # Sort by timestamp descending
        df_sorted = df.sort_values('timestamp', ascending=False)
        
        for idx, row in df_sorted.head(20).iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 2, 1])
            with col1:
                st.write(f"**{row['vendor']}**")
            with col2:
                st.write(f"{row['category_name']}")
            with col3:
                st.write(f"${row['amount']:.2f}")
            with col4:
                # Format timestamp
                timestamp_str = str(row['timestamp'])[:10] if pd.notna(row['timestamp']) else "N/A"
                st.write(timestamp_str)
            with col5:
                if st.button("🗑️", key=f"delete_{row['id']}"):
                    try:
                        execute_query(conn, "DELETE FROM transactions WHERE id = ?", (row['id'],))
                        st.success("Deleted!")
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
    else:
        st.info("No transactions found. Add some expenses!")

elif page == "Add Expense":
    st.title("Add Expense")
    
    tab_ai, tab_manual = st.tabs(["AI Input", "Manual Input"])
    
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
                            'notes': notes
                        }
                
                # Save all button
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("Save All", type="primary"):
                        try:
                            saved_count = 0
                            for expense in st.session_state.edited_expenses:
                                category_id = category_map.get(expense['category'])
                                if not category_id:
                                    st.error(f"Invalid category: {expense['category']}")
                                    continue
                                
                                # Debug output
                                st.write(f"DEBUG: Saving - User: {user_id}, Category ID: {category_id}, Amount: {expense['amount']}, Vendor: {expense['vendor']}")
                                
                                result = execute_query(conn, 
                                    "INSERT INTO transactions (user_id, category_id, amount, vendor, notes) VALUES (?, ?, ?, ?, ?)",
                                    (user_id, category_id, expense['amount'], expense['vendor'], expense['notes'])
                                )
                                
                                if result:
                                    saved_count += 1
                                    st.write(f"✓ Saved: {expense['vendor']}")
                                else:
                                    st.error(f"Failed to save expense: {expense['vendor']}")
                            
                            if saved_count > 0:
                                st.success(f"Saved {saved_count} expense(s)!")
                                del st.session_state.ai_result
                                del st.session_state.edited_expenses
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("No expenses were saved. Please check the errors above.")
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
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            vendor = st.text_input("Vendor")
            category = st.selectbox("Category", category_names)
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Save Expense"):
                try:
                    execute_query(conn, 
                        "INSERT INTO transactions (user_id, category_id, amount, vendor, notes) VALUES (?, ?, ?, ?, ?)",
                        (user_id, category_map[category], amount, vendor, notes)
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
    
    # Add sorting option
    sort_by = st.radio("Sort by:", ["Name", "Planned Amount", "ID"], horizontal=True)
    
    if sort_by == "Name":
        categories_df_sorted = categories_df.sort_values('name')
    elif sort_by == "Planned Amount":
        categories_df_sorted = categories_df.sort_values('planned_amount', ascending=False)
    else:
        categories_df_sorted = categories_df.sort_values('id')
    
    # Display categories with edit and delete options
    for idx, row in categories_df_sorted.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.write(f"**{row['name']}**")
        with col2:
            st.write(f"Planned: ${float(row['planned_amount']):.2f}")
        with col3:
            # Edit button (using expander for inline editing)
            if st.button("✏️", key=f"edit_{row['id']}"):
                st.session_state[f"editing_{row['id']}"] = True
        with col4:
            if st.button("🗑️", key=f"delete_cat_{row['id']}"):
                try:
                    # Check if category has transactions
                    transactions = execute_query(conn, "SELECT COUNT(*) as count FROM transactions WHERE category_id = ?", (row['id'],))
                    if transactions and transactions[0].get('count', 0) > 0:
                        st.error(f"Cannot delete '{row['name']}' - it has {transactions[0]['count']} transaction(s). Delete those first.")
                    else:
                        execute_query(conn, "DELETE FROM categories WHERE id = ?", (row['id'],))
                        st.success("Deleted!")
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Inline editing
        if st.session_state.get(f"editing_{row['id']}", False):
            with st.form(f"edit_form_{row['id']}"):
                new_name = st.text_input("Category Name", value=row['name'])
                new_planned = st.number_input("Planned Amount", value=float(row['planned_amount']), min_value=0.0, step=10.0)
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("Save"):
                        try:
                            execute_query(conn,
                                "UPDATE categories SET name = ?, planned_amount = ? WHERE id = ?",
                                (new_name, new_planned, row['id'])
                            )
                            st.success("Updated!")
                            del st.session_state[f"editing_{row['id']}"]
                            st.cache_data.clear()
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                with col_cancel:
                    if st.form_submit_button("Cancel"):
                        del st.session_state[f"editing_{row['id']}"]
                        st.rerun()
    
    st.divider()
    
    st.subheader("Add New Category")
    with st.form("add_category"):
        new_name = st.text_input("Category Name")
        new_planned = st.number_input("Planned Amount", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Add Category"):
            try:
                execute_query(conn,
                    "INSERT INTO categories (name, planned_amount) VALUES (?, ?)",
                    (new_name, new_planned)
                )
                st.success("Category added!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error adding category: {e}")

elif page == "Settings":
    st.title("Settings")
    st.write("Environment Configuration")
    st.code(f"""
DB2_DATABASE = ...
WATSONX_PROJECT_ID = ...
    """)
    
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")
