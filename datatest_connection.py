import pyodbc
import sys

def test_azure_db_connection():
    """Test connection to Azure SQL Database"""
    
    # Database connection parameters
    server = 'breachdataagent.database.windows.net'
    database = 'ProActiveRiskDB'
    username = 'safemap'
    password = 'jBfwulszn846r4'
    driver = 'ODBC Driver 17 for SQL Server'
    
    print("========================================")
    print("Azure SQL Database Connection Test")
    print("========================================")
    print(f"Server: {server}")
    print(f"Database: {database}")
    print(f"Username: {username}")
    print("========================================\n")
    
    # Build connection string
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"PORT=1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    
    try:
        print("Attempting to connect...")
        
        # Attempt connection
        connection = pyodbc.connect(connection_string)
        print("✓ Connection successful!")
        
        # Create cursor
        cursor = connection.cursor()
        print("✓ Cursor created successfully!")
        
        # Test query - get SQL Server version
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print("\n✓ Query executed successfully!")
        print(f"\nSQL Server Version:\n{row[0]}")
        
        # Get database name to confirm we're connected to the right database
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()[0]
        print(f"\n✓ Connected to database: {db_name}")
        
        # Get current user
        cursor.execute("SELECT SUSER_NAME()")
        current_user = cursor.fetchone()[0]
        print(f"✓ Connected as user: {current_user}")
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        table_count = cursor.fetchone()[0]
        print(f"✓ Number of tables in database: {table_count}")
        
        # Close cursor and connection
        cursor.close()
        connection.close()
        print("\n✓ Connection closed successfully!")
        
        print("\n========================================")
        print("CONNECTION TEST PASSED ✓")
        print("========================================")
        
        return True
        
    except pyodbc.Error as e:
        print("\n✗ Connection failed!")
        print(f"\nError details:")
        print(f"Error code: {e.args[0] if e.args else 'Unknown'}")
        print(f"Error message: {e.args[1] if len(e.args) > 1 else str(e)}")
        
        # Common error troubleshooting
        print("\n========================================")
        print("TROUBLESHOOTING TIPS:")
        print("========================================")
        
        if "28000" in str(e):
            print("• Authentication failed - check username/password")
        elif "08001" in str(e):
            print("• Cannot connect to server - check server name and network")
        elif "driver" in str(e).lower():
            print("• ODBC Driver issue - ensure 'ODBC Driver 17 for SQL Server' is installed")
            print("  Install with: ")
            print("  - Windows: Download from Microsoft")
            print("  - Mac: brew install msodbcsql17")
            print("  - Linux: Follow Microsoft's guide for your distribution")
        elif "timeout" in str(e).lower():
            print("• Connection timeout - check firewall rules and network connectivity")
        
        print("\n========================================")
        print("CONNECTION TEST FAILED ✗")
        print("========================================")
        
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print("\n========================================")
        print("CONNECTION TEST FAILED ✗")
        print("========================================")
        return False

def check_driver():
    """Check if ODBC drivers are installed"""
    print("\nChecking installed ODBC drivers...")
    try:
        drivers = [driver for driver in pyodbc.drivers()]
        if drivers:
            print("Installed ODBC drivers:")
            for driver in drivers:
                print(f"  - {driver}")
                
            if "ODBC Driver 17 for SQL Server" in drivers:
                print("\n✓ Required driver 'ODBC Driver 17 for SQL Server' is installed")
                return True
            else:
                print("\n✗ Required driver 'ODBC Driver 17 for SQL Server' is NOT installed")
                return False
        else:
            print("✗ No ODBC drivers found")
            return False
    except Exception as e:
        print(f"✗ Error checking drivers: {e}")
        return False

if __name__ == "__main__":
    # First check if required driver is installed
    driver_ok = check_driver()
    
    if not driver_ok:
        print("\nPlease install ODBC Driver 17 for SQL Server before proceeding.")
        sys.exit(1)
    
    # Test the connection
    print("\n")
    test_azure_db_connection()