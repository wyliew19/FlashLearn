from flashlearn.utils.database import DatabaseManager
from flashlearn.models.user import User
import hashlib

class UserHandler:
    def __init__(self):
        self._db = DatabaseManager()

    def login(self, user: str, password: str) -> User:
        print(f"DEBUG::User Handler::login({user}, {password})")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        info = self._db.select_from_table("USER", email=user, password=password)
        if not info:
            info = self._db.select_from_table("USER", name=user, password=password)
        if not info:
            return None
        return User(info[0], info[1], info[3])
    
    def register(self, user: str, password: str, email: str):
        print(f"DEBUG::User Handler::register({user}, {password}, {email})")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self._db.insert_into_table("USER", name=user, password=hashed_password, email=email)
        info = self.login(user, password)
        if not info:
            return None
        return info
    
    def get_user(self, email: str) -> User:
        print(f"DEBUG::User Handler::get_user({email})")
        info = self._db.select_from_table("USER", email=email)
        if not info:
            return None
        return User(info[0], info[1], info[3])
        