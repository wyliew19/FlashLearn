from typing import Optional

from flashlearn.utils.database import DatabaseManager
from flashlearn.models.card import Card
from flashlearn.models.sets import AbstractSet, Set, SuperSet

class SetHandler:
    def __init__(self):
        self._db = DatabaseManager()

    def create_set(self, name: str, email: str, super_id: Optional[int]):
        print(f"DEBUG::Set Handler::create_set(\"{name}\", {email}, {super_id})")
        # Get user ID
        user_id = self._db.select_from_table("USER", email=email)[0]
        # Insert set into database
        if super_id is None:
            self._db.insert_into_table("SUBSET", title=name, user_id=user_id)
        else:
            self._db.insert_into_table("SUBSET", title=name, user_id=user_id, super_id=super_id)
        # Return set object if found
        info = self._db.select_from_table("SUBSET", title=name, user_id=user_id)
        if not info:
            return None
        return Set(info[0], info[1], [])
    
    def create_super_set(self, name: str, user_id: int):
        print(f"DEBUG::Set Handler::create_super_set(\"{name}\", {user_id})")
        # Insert set into database
        self._db.insert_into_table("SUPERSET", title=name, user_id=user_id)
        # Return set object if found
        info = self._db.select_from_table("SUPERSET", title=name, user_id=user_id)
        if not info:
            return None
        return SuperSet(info[0], info[1], [])
    
    def _populate_set(self, set_id: int):
        print(f"DEBUG::Set Handler::_populate_set({set_id})")
        # Get cards given set
        cards = self._db.select_from_table("FLASHCARD", set_id=set_id)
        # Populate array with card objects
        return [Card(*info) for info in cards]
    
    def _populate_super_set(self, super_id: int):
        print(f"DEBUG::Set Handler::_populate_super_set({super_id})")
        # Get sets given super set
        sets = self._db.select_from_table("SUBSET", "id", "title", super_id=super_id)
        # Populate sets with cards before returning
        return [Set(*info, self._populate_set(info[0])) for info in sets]

    def get_set(self, set_id: int) -> Set:
        print(f"DEBUG::Set Handler::get_set({set_id})")
        # Get set info
        info = self._db.select_from_table("SUBSET", id=set_id)
        # Return set object
        return Set(info[0], info[1], self._populate_set(set_id))
    
    def get_super_set(self, super_id: int) -> SuperSet:
        print(f"DEBUG::Set Handler::get_super_set({super_id})")
        # Get super set info
        info = self._db.select_from_table("SUPERSET", id=super_id)
        # Return super set object
        return SuperSet(info[0], info[1], self._populate_super_set(super_id))
    
    def get_user_sets(self, user_id: int) -> list[AbstractSet]:
        print(f"DEBUG::Set Handler::get_user_sets({user_id})")
        # Get sets and super sets
        sets = self._db.select_from_table("SUBSET", user_id=user_id)
        super_sets = self._db.select_from_table("SUPERSET", user_id=user_id)
        # Return list of sets and super sets
        return ([Set(info[0], info[1], self._populate_set(info[0])) for info in sets] 
                +
                [SuperSet(info[0], info[1], self._populate_super_set(info[0])) for info in super_sets])
    
    def get_subsets(self, super_id: int) -> list[Set]:
        print(f"DEBUG::Set Handler::get_subsets({super_id})")
        # Get sets given super set
        sets = self._db.select_from_table("SUBSET", super_id=super_id)
        # Populate sets with cards before returning
        return [Set(info[0], info[1], self._populate_set(info[0])) for info in sets]
    
    def edit_set(self, set_id: int, new_title: str):
        print(f"DEBUG::Set Handler::edit_set({set_id}, \"{new_title}\")")
        # Update set title
        self._db.update_table("SUBSET", {"title": new_title}, id=set_id)
        # Return updated set object if found
        info = self._db.select_from_table("SUBSET", id=set_id)
        if not info:
            return None
        return Set(info[0], info[1], self._populate_set(set_id))

    def delete_set(self, set_id: int):
        print(f"DEBUG::Set Handler::delete_set({set_id})")
        # Delete set from database
        self._db.delete_from_table("SUBSET", set_id)
        # Return True if set is deleted
        info = self._db.select_from_table("SUBSET", id=set_id)
        if not info:
            return True
        return False

    def add_card_to_set(self, set_id: int, user_id: int, term: str, body: str):
        print(f"DEBUG::Set Handler::add_card_to_set({set_id}, {user_id}, \"{term}\", \"{body}\")")
        # Insert card into database
        self._db.insert_into_table("FLASHCARD", term=term, body=body, user_id=user_id, set_id=set_id)
        # Return card object if found
        info = self._db.select_from_table("FLASHCARD", term=term, body=body, user_id=user_id, set_id=set_id)
        if not info:
            return None
        return info

    def get_card(self, card_id: int) -> Card:
        print(f"DEBUG::Set Handler::get_card({card_id})")
        # Get card info
        info = self._db.select_from_table("FLASHCARD", id=card_id)
        # Return card object
        return Card(*info)
    
    def edit_card(self, card_id: int, new_term: Optional[str], new_body: Optional[str]):
        print(f"DEBUG::Set Handler::edit_card({card_id}, \"{new_term}\", \"{new_body}\")")
        if not new_term and not new_body:
            return None
        new_vals = {}
        if new_term:
            new_vals["term"] = new_term
        if new_body:
            new_vals["body"] = new_body
        # Update card term and body
        self._db.update_table("FLASHCARD", new_vals, id=card_id)
        # Return updated card object if found
        info = self._db.select_from_table("FLASHCARD", id=card_id)
        if not info:
            return None
        return info
    
    def delete_card(self, card_id: int):
        print(f"DEBUG::Set Handler::delete_card({card_id})")
        # Delete card from database
        self._db.delete_from_table("FLASHCARD", card_id)
        # Return True if card is deleted
        info = self._db.select_from_table("FLASHCARD", id=card_id)
        if not info:
            return True
        return False

    def study_card(self, card_id: int):
        print(f"DEBUG::Set Handler::study_card({card_id})")
        # Update card to studied
        self._db.update_table("FLASHCARD", {"studied": True}, id=card_id)
        # Return updated card object if found
        info = self._db.select_from_table("FLASHCARD", id=card_id)
        if not info:
            return None
        return info
    
    def get_unstudied_cards(self, card_id: int) -> list[Card]:
        print(f"DEBUG::Set Handler::get_unstudied_cards({card_id})")
        # Get card info
        info = self._db.select_from_table("FLASHCARD", id=card_id)
        card = Card(*info)
        # Get unstudied cards
        cards = self._db.select_from_table("FLASHCARD", set_id=card.set_id, studied=False)
        return [Card(*info) for info in cards]
