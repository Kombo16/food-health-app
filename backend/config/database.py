""" Database configuration and connection management """
import mysql.connector
from mysql.connector import Error
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL database configuration
DB_CONFIG = {
    'host' : os.getenv('DB_HOST', 'localhost'),
    'database' : os.getenv('DB_NAME', 'food_doctor'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', 3306),
    'auth_plugin': 'caching_sha2_password',  # Use caching_sha2_password for MySQL 8.0+
    'raise_on_warnings': True,
}

def get_db_connection(use_database: bool = True) -> Optional[mysql.connector.connection.MySQLConnection]:
    """Establish a connection to the MySQL database. """
    try:
        if use_database:
            config = DB_CONFIG
        else:
            config = DB_CONFIG.copy()
            config.pop('database', None)  # Remove database if not needed
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None