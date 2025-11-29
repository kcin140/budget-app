import ibm_db
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """
    Establishes a connection to the IBM Db2 database.
    """
    # Try to get from Streamlit secrets first (for deployment)
    try:
        import streamlit as st
        database = st.secrets.get("DB2_DATABASE")
        hostname = st.secrets.get("DB2_HOSTNAME")
        port = st.secrets.get("DB2_PORT")
        uid = st.secrets.get("DB2_UID")
        pwd = st.secrets.get("DB2_PWD")
        security = st.secrets.get("DB2_SECURITY", "SSL")
    except:
        # Fall back to environment variables (for local development)
        database = os.environ.get("DB2_DATABASE")
        hostname = os.environ.get("DB2_HOSTNAME")
        port = os.environ.get("DB2_PORT")
        uid = os.environ.get("DB2_UID")
        pwd = os.environ.get("DB2_PWD")
        security = os.environ.get("DB2_SECURITY", "SSL")

    if not all([database, hostname, port, uid, pwd]):
        return None

    # Create SSL certificate file if it doesn't exist
    cert_path = "db2_ssl_cert.pem"
    if not os.path.exists(cert_path):
        cert_content = """-----BEGIN CERTIFICATE-----
MIIDEjCCAfqgAwIBAgIJAP5KDwe3BNLbMA0GCSqGSIb3DQEBCwUAMB4xHDAaBgNV
BAMME0lCTSBDbG91ZCBEYXRhYmFzZXMwHhcNMjAwMjI5MDQyMTAyWhcNMzAwMjI2
MDQyMTAyWjAeMRwwGgYDVQQDDBNJQk0gQ2xvdWQgRGF0YWJhc2VzMIIBIjANBgkq
hkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuu/n+iYoqvGF5O1HjDjZl+nbb18RDxdl
O4T/qhPc114DcQT+JeEwatmwhicLlZBqvAaLoXknhjIQN0m5/Lyc7AcouUsfHdtC
CTg+IK1n0kt3+Ls7wWSjLjTOz7s72VTINrblwrtHEIo3RVNEzJCGanKIwY1fUIKk
WM2TtH9yrqlHctgjHRQfFESFiXhrb88RBgtjb/kLmTjBi1AxEZuchmfvATf4CNcq
cmPpsjt0ONr4bxI1TrQlDzcb7XLHPkYouIJkvus1Foi12JdM3S++yZlVO1FffE7o
J28TtbhgrF8kHSCLJBoM1RgqOdoNVnP8/D9fajcM7IVwexkIR93JGQIDAQABo1Mw
UTAdBgNVHQ4EFgQUeCrYjqIC75UJqVfD08uegjx6bRcwHwYDVR0jBBgwFoAUeCrY
jqIC75UJqVfD08uegjx6bRcwDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsF
AAOCAQEAI2E0T9Kw2SwF2v1pjhux3IdYevHaUJDLoKOwHRFqR8x1ggQpeDpPg2NR
LwGO2zO9IfT2hKiguwj+ZryHlqpyqCJK8rDSo1eEOzB2Za6KV+A5lpKm1gcWuGc3
+U+U1sL7eR7wdQnV54MU8hDo6/lTtLEPv2w7VSOJQC+Mwz8+LRLv5GInA6RrIca+
33L16pxdKmwZKa8Vrpg1rwC4gcweaHX1CDXN6+BHo8oXnXZHzPourWXKPhhgWgby
CCqGH+CV6t5xX7oNMKuMICjEVgvsKZtjy49Unb5VYlt4oRwu1elgsD3czImn9KDD
4puDAoa6r2KYdN1VLn7qwTmSl9SSNQ==
-----END CERTIFICATE-----
"""
        with open(cert_path, 'w') as f:
            f.write(cert_content)

    conn_str = (
        f"DATABASE={database};"
        f"HOSTNAME={hostname};"
        f"PORT={port};"
        f"PROTOCOL=TCPIP;"
        f"UID={uid};"
        f"PWD={pwd};"
        f"SECURITY={security};"
        f"SSLServerCertificate=db2_ssl_cert.pem;"
    )

    try:
        conn = ibm_db.connect(conn_str, "", "")
        return conn
    except Exception as e:
        print(f"Error connecting to Db2: {e}")
        return None

def execute_query(conn, sql, params=None):
    """
    Executes a SQL query.
    If it's a SELECT statement, returns a list of dictionaries.
    If it's an INSERT/UPDATE/DELETE, returns True on success.
    """
    if not conn:
        return None

    try:
        stmt = ibm_db.prepare(conn, sql)
        if params:
            # ibm_db expects a tuple for params
            ibm_db.execute(stmt, tuple(params))
        else:
            ibm_db.execute(stmt)

        # Check if it's a SELECT query
        if sql.strip().upper().startswith("SELECT"):
            result = []
            dictionary = ibm_db.fetch_assoc(stmt)
            while dictionary:
                # Normalize keys to lowercase
                clean_dict = {k.lower(): v for k, v in dictionary.items()}
                result.append(clean_dict)
                dictionary = ibm_db.fetch_assoc(stmt)
            return result
        else:
            return True
    except Exception as e:
        error_msg = f"Error executing query: {e}"
        if hasattr(ibm_db, 'stmt_errormsg'):
            try:
                error_msg += f"\nDB2 Error: {ibm_db.stmt_errormsg()}"
            except:
                pass
        print(error_msg)
        raise Exception(error_msg)
    finally:
        # We don't close the connection here to allow reuse, 
        # but in a real app we might want to manage this better.
        pass
