#---------------------------------------------------------------Importations
import json
import os
from werkzeug.security import generate_password_hash
import uuid

#---------------------------------------------------------------Languages
languages = {
    "fr": {
        1: "Choisissez un nom d'utilisateur ",
        2: "Choisissez un mot de passe pour l'utilisateur ",
        3: "Fichier JSON corrompu, recréation..."
    },
    "en": {
        1: "Choose a username  ",
        2: "Choose a password for the user ",
        3: "JSON file corrupted, recreate..."
    },
    "de": {
        1: "Wählen Sie einen Benutzernamen ",
        2: "Wählen Sie ein Passwort für den Benutzer ",
        3: "Beschädigte JSON-Datei, Neuerstellung..."
    },
    "es": {
        1: "Elija un nombre de usuario ",
        2: "Elija una contraseña para el usuario ",
        3: "Archivo JSON dañado, volver a crear..."
    }
}

#---------------------------------------------------------------Variables definitions
USERS_FILE = "users.json"

#---------------------------------------------------------------Create a user
def create_user_access(username, password, role):
    data = {}

    # Charger le fichier s'il existe
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("")#TODO

    # Générer le nouvel id
    new_id = uuid.uuid4()

    # Ajouter le nouvel accès
    data[new_id] = {
        "username": username,
        "password_hash": password,
        "role": role
    }

    # Écrire les données mises à jour dans le fichier
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("")#TODO

#---------------------------------------------------------------Remove a user
#TODO

#---------------------------------------------------------------Add a root user
def add_root_user():
    username = input()
    password = input()
    password_hash = generate_password_hash(password)
    create_user_access(username, password_hash, "root")

#---------------------------------------------------------------Add a moderator user
def add_moderator_user():
    username = input()
    password = input()
    password_hash = generate_password_hash(password)
    create_user_access(username, password_hash, "moderator")

#---------------------------------------------------------------Add a simple user
def add_simple_user():
    username = input()
    password = input()
    password_hash = generate_password_hash(password)
    create_user_access(username, password_hash, "user")

#-----------------------------------------------------------------------------------------------------------------------Main

password = input(languages["fr"][1])