import ibm_db
from db_client import get_db_connection, execute_query

def init_db():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to Db2.")
        return

    print("Connected to Db2.")
    
    with open("schema.sql", "r") as f:
        sql_script = f.read()

    # Split by semicolon, but be careful about semicolons in strings if any.
    # For this simple schema, splitting by ';' is likely fine.
    statements = sql_script.split(';')
    
    for stmt in statements:
        stmt = stmt.strip()
        if stmt:
            print(f"Executing: {stmt[:50]}...")
            try:
                # ibm_db.exec_immediate(conn, stmt)
                # Using our helper which uses prepare/execute
                # But execute_query expects params for prepare/execute usually.
                # Let's use ibm_db directly for DDL to be safe or just use execute_query without params
                
                # Note: execute_query in db_client.py uses ibm_db.prepare + execute.
                # This should work for DDL too.
                
                # However, our execute_query returns True/False/Result.
                result = execute_query(conn, stmt)
                if result is False:
                    print(f"Failed to execute: {stmt}")
                    # Print error details if possible (db_client prints them)
                else:
                    print("Success.")
            except Exception as e:
                print(f"Error: {e}")

    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
