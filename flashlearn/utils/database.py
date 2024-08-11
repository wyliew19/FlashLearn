import sqlite3
import threading

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

    def execute_query(self, query: str, params: Optional[str]) -> list:
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
                email TEXT PRIMARY KEY,
                password TEXT,
                name TEXT
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS SUPERSET (
                id INTEGER PRIMARY KEY,
                name TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES USER (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS SET (
                id INTEGER PRIMARY KEY,
                name TEXT,
                user_id INTEGER,
                super_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES USER (id)
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
                FOREIGN KEY (user_id) REFERENCES USER (id),
                FOREIGN KEY (set_id) REFERENCES SET (id)
            )
            '''
        ]

        for query in tables:
            self.execute_query(query)

    def close_connection(self):
        self.connection.close()

    def insert_into_table(self, table_name: str, **kwargs) -> None:
        columns = ', '.join(str(x) for x in kwargs.keys())
        placeholders = ', '.join('?' * len(kwargs))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(kwargs.values()))

    def select_from_table(self, table_name, *columns, **kwargs) -> list:
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
            conditions = ' AND '.join(f"{key} = ?" for key in kwargs.keys())
            query += f" WHERE {conditions}"
            return self.execute_query(query, tuple(kwargs.values()))
        else:
            return self.execute_query(query)
        
    def union_select(self, table1: str, table2: str, *columns, **kwargs) -> list:
        '''
        Sample usage:
          ```cards = union_select("SET", "SUPERSET", "title", user_id=1)```
        this will return all titles of the rows in the SET and SUPERSET tables where user_id is 1'''
        query = f"SELECT {', '.join(columns)} FROM {table1} UNION SELECT {', '.join(columns)} FROM {table2}"
        if kwargs:
            conditions = ' AND '.join(f"{key} = ?" for key in kwargs.keys())
            query += f" WHERE {conditions}"
            return self.execute_query(query, tuple(kwargs.values()))
        else:
            return self.execute_query(query)
        
    def update_table(self, table_name: str, set_dict: dict, where_dict: dict) -> list:
        """set_dict = {'column_name': 'new_value'}
           where_dict = {'column_name': 'value'}"""
        set_columns = ', '.join(f"{key} = ?" for key in set_dict.keys())
        where_columns = ' AND '.join(f"{key} = ?" for key in where_dict.keys())
        query = f"UPDATE {table_name} SET {set_columns} WHERE {where_columns}"
        return self.execute_query(query, tuple(set_dict.values()) + tuple(where_dict.values()))
    
    def remove_from_table(self, table_name: str, **kwargs) -> list:
        query = f"DELETE FROM {table_name} WHERE {list(kwargs.keys())[0]} = ?"
        return self.execute_query(query, tuple(kwargs.values()))
