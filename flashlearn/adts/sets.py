from dataclasses import dataclass
from typing import List, Optional

from flashlearn.adts.card import Card

@dataclass
class AbstractSet:
    """Class representing a set of flashcards"""
    id: int
    """ID of set in database"""
    title: str
    """Title of set"""

@dataclass
class Set(AbstractSet):
    """Class representing a set of flashcards"""
    id: int
    """ID of set in database"""
    super_id: Optional[int]
    """ID of superset set belongs to"""
    title: str
    """Title of set"""
    cards: List[Card] = []
    """List of cards in set"""

@dataclass
class SuperSet(AbstractSet):
    """Class representing a superset of sets"""
    id: int
    """ID of superset in database"""
    title: str
    """Title of superset"""
    sets: List[int] = []
    """List of sets in superset"""