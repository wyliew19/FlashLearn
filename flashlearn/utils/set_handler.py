from typing import Optional

from flashlearn.utils.database import DatabaseManager
from flashlearn.adts.card import Card
from flashlearn.adts.sets import AbstractSet, Set, SuperSet

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
        # Return set object if found
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
        # Return set object if found
        info = self._db.select_from_table("SUPERSET", title=name, user_id=user_id)
        if not info:
            return None
        return SuperSet(info[0], info[1], [])
    
    def _populate_set(self, set_id: int):
        # Get cards given set
        cards = self._db.select_from_table("FLASHCARD", set_id=set_id)
        # Populate array with card objects
        return [Card(*info) for info in cards]
    
    def _populate_super_set(self, super_id: int):
        # Get sets given super set
        sets = self._db.select_from_table("SET", "id", "title", super_id=super_id)
        # Populate sets with cards before returning
        return [Set(*info, cards=self._populate_set(info[0])) for info in sets]

    def get_set(self, set_id: int) -> Set:
        # Get set info
        info = self._db.select_from_table("SET", id=set_id)
        # Return set object
        return Set(info[0], info[1], cards=self._populate_set(set_id))
    
    def get_super_set(self, super_id: int) -> SuperSet:
        # Get super set info
        info = self._db.select_from_table("SUPERSET", id=super_id)
        # Return super set object
        return SuperSet(info[0], info[1], sets=self._populate_super_set(super_id))
    
    def get_user_sets(self, email: str) -> list[AbstractSet]:
        # Get user ID
        user_id = self._db.select_from_table("USER", email=email)[0]
        # Get sets and super sets
        sets = self._db.select_from_table("SET", user_id=user_id)
        super_sets = self._db.select_from_table("SUPERSET", user_id=user_id)
        # Return list of sets and super sets
        return ([Set(info[0], info[1], cards=self._populate_set(info[0])) for info in sets] 
                +
                [SuperSet(info[0], info[1], sets=self._populate_super_set(info[0])) for info in super_sets])
    
    def get_subsets(self, super_id: int) -> list[Set]:
        # Get sets given super set
        sets = self._db.select_from_table("SET", super_id=super_id)
        # Populate sets with cards before returning
        return [Set(info[0], info[1], cards=self._populate_set(info[0])) for info in sets]
    
    def edit_set(self, set_id: int, email: str, new_title: str):
        # Update set title
        self._db.update_table("SET", {"title": new_title}, id=set_id)
        # Return updated set object if found
        info = self._db.select_from_table("SET", id=set_id)
        if not info:
            return None
        return Set(info[0], info[1], self._populate_set(set_id))

    def delete_set(self, set_id: int):
        # Delete set from database
        self._db.delete_from_table("SET", set_id)
        # Return True if set is deleted
        info = self._db.select_from_table("SET", id=set_id)
        if not info:
            return True
        return False

    def add_card_to_set(self, set_id: int, email: str, term: str, body: str):
        # Get user ID
        user_id = self._db.select_from_table("USER", email=email)[0]
        # Insert card into database
        self._db.insert_into_table("FLASHCARD", term=term, body=body, user_id=user_id, set_id=set_id)
        # Return card object if found
        info = self._db.select_from_table("FLASHCARD", term=term, body=body, user_id=user_id, set_id=set_id)
        if not info:
            return None
        return info