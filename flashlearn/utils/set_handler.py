from typing import Optional
import random

from flashlearn.utils.database import DatabaseManager
from flashlearn.models.card import Card
from flashlearn.models.sets import AbstractSet, Set, SuperSet

class SetHandler:
    def __init__(self):
        self._db = DatabaseManager()

    def create_set(self, name: str, user_id: int, super_id: Optional[int] = None) -> Set:
        print(f"DEBUG::Set Handler::create_set(\"{name}\", {user_id}, {super_id})")
        # Insert set into database
        if super_id is None:
            self._db.insert_into_table("SUBSET", title=name, user_id=user_id)
        else:
            self._db.insert_into_table("SUBSET", title=name, user_id=user_id, super_id=super_id)
        # Return set object if found
        info = self._db.select_from_table("SUBSET", title=name, user_id=user_id)
        if not info:
            return None
        info = info[0]
        return Set(info[0], info[1], [])
    
    def create_super_set(self, name: str, user_id: int):
        print(f"DEBUG::Set Handler::create_super_set(\"{name}\", {user_id})")
        # Insert set into database
        self._db.insert_into_table("SUPERSET", title=name, user_id=user_id)
        # Return set object if found
        info = self._db.select_from_table("SUPERSET", title=name, user_id=user_id)
        if not info:
            return None
        info = info[0]
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
        info = info[0]
        return Set(info[0], info[1], self._populate_set(set_id))
    
    def get_super_set(self, super_id: int) -> SuperSet:
        print(f"DEBUG::Set Handler::get_super_set({super_id})")
        # Get super set info
        info = self._db.select_from_table("SUPERSET", id=super_id)
        # Return super set object
        info = info[0]
        return SuperSet(info[0], info[1], self._populate_super_set(super_id))
    
    def get_user_sets(self, user_id: int) -> list[AbstractSet]:
        print(f"DEBUG::Set Handler::get_user_sets({user_id})")
        # Get sets and super sets
        sets = self._db.select_from_table("SUBSET", user_id=user_id, super_id=None)
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
        info = info[0]
        return Set(info[0], info[1], self._populate_set(set_id))
    
    def edit_super_set(self, super_id: int, new_title: str):
        print(f"DEBUG::Set Handler::edit_super_set({super_id}, \"{new_title}\")")
        # Update super set title
        self._db.update_table("SUPERSET", {"title": new_title}, id=super_id)
        # Return updated super set object if found
        info = self._db.select_from_table("SUPERSET", id=super_id)
        if not info:
            return None
        info = info[0]
        return SuperSet(info[0], info[1], self._populate_super_set(super_id))

    def delete_set(self, set_id: int):
        print(f"DEBUG::Set Handler::delete_set({set_id})")
        # Delete set from database
        self._db.remove_from_table("SUBSET", id=set_id)
        # Return True if set is deleted
        info = self._db.select_from_table("SUBSET", id=set_id)
        if not info:
            return True
        return False
    
    def delete_super_set(self, super_id: int):
        print(f"DEBUG::Set Handler::delete_super_set({super_id})")
        # Delete super set from database
        self._db.remove_from_table("SUPERSET", id=super_id)
        self._db.remove_from_table("SUBSET", super_id=super_id)
        info = self._db.select_from_table("SUPERSET", id=super_id)
        if not info:
            return True
        return False

    def add_card_to_set(self, set_id: int, user_id: int, term: str, body: str) -> Card:
        print(f"DEBUG::Set Handler::add_card_to_set({set_id}, {user_id}, \"{term}\", \"{body}\")")
        # Insert card into database
        self._db.insert_into_table("FLASHCARD", term=term, body=body, user_id=user_id, set_id=set_id)
        # Return card object if found
        info = self._db.select_from_table("FLASHCARD", term=term, body=body, user_id=user_id, set_id=set_id)
        if not info:
            return None
        info = info[0]
        return Card(*info)

    def get_card(self, card_id: int) -> Card:
        print(f"DEBUG::Set Handler::get_card({card_id})")
        # Get card info
        info = self._db.select_from_table("FLASHCARD", id=card_id)
        # Return card object
        if not info:
            return None
        info = info[0]
        return Card(*info)
    
    def edit_card(self, card_id: int, new_term: Optional[str], new_body: Optional[str]) -> Card:
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
        info = info[0]
        return Card(*info)
    
    def delete_card(self, card_id: int):
        print(f"DEBUG::Set Handler::delete_card({card_id})")
        # Delete card from database
        self._db.remove_from_table("FLASHCARD", id=card_id)
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
        info = info[0]
        return Card(*info)
    
    def _get_unstudied_cards(self, set_id: int) -> list[Card]:
        print(f"DEBUG::Set Handler::get_unstudied_cards({set_id})")
        # Get unstudied cards
        cards = self._db.select_from_table("FLASHCARD", set_id=set_id, studied=False)
        return [Card(*info) for info in cards]

    def get_next_unstudied_card(self, card_id: int | None = None, set_id: int | None = None) -> Card:
        print(f"DEBUG::Set Handler::get_next_unstudied_card({card_id}, {set_id})")
        # Get unstudied cards
        if set_id:
            cards = self._get_unstudied_cards(set_id)
        else:
            cards = self._get_unstudied_cards(self.get_card(card_id).set_id)
        # Return random card
        return random.choice(cards)