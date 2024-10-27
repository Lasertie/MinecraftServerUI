import os
import sys
import subprocess
import platform

def setup_autostart():
        system = platform.system()
        if system == "Windows":
            # Créer une tâche planifiée sur Windows
            os.system('schtasks /create /tn "StartApp" /tr "python3 {}" /sc onstart'.format(os.path.abspath("app.py")))
        elif system == "Darwin":
            # Créer un fichier plist sur macOS
            plist_content = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>com.MineGUI.app</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{os.abspath(venv)}/bin/python3</string>
                    <string>{os.path.abspath("app.py")}</string>
                </array>
                <key>RunAtLoad</key>
                <true/>
            </dict>
            </plist>
            """
            with open(os.path.expanduser("~/Library/LaunchAgents/com.example.app.plist"), "w") as f:
                f.write(plist_content)
            os.system("launchctl load ~/Library/LaunchAgents/com.example.app.plist")
        elif system == "Linux":
            # Créer un fichier de service systemd sur Linux
            service_content = f"""
            [Unit]
            Description=MineGUI

            [Service]
            ExecStart={os.abspath(venv)}/bin/python3 {os.path.abspath("app.py")}
            Restart=always

            [Install]
            WantedBy=multi-user.target
            """
            with open("/etc/systemd/system/app.service", "w") as f:
                f.write(service_content)
            os.system("sudo systemctl enable app.service")
            os.system("sudo systemctl start app.service")

def start():
    # demander a l'utilisateur s'il veut mettre a jour les fichiers
    print("Voulez-vous mettre a jour les fichiers depuis le repo github ? (o/n)")
    choix = input()
    if choix == "o":
        os.system('venv/bin/python3 maj.py')

    # demarrer le serveur
    print("Demarrage du serveur")
    os.system('venv/bin/flask run')

    # demander si l'utilisateur veut demarrer le serveur au demarrage de l'ordinateur
    print("Voulez-vous demarrer le serveur au demarrage de l'ordinateur ? [O(Oui)/n(Non)]")
    print("Would you like to start the server when the computer start ? [O(Yes)/n(No)]")
    choixdeux = input()
    if choixdeux == "O" or choixdeux == "o":
        setup_autostart()
    else:
        print("Le serveur ne demarrera pas au demarrage de l'ordinateur")
        print("Ok nothing append when the computer start...")

if __name__ == "__main__":
    start()
    sys.exit(0)