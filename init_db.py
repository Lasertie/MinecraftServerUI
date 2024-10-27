from app import db, User, app
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # suppression des tables
        db.drop_all()
        # création des tables
        db.create_all()
        
        print("Ajout de l'utilisateur admin {root}")
        print("Adding the admin user {root}")
        print("Veuillez entrer le mot de passe de l'utilisateur admin {root}")
        print("Please enter the password of the admin user {root}")
        password = input()
        # ajout de l'utilisateur admin
        user = User(username="root", password=password, role="root")
        db.session.add(user)

        print("Ajout d'un utilisateur de base (user)")
        print("Adding a basic user (user)")
        print("Veuillez entrer le nom d'utilisateur de l'utilisateur de base (user)")
        print("Please enter the username of the user 'user'")
        username = input()
        print("Veuillez entrer le mot de passe de l'utilisateur de base (user)")
        print("Please enter the password of the user 'user'")
        password = input()
        # hash du mot de passe
        password = generate_password_hash(password)
        # ajout de l'utilisateur de base
        user = User(username=username, password=password, role="user")
        db.session.add(user)
        
        db.session.commit()
        print("Base de données initialisée avec succès et utilisateurs ajoutés.")

init_db()