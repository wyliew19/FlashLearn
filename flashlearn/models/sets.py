from typing import Optional

from flashlearn.models.card import Card

class AbstractSet:
    def __init__(self, id: int, title: str):
        self.id = id
        self.title = title

class Set(AbstractSet):
    def __init__(self, id: int, title: str, cards: list[Card]):
        super().__init__(id, title)
        self.cards = cards

class SuperSet(AbstractSet):
    def __init__(self, id: int, title: str, sets: list[Set]):
        super().__init__(id, title)
        self.sets = sets