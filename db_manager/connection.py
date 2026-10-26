import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def connect(self, host, user, password, database):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                return True
            return False
        except Error as e:
            print(f"Error: {e}")
            self.connection = None
            return False

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()