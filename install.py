# script d'installation de l'application ne requerant aucune dependance
# il installe les dependances de "requirement.txt"
# crée le dossier des serveurs

import os
import sys
import subprocess

def install():
    # installation des dependances
    print("Installation des dependances")
    subprocess.run(["pip3", "install", "-r", "requirements.txt"])

    # creation du dossier des serveurs
    print("Creation du dossier du dossier des serveurs")
    if not os.path.exists("servers"):
        os.mkdir("servers")

    print("Installation terminee")

if __name__ == "__main__":
    install()
    sys.exit(0)