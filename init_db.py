#---------------------------------------------------------------Importations
import json
import os
from werkzeug.security import generate_password_hash

USERS_FILE = "users.json"

def init_db():
    # suppression des tables
    with open(USERS_FILE, "w") as f:
        json.dump({"codes": []}, f, indent=4)
        
    print("Ajout de l'utilisateur admin {root}")
    print("Adding the admin user {root}")
    print("Veuillez entrer le mot de passe de l'utilisateur admin {root}")
    print("Please enter the password of the admin user {root}")
    password = input()
    # ajout de l'utilisateur admin
    create_user_access(password, "root")

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
    create_user_access(password, "user")
        
    db.session.commit()
    print("Base de données initialisée avec succès et utilisateurs ajoutés.")

def create_user_access(code, role):
    data = {"codes": []}

    # Charger le fichier s'il existe
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Fichier JSON corrompu, recréation.")

    # Vérifier si le code existe déjà
    for entry in data["codes"]:
        if entry["code"] == code:
            print("⚠️ Ce code existe déjà.")
            return

    # Ajouter le nouvel accès
    data["codes"].append({
        "code": code,
        "role": role
    })

    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Accès '{role}' avec code '{code}' ajouté.")


init_db()