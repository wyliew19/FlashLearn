from flashlearn.utils.database import DatabaseManager
from flashlearn.models.user import User
import hashlib

class UserHandler:
    def __init__(self):
        self._db = DatabaseManager()

    def login(self, user: str, password: str) -> User:
        print(f"DEBUG::User Handler::login({user}, {password})")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        info = self._db.select_from_table("USER", email=user, password=hashed_password)
        if not info:
            info = self._db.select_from_table("USER", name=user, password=hashed_password)
        if not info:
            return None
        info = info[0]
        print(f"DEBUG::User Handler::login::info: {info}")
        return User(info[0], info[1], info[3])
    
    def register(self, user: str, password: str, email: str):
        print(f"DEBUG::User Handler::register({user}, {password}, {email})")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Check if user already exists
        try:
            self._db.insert_into_table("USER", name=user, password=hashed_password, email=email)
        except Exception as e:
            print(e)
            return None

        info = self.login(user, password)
        if not info:
            return None
        return info
    
    def get_user(self, email: str) -> User:
        print(f"DEBUG::User Handler::get_user({email})")
        info = self._db.select_from_table("USER", email=email)
        if not info:
            return None
        info = info[0]
        return User(info[0], info[1], info[3])
    
    def change_password(self, email: str, password: str, new_pass: str) -> bool:
        print(f"DEBUG::User Handler::change_password({email}, {password}, {new_pass})")
        hashed_password = hashlib.sha256(new_pass.encode()).hexdigest()
        if self.login(email, password) is None:
            return False
        self._db.update_table("USER", { "password" : hashed_password }, email=email)
        if self.login(email, new_pass) is None:
            raise Exception("Password change failed")
        return True