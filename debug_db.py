import sys
sys.path.insert(0, '/Users/nickkyburz/Desktop/budget-app')

from db_client import get_db_connection, execute_query

conn = get_db_connection()
if conn:
    print("Connected to Db2")
    
    print("\n=== All Transactions ===")
    transactions = execute_query(conn, "SELECT * FROM transactions")
    if transactions:
        for t in transactions:
            print(f"ID: {t.get('id')}, User: {t.get('user_id')}, Amount: {t.get('amount')}, Vendor: {t.get('vendor')}")
    else:
        print("No transactions found")
    
    print("\n=== Expected User ID ===")
    print("default-user-001")
    
    print("\n=== Categories ===")
    categories = execute_query(conn, "SELECT * FROM categories")
    if categories:
        for c in categories:
            print(f"ID: {c.get('id')}, Name: {c.get('name')}")
else:
    print("Failed to connect")
