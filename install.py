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
        13: "[INFO] -- Éxecution de \"init_db.py\"...",
        14: "[INFO] -- PyQt5 fonctionnel",
        15: "[ERROR] -- PyQt5 n'est pas installé",
        16: "Pouvez vous indiquer le chemin de java ? (Sur linux, vous pouvez utiliser 'whereis java')"
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
        13: "[INFO] -- Execution of \"init_db.py\"...",
        14: "[INFO] -- PyQt5 functional",
        15: "[ERROR] -- PyQt5 is not installed",
        16: "Can you provide the path to java? (On linux you can use 'whereis java')"
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
        13: "[INFO] -- Ausführung von \"init_db.py\"...",
        14: "[INFO] -- PyQt5 funktioniert",
        15: "[ERROR] -- PyQt5 ist nicht installiert",
        16: "Können Sie den Pfad zu Java angeben? (Unter Linux können Sie „whereis java“ verwenden.)"
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
        13: "[INFO] -- Ejecución de \"init_db.py\"...",
        14: "[INFO] -- PyQt5 está funcionando",
        15: "[ERROR] -- PyQt5 no está instalado",
        16: "¿Podrías proporcionar la ruta a Java? (En Linux, puedes usar \"whereis java\")"
    }
}

#---------------------------------------------------------------Importations
import os
import sys
import subprocess
import json
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    for lang_code, phrases in languages.items():
        print(phrases[14])
    GUI = True
except ImportError:
    for lang_code, phrases in languages.items():
        print(phrases[15])
    class QMainWindow(): # Afin de ne pas avoir d'erreur après
        pass
    GUI = False

#---------------------------------------------------------------Platform commands
platform_commands = {
    "linux": ["python3"],
    "win32": ["python"],
    "cygwin": ["python"],
    "darwin":["python"],
    "aix": ["python"]
}

#---------------------------------------------------------------Variables definitions
SETTINGS_FILE = os.path.join('Config','settings.json')
language_chosen = None
finish = False
system_platform = sys.platform
logo_path = os.path.join('imgs', 'favicon-abbg.ico')

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
    subprocess.run([pip_path, "install", "-r", os.path.join("Utils", "requirements.txt")])

    #---------------------------------------Creation of the folder "servers"
    print("\n")
    print(languages[language_chosen][12])
    if not os.path.exists("Servers"):
        os.mkdir("Servers")
    
    #---------------------------------------Add java_path to settings.json
    print("\n")
    print(languages[language_chosen][16])
    with open(SETTINGS_FILE, 'r') as s:
        settings = json.load(s)
        settings['java_path'] = input("\n")
    with open(SETTINGS_FILE, "w") as s:
        json.dump(settings, s, indent=4)

    #---------------------------------------Execution of "init_db.py"
    print("\n")
    print(languages[language_chosen][13])
    if pip_path == "./venv/bin/pip":
        print("\n")
        subprocess.run(["venv/bin/python", os.path.join("Utils", "init_db.py")])
    else:
        print("\n")
        subprocess.run([platform_commands[system_platform][0], os.path.join("Utils", "init_db.py")])

#---------------------------------------------------------------GUI Language
class GUI_Language(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MinePylot : Language")
        self.setWindowIcon(QIcon(logo_path))
        self.setGeometry(300, 100, 1100, 550)
        self.setFixedWidth(1150)
        self.setFixedHeight(550)
        self.setStyleSheet("background-color: #1e1f22; color: #ffffff;")

        QApplication.setStyle("windows")  # Fusion or WindowsVista

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left Section - Logo
        left_layout = QVBoxLayout()
        logo_pixmap = QPixmap(logo_path).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap)
        left_layout.addSpacing(50)
        left_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        footer_label = QLabel("2025 - Made by Lasertie and $now_")
        footer_label.setStyleSheet("font-size: 12px; color: #555555;")
        left_layout.addWidget(footer_label, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("border: 1px solid #72bf3c;")
        separator.setFixedWidth(2)

        # Right Section - Text and Controls
        right_layout = QVBoxLayout()
        for lang_code, phrases in languages.items():
            label = QLabel(phrases[2])
            label.setStyleSheet("font-size: 14px; padding: 8px; background-color: #2c2f33; border-radius: 5px; margin-top: 15px; margin-bottom: 5px; margin-right: 20px;")
            right_layout.addWidget(label)

        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(["Français", "English", "Deutsch", "Español"])
        self.language_dropdown.setStyleSheet("QComboBox {padding: 5px; font-size: 16px; background-color: #2f3136; color: #ffffff; border: 1px solid #72bf3c; border-radius: 5px; margin-left: 50px; margin-right: 70px; margin-top: 50px} QComboBox::drop-down {background-color: #2f3136; width: 30px; padding-left: 5px;} QComboBox::down-arrow {image: url('arrow.png'); width: 16px; height: 16px; background-color: transparent;} QComboBox QAbstractItemView {background-color: #2f3136; selection-background-color: #444751; selection-color: #ffffff; border: 1px solid #72bf3c;}")
        right_layout.addWidget(self.language_dropdown)

        ok_button = QPushButton("OK")
        ok_button.setStyleSheet("background-color: #72bf3c; padding: 10px; font-size: 16px; border-radius: 5px; margin-left: 50px; margin-right: 70px; margin-top: 150px;")
        ok_button.clicked.connect(self.save_language)
        right_layout.addWidget(ok_button)
        right_layout.addStretch()

        # Add sections to the main layout
        main_layout.addLayout(left_layout)
        main_layout.addSpacing(20)
        main_layout.addWidget(separator)
        main_layout.addSpacing(20)
        main_layout.addLayout(right_layout)

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
        self.setWindowTitle(f"MinePylot : {title}")
        self.setWindowIcon(QIcon(os.path.join('imgs', 'favicon-abbg.ico')))
        self.setGeometry(300, 100, 1100, 550)
        self.setFixedWidth(1150)
        self.setFixedHeight(550)
        self.setStyleSheet("background-color: #1e1f22; color: #ffffff;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left Section - Logo
        left_layout = QVBoxLayout()
        logo_pixmap = QPixmap(logo_path).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation)
        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap)
        left_layout.addSpacing(50)
        left_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        footer_label = QLabel("2025 - Made by Lasertie and $now_")
        footer_label.setStyleSheet("font-size: 12px; color: #555555;")
        left_layout.addWidget(footer_label, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("border: 1px solid #72bf3c;")
        separator.setFixedWidth(2)

        # Right Section - Text and Controls
        right_layout = QVBoxLayout()
        venv_text = languages[language_chosen][6]
        venv_label = QLabel(venv_text)
        venv_label.setStyleSheet("font-size: 14px; padding: 8px; background-color: #2c2f33; border-radius: 5px; margin-top: 150px; margin-bottom: 5px; margin-right: 20px;")

        right_layout.addWidget(venv_label)

        yes_button = QPushButton(languages[language_chosen][9])
        yes_button.setStyleSheet("background-color: #72bf3c; padding: 10px; font-size: 16px; border-radius: 5px; margin-left: 50px; margin-right: 70px; margin-top: 150px;")
        yes_button.clicked.connect(self.create_venv)
        right_layout.addWidget(yes_button)
        right_layout.addStretch()

        no_button = QPushButton(languages[language_chosen][10])
        no_button.setStyleSheet("background-color: #72bf3c; padding: 10px; font-size: 16px; border-radius: 5px; margin-left: 50px; margin-right: 70px; margin-top: 10px;")
        no_button.clicked.connect(self.skip_venv)
        right_layout.addWidget(no_button)
        right_layout.addStretch()

        # Add sections to the main layout
        main_layout.addLayout(left_layout)
        main_layout.addSpacing(20)
        main_layout.addWidget(separator)
        main_layout.addSpacing(20)
        main_layout.addLayout(right_layout)

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

    if (GUI != False):
        app = QApplication(sys.argv)

    print(r"""
    __  ____            ____        __      __ 
   /  |/  (_)___  ___  / __ \__  __/ /___  / /_
  / /|_/ / / __ \/ _ \/ /_/ / / / / / __ \/ __/
 / /  / / / / / /  __/ ____/ /_/ / / /_/ / /_  
/_/  /_/_/_/ /_/\___/_/    \__, /_/\____/\__/  
                          /____/               
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
        #-----------------------------------Ask port (Important car définit le port dans settings.json, sans ca le server ne démarerra pas)
        with open(SETTINGS_FILE) as file:
            settings = json.load(file)
        print(languages[language_chosen][14])
        settings["port"] = input('[Default : 5000] : ')
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        finish_installation()

    elif configuration_chosen == "GUI":
        window = GUI_Language()
        window.show()

    if (GUI != False):
        sys.exit(app.exec())