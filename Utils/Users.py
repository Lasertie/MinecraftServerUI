# --- User management ---
import json
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = str(id)
        self.username = username
        self.password_hash = password_hash
        self.role = role

    @staticmethod
    def load_all():
        if not os.path.exists(USERS_FILE):
            return {}
        with open(USERS_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_all(users):
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)

    @classmethod
    def get(cls, username):
        users = cls.load_all()
        for uid, u in users.items():
            if u['username'] == username:
                return cls(uid, u['username'], u['password_hash'], u['role'])
        return None

    @classmethod
    def get_by_id(cls, id):
        users = cls.load_all()
        u = users.get(str(id))
        if u:
            return cls(id, u['username'], u['password_hash'], u['role'])
        return None

    @classmethod
    def create(cls, username, password, role):
        users = cls.load_all()
        # assign new id
        new_id = max([int(i) for i in users.keys()] + [0]) + 1
        users[str(new_id)] = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'role': role
        }
        cls.save_all(users)
        return cls.get(username)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def delete(self):
        users = User.load_all()
        if self.id in users:
            del users[self.id]
            User.save_all(users)
