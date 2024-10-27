import os
import sys
import subprocess

def install():
    # Création de l'environnement virtuel si inexistant
    if not os.path.exists("venv"):
        print("Création de l'environnement virtuel...")
        subprocess.run(["python3", "-m", "venv", "venv"])
    
    # Chemin vers pip dans l'environnement virtuel
    pip_path = "venv/bin/pip"
    
    # Vérifier si pip existe, sinon l'installer
    if not os.path.exists(pip_path):
        print("Installation de pip dans l'environnement virtuel...")
        # Télécharger get-pip.py
        subprocess.run(["curl", "-sS", "https://bootstrap.pypa.io/get-pip.py", "-o", "get-pip.py"])
        # Installer pip dans l'environnement virtuel
        subprocess.run(["venv/bin/python", "get-pip.py"])
        # Supprimer le script get-pip.py après installation
        os.remove("get-pip.py")
    
    # Installation des dépendances
    print("Installation des dépendances...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])

    # Création du dossier des serveurs
    print("Création du dossier des serveurs...")
    if not os.path.exists("servers"):
        os.mkdir("servers")

    print("Installation terminée")

if __name__ == "__main__":
    install()
    # Exécuter le script init_db.py dans l'environnement virtuel
    subprocess.run(["venv/bin/python", "init_db.py"])
    sys.exit(0)
