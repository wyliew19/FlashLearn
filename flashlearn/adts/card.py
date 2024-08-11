from dataclasses import dataclass

@dataclass
class Card:
    """Class representing a flashcard"""
    id: int
    """ID of card in database"""
    term: str
    """Question on card"""
    body: str
    """Answer on card"""
    set_id: int
    """ID of set card belongs to"""
    user_id: int
    """ID of user who created card"""