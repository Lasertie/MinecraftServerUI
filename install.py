# script d'installation de l'application ne requerant aucune dependance
# il installe les dependances de "requirement.txt"
# crée le dossier des serveurs

import os
import sys
import subprocess
from init_db import init_db

def install():
    # installation des dependances
    print("Installation des dependances")
    print("Installing dependencies")
    subprocess.run(["pip3", "install", "-r", "requirements.txt"])

    # creation du dossier des serveurs
    print("Creation du dossier du dossier des serveurs")
    print("Creating the servers folder")
    if not os.path.exists("servers"):
        os.mkdir("servers")

    print("Installation terminee")
    print("Installation completed")
    init_db()

if __name__ == "__main__":
    install()
    init_db()
    sys.exit(0)