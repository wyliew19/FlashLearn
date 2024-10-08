import sqlite3
import threading
from typing import Optional

from typing import Optional

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = sqlite3.connect('database.db', check_same_thread=False)
            cls._instance.lock = threading.Lock()  # Initialize lock
        return cls._instance
    
    def __init__(self):
        self.create_tables()


    def execute_query(self, query: str, params: Optional[list] = None) -> list[tuple]:
        with self.lock:  # Acquire lock
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            print(f"Executed query:\n{query}\n")
            print(f"Params:\n{params}\n")
            return cursor.fetchall()

    def create_tables(self):
        tables = [
            '''
            CREATE TABLE IF NOT EXISTS USER (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                password TEXT,
                name TEXT
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS SUPERSET (
                id INTEGER PRIMARY KEY,
                title TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES USER (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS SUBSET (
                id INTEGER PRIMARY KEY,
                title TEXT,
                user_id INTEGER,
                super_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES USER (id),
                FOREIGN KEY (super_id) REFERENCES SUPERSET (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS FLASHCARD (
                id INTEGER PRIMARY KEY,
                term TEXT,
                body TEXT,
                user_id INTEGER,
                set_id INTEGER,
                studied BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES USER (id),
                FOREIGN KEY (set_id) REFERENCES SUBSET (id)
            )
            '''
        ]

        for query in tables:
            self.execute_query(query)

    def close_connection(self):
        self.connection.close()

    def insert_into_table(self, table_name: str, **kwargs) -> None:
        print(f"DEBUG::DatabaseManager::insert_into_table({table_name}, {kwargs})")
        columns = ', '.join(str(x) for x in kwargs.keys())
        placeholders = ', '.join('?' * len(kwargs))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, list(kwargs.values()))

    def select_from_table(self, table_name, *columns, **kwargs) -> list[tuple]:
        '''
        Sample usage: 
          ```cards = select_from_table("FLASHCARD", "term", "body", user_id=1)```
        this will return all terms and bodies of the rows in the FLASHCARD table where user_id is 1
        '''
        if columns:
            query = f"SELECT {', '.join(columns)} FROM {table_name}"
        else:
            query = f"SELECT * FROM {table_name}"
        if kwargs:
            conditions = ' AND '.join(f"{key} IS ?" for key in kwargs.keys())
            query += f" WHERE {conditions}"
            return self.execute_query(query, list(kwargs.values()))
        else:
            return self.execute_query(query)
        
    def update_table(self, table_name: str, new_vals: dict, **kwargs):
        '''
        Sample usage:
          ```update_table("FLASHCARD", {"term": "new term"}, id=1)```
        this will update the term of the row in the FLASHCARD table where the flashcard's id is 1'''
        for key, value in new_vals.items():
            query = f"UPDATE {table_name} SET {key} = ? WHERE {list(kwargs.keys())[0]} = ?"
            self.execute_query(query, (value, list(kwargs.values())[0]))
            
    
    def remove_from_table(self, table_name: str, **kwargs) -> list[tuple]:
        query = f"DELETE FROM {table_name} WHERE {list(kwargs.keys())[0]} = ?"
        return self.execute_query(query, list(kwargs.values()))
