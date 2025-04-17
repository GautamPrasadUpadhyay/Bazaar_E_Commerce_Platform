import mysql.connector
from mysql.connector import Error

# Use the same configuration as in app.py
db_config = {
    'host': 'localhost',
    'user': 'root',  # Change to your MySQL username
    'password': 'Gautam5@1$',  # Change to your MySQL password
    'database': 'bazaar_db'
}

def test_connection():
    try:
        # Try to connect to the database
        print("Attempting to connect to MySQL database...")
        conn = mysql.connector.connect(**db_config)
        
        if conn.is_connected():
            print("Successfully connected to MySQL database!")
            
            # Get database info
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            database = cursor.fetchone()
            print(f"Connected to database: {database[0]}")
            
            # Check if users table exists
            cursor.execute("SHOW TABLES LIKE 'users'")
            if cursor.fetchone():
                print("\nUsers table exists!")
                
                # Count total users
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"Total users in database: {user_count}")
                
                # Display all users
                if user_count > 0:
                    print("\nUser details:")
                    cursor.execute("SELECT id, username, email FROM users")
                    users = cursor.fetchall()
                    for user in users:
                        print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
                else:
                    print("\nNo users found in the database")
            else:
                print("\nUsers table does not exist!")
            
            cursor.close()
            conn.close()
            print("\nConnection closed successfully!")
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")

if __name__ == "__main__":
    test_connection() 