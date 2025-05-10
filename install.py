#---------------------------------------------------------------Importations
import os
import sys
import subprocess
import json
from PyQt5.QtWidgets import *

#---------------------------------------------------------------Languages
languages = {
    "fr": {
        1: "[FR] Voulez-vous utiliser l'application en ligne de commande ou avec interface graphique ?",
        2: "[FR] Choisissez votre langue",
        3: "[FR] Aucune langue choisie",
        4: "Voulez-vous créer un environnement virtuel pour exécuter l'application ? (O/n) : ",
        5: "Environnement virtuel",
        6: "Voulez-vous créer un environnement virtuel pour exécuter l'application ?",
        7: "[INFO] -- Création de l'environnement virtuel...",
        8: "[INFO] -- Environnement virtuel non créé",
        9: "Oui",
        10: "Non",
        11: "[INFO] -- Installation des dépendances...",
        12: "[INFO] -- Création du dossier \"servers\"...",
        13: "[INFO] -- Éxecution de \"init_db.py\"..."
    },
    "en": {
        1: "[EN] Do you want to use the application from the command line or with a graphical interface ?",
        2: "[EN] Choose your language",
        3: "[EN] No language chosen",
        4: "Do you want to create a virtual environment to run the application ? (Y/n) : ",
        5: "Virtual environment",
        6: "Do you want to create a virtual environment to run the application ?",
        7: "[INFO] -- Creating the virtual environment...",
        8: "[INFO] -- Virtual environment not created",
        9: "Yes",
        10: "No",
        11: "[INFO] -- Installing dependencies...",
        12: "[INFO] -- Creation of the folder \"servers\"...",
        13: "[INFO] -- Execution of \"init_db.py\"..."
    },
    "de": {
        1: "[DE] Möchten Sie die Anwendung als Kommandozeile oder mit grafischer Benutzeroberfläche verwenden ?",
        2: "[DE] Wählen Sie Ihre Sprache",
        3: "[DE] Keine Sprache gewählt",
        4: "Möchten Sie eine virtuelle Umgebung erstellen, um die Anwendung auszuführen ? (J/n) : ",
        5: "Virtuelle Umgebung",
        6: "Möchten Sie eine virtuelle Umgebung erstellen, um die Anwendung auszuführen ?",
        7: "[INFO] -- Erstellen der virtuellen Umgebung...",
        8: "[INFO] -- Virtuelle Umgebung nicht erstellt",
        9: "Ja",
        10: "Nein",
        11: "[INFO] -- Installation von Abhängigkeiten...",
        12: "[INFO] -- Anlegen des Ordners \"servers\"...",
        13: "[INFO] -- Ausführung von \"init_db.py\"..."
    },
    "es": {
        1: "[ES] ¿ Desea utilizar la aplicación en la línea de comandos o con una interfaz gráfica ?",
        2: "[ES] Elija su idioma",
        3: "[ES] Ninguna lengua elegida",
        4: "¿ Desea crear un entorno virtual para ejecutar la aplicación ? (S/n) : ",
        5: "Entorno virtual",
        6: "¿ Desea crear un entorno virtual para ejecutar la aplicación ?",
        7: "[INFO] -- Creación del entorno virtual...",
        8: "[INFO] -- Entorno virtual no creado",
        9: "Sì",
        10: "No",
        11: "[INFO] -- Instalando dependencias...",
        12: "[INFO] -- Creación de carpeta \"servers\"...",
        13: "[INFO] -- Ejecución de \"init_db.py\"..."
    }
}

#---------------------------------------------------------------Platform commands 
platform_commands = {
    "linux": [
        "python3"
    ],
    "win32": [
        "python"
    ],
    "cygwin": ["python"],
    "darwin":["python"],
    "aix": ["python"]
}

#---------------------------------------------------------------Variables definitions
SETTINGS_FILE = "settings.json"
language_chosen = None
finish = False
system_platform = sys.platform

#---------------------------------------------------------------Save Language
def save_language(language):
    data = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                pass

    data["language"] = language

    with open(SETTINGS_FILE, "w") as file:
        json.dump(data, file, indent=4)

#---------------------------------------------------------------Finish installation
def finish_installation():
    #---------------------------------------Dependencies installation
    print("\n")
    print(languages[language_chosen][11])
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])

    #---------------------------------------Creation of the folder "servers"
    print("\n")
    print(languages[language_chosen][12])
    if not os.path.exists("servers"):
        os.mkdir("servers")

    #---------------------------------------Execution of "init_db.py"
    print("\n")
    print(languages[language_chosen][13])
    if pip_path == "./venv/bin/pip":
        print("\n")
        subprocess.run(["venv/bin/python", "init_db.py"])
    else:
        print("\n")
        subprocess.run([platform_commands[system_platform][0], "init_db.py"])

#---------------------------------------------------------------GUI Language
class GUI_Language(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MinecraftServerUI : Language")
        self.setGeometry(300, 300, 400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        for lang_code, phrases in languages.items():
            label = QLabel(phrases[2])
            layout.addWidget(label)

        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(["Français", "English", "Deutsch", "Español"])
        layout.addWidget(self.language_dropdown)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_language)
        layout.addWidget(ok_button)

    def save_language(self):
        global language_chosen

        language_chosen = self.language_dropdown.currentText()
        language_chosen = {
            "Français": "fr",
            "English": "en",
            "Deutsch": "de",
            "Español": "es"
        }.get(language_chosen, "en")

        save_language(language_chosen)
        self.close()

        # Ouvrir la fenêtre pour le venv
        self.venv_window = GUI_Venv()
        self.venv_window.show()


#---------------------------------------------------------------GUI Venv
class GUI_Venv(QMainWindow):
    def __init__(self):
        super().__init__()

        title = languages[language_chosen][5]
        self.setWindowTitle(f"MinecraftServerUI : {title}")
        self.setGeometry(300, 300, 400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        venv_text = languages[language_chosen][6]
        venv_label = QLabel(venv_text)
        layout.addWidget(venv_label)

        yes_button = QPushButton(languages[language_chosen][9])
        yes_button.clicked.connect(self.create_venv)
        layout.addWidget(yes_button)

        no_button = QPushButton(languages[language_chosen][10])
        no_button.clicked.connect(self.skip_venv)
        layout.addWidget(no_button)

    def create_venv(self):
        global finish
        global pip_path
        print("\n")
        print(languages[language_chosen][7])
        subprocess.run([platform_commands[system_platform][0], "-m", "venv", "venv"])
        pip_path = "./venv/bin/pip"
        self.close()
        finish_installation()

    def skip_venv(self):
        global finish
        global pip_path
        print("\n")
        print(languages[language_chosen][8])
        pip_path = 'pip'
        self.close()
        finish_installation()

#-----------------------------------------------------------------------------------------------------------------------Main
if __name__ == "__main__":

    app = QApplication(sys.argv)

    print(r"""
    __  ____                            ______  _____                           __  ______
   /  |/  (_)___  ___  ______________ _/ __/ /_/ ___/___  ______   _____  _____/ / / /  _/
  / /|_/ / / __ \/ _ \/ ___/ ___/ __ `/ /_/ __/\__ \/ _ \/ ___/ | / / _ \/ ___/ / / // /  
 / /  / / / / / /  __/ /__/ /  / /_/ / __/ /_ ___/ /  __/ /   | |/ /  __/ /  / /_/ // /   
/_/  /_/_/_/ /_/\___/\___/_/   \__,_/_/  \__//____/\___/_/    |___/\___/_/   \____/___/   

""")

    #---------------------------------------Ask GUI/CMD
    for lang_code, phrases in languages.items():
        print(phrases[1])

    configuration_chosen = input("(CMD/GUI) : ").strip().upper()

    data = {"configuration": configuration_chosen}
    with open(SETTINGS_FILE, "w") as file:
        json.dump(data, file, indent=4)

    #---------------------------------------Ask Language and Venv
    if configuration_chosen == "CMD":
        print("\n")
        for lang_code, phrases in languages.items():
            print(phrases[2])
        language_chosen = input("(FR/EN/DE/ES) : ").strip().lower()
        save_language(language_chosen)
        print("\n")
        venv_choice = input(languages[language_chosen][4])
        if venv_choice.lower() in ["o", "y", "j", "s"]:
            subprocess.run([platform_commands[system_platform][0], "-m", "venv", "venv"])
            pip_path = "./venv/bin/pip"
        else:
            print(languages[language_chosen][8])
            pip_path = "pip"
        finish_installation()

    elif configuration_chosen == "GUI":
        window = GUI_Language()
        window.show()

    sys.exit(app.exec())