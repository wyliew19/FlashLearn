import sqlite3
import threading

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

    def execute_query(self, query, params=None) -> list:
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
                email TEXT PRIMARY KEY,
                password TEXT,
                name TEXT
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS FLASHCARD (
                id INTEGER PRIMARY KEY,
                text TEXT,
                image_url TEXT,
                user_id INTEGER,
                set_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES USER (id),
                FOREIGN KEY (set_id) REFERENCES SET (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS SET (
                id INTEGER PRIMARY KEY,
                name TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES USER (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS STUDY_SESSION (
                id INTEGER PRIMARY KEY,
                start_time DATETIME,
                end_time DATETIME,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES USER (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS SESSION_FLASHCARD (
                session_id INTEGER,
                flashcard_id INTEGER,
                correct INTEGER,
                FOREIGN KEY (session_id) REFERENCES STUDY_SESSION (id),
                FOREIGN KEY (flashcard_id) REFERENCES FLASHCARD (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS SHARED_SET (
                set_id INTEGER,
                receiver_email TEXT,
                FOREIGN KEY (set_id) REFERENCES SET (id)
            )
            '''
        ]

        for query in tables:
            self.execute_query(query)

    def close_connection(self):
        self.connection.close()

    def insert_into_table(self, table_name, **kwargs) -> list:
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' * len(kwargs))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_query(query, tuple(kwargs.values()))

    def select_from_table(self, table_name, *columns) -> list:
        if columns:
            query = f"SELECT {', '.join(columns)} FROM {table_name}"
        else:
            query = f"SELECT * FROM {table_name}"
        return self.execute_query(query)
    
    def remove_from_table(self, table_name, **kwargs) -> list:
        query = f"DELETE FROM {table_name} WHERE {list(kwargs.keys())[0]} = ?"
        return self.execute_query(query, tuple(kwargs.values()))
