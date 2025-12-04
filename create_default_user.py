from db_client import get_db_connection, execute_query

conn = get_db_connection()
if conn:
    print("Connected to Db2")
    
    # Check if default user exists
    users = execute_query(conn, "SELECT * FROM users WHERE id = ?", ("default-user-001",))
    
    if users:
        print("Default user already exists")
    else:
        print("Creating default user...")
        try:
            execute_query(conn, 
                "INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)",
                ("default-user-001", "default@budgetapp.local", "no-password-needed")
            )
            print("✓ Default user created successfully!")
        except Exception as e:
            print(f"Error creating user: {e}")
    
    # Verify
    users = execute_query(conn, "SELECT * FROM users")
    print(f"\nAll users in database:")
    for u in users:
        print(f"  - ID: {u.get('id')}, Email: {u.get('email')}")
else:
    print("Failed to connect")
