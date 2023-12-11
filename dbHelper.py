import sqlite3
from sqlite3 import Error

class dbHelper:

    def __init__(self, dbPath):
        self.path = dbPath

    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path, timeout=10)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection
    
    def execute_query(self, connection, query, data):
        cursor = connection.cursor()
        try:
            cursor.execute(query, data)
            connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_read_query(self, connection, query):
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")

    def execute(self, query):
        connection = self.create_connection(self.path)
        result = self.execute_read_query(connection, query)
        if result == None :
            return {}
        else :
            return result
        
    def executePush(self, query, data):
        connection = self.create_connection(self.path)
        result = self.execute_query(connection, query, data)
        if result == None :
            return {}
        else :
            return result

        