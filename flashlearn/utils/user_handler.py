from flashlearn.utils.database import DatabaseManager
from flashlearn.adts.user import User

class UserHandler:
    def __init__(self):
        self._db = DatabaseManager()

    def login(self, user: str, password: str) -> User:
        info = self._db.select_from_table("USER", email=user, password=password)
        if not info:
            info = self._db.select_from_table("USER", name=user, password=password)
        if not info:
            return None
        return User(info[0], info[1], info[3])
    
    def register(self, user: str, password: str, email: str):
        self._db.insert_into_table("USER", name=user, password=password, email=email)
        info = self.login(user, password)
        if not info:
            return None
        return info
    
    def get_user(self, email: str) -> User:
        info = self._db.select_from_table("USER", email=email)
        if not info:
            return None
        return User(info[0], info[1], info[3])
        