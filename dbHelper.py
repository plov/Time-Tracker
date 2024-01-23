import sqlite3
from sqlite3 import Error

class dbHelper:

    def __init__(self, dbPath):
        self.path = dbPath
        
    def execute_query(self, query, data=None):
        try:
            with sqlite3.connect(self.path, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute(query, data)
                rows_affected = cursor.rowcount
                conn.commit()
                if(rows_affected > 0):
                    return rows_affected
                return cursor.fetchall()
        except Error as e:
            raise e

    def execute(self, query, data):
        return self.execute_query(query, data)

        