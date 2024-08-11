from typing import Optional

from flashlearn.utils.database import DatabaseManager
from flashlearn.adts.sets import Set, SuperSet

class SetHandler:
    def __init__(self):
        self._db = DatabaseManager()

    def create_set(self, name: str, email: str, super_id: Optional[int]):
        print(f"DEBUG::Set Handler::create_set({name}, {email}, {super_id})")
        # Get user ID
        user_id = self._db.select_from_table("USER", email=email)[0]
        # Insert set into database
        if super_id is None:
            self._db.insert_into_table("SET", title=name, user_id=user_id)
        else:
            self._db.insert_into_table("SET", title=name, user_id=user_id, super_id=super_id)
        info = self._db.select_from_table("SET", title=name, user_id=user_id)
        if not info:
            return None
        return Set(info[0], info[1], [])
    
    def create_super_set(self, name: str, email: str):
        print(f"DEBUG::Set Handler::create_super_set({name}, {email})")
        # Get user ID
        user_id = self._db.select_from_table("USER", email=email)[0]
        # Insert set into database
        self._db.insert_into_table("SUPERSET", title=name, user_id=user_id)
        info = self._db.select_from_table("SUPERSET", title=name, user_id=user_id)
        if not info:
            return None
        return info[0]
    
    def _retrieve_set(self, table, set_title: str, email: str):
        info = self._db.select_from_table(table, title=set_title, user_id=self._db.select_from_table("USER", email=email)[0])
        if not info:
            return None
        return info[0]   
    
    def get_set(self, set_title: str, email: str):
        return self._retrieve_set("SET", set_title, email)
    
    def get_super_set(self, super_title: str, email: str):
        return self._retrieve_set("SUPERSET", super_title, email)
    
    def get_all_sets(self, email: str):
        user_id = self._db.select_from_table("USER", email=email)[0]
        info = self._db.select_from_table("SET", user_id=user_id)
        if not info:
            return None
        return info
    

    
