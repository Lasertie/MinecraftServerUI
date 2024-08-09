# mise a jour des fichiers servers.json, versions.json commands.json app.py depuis le repo github selon les choix de l'utilisateur

import os
import sys
import subprocess

def maj():
    # mise a jour des fichiers servers.json, versions.json commands.json app.py depuis le repo github selon les choix de l'utilisateur
    print("Mise a jour des fichiers depuis le repo github")
    subprocess.run(["git", "pull", "origin", "master"])
    print("Mise a jour terminee")

if __name__ == "__main__":
    maj()
    sys.exit(0)
