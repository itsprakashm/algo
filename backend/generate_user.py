#!/usr/bin/env python3
"""
Script to generate SQL query for adding a new user with properly hashed password
"""

from werkzeug.security import generate_password_hash
from datetime import datetime

def generate_user_sql(username, password, email=None, is_admin=False):
    """Generate SQL query to insert a new user with properly hashed password"""
    
    # Generate password hash
    password_hash = generate_password_hash(password)
    
    # Generate email if not provided
    if not email:
        email = f"{username}@algo-trading.com"
    
    # Create SQL query
    sql_query = f"""
INSERT INTO users (username, password_hash, email, is_active, is_admin, created_at) 
VALUES (
    '{username}', 
    '{password_hash}', 
    '{email}', 
    TRUE, 
    {str(is_admin).upper()}, 
    NOW()
);
"""
    
    return sql_query

if __name__ == "__main__":
    # Generate SQL for the requested user
    username = "prakash"
    password = "prakash@123"
    
    sql = generate_user_sql(username, password)
    
    print("SQL Query to add user 'prakash':")
    print("=" * 50)
    print(sql)
    print("=" * 50)
    print("\nTo execute this query:")
    print("1. Connect to your MySQL database")
    print("2. Use the database: USE algo_trading;")
    print("3. Run the above SQL query")
    print("\nOr you can run this script directly to get the query.") 