from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file, Response, flash
import psutil
import json
import os
import time
import subprocess
import requests
import mcstatus
from mcrcon import MCRcon
import glob
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from wsgidav.wsgidav_app import WsgiDAVApp
from wsgidav.fs_dav_provider import FilesystemProvider
import shutil
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "b'\x84\t\x8c\x94\xdc\x1a\x8bv\x18Ac\xaf\xf4*\xeeDu\x9e\xe4y\x02\x085a'" #os.urandom(24) # On enleve la génération de clé secrete pour les tests
# print(app.secret_key)

# ------------------------------------------ JSON file paths ---------------------------------- #
JSON_DIR = os.path.abspath(os.path.dirname(__file__))
USERS_FILE = os.path.join(JSON_DIR, 'users.json')
SERVERS_FILE = os.path.join(JSON_DIR, 'servers.json')
VERSIONS_FILE = os.path.join(JSON_DIR, 'versions.json')
COMMANDS_FILE = os.path.join(JSON_DIR, 'commands.json')
SETTINGS_FILE = os.path.join(JSON_DIR, 'settings.json')
JAVA_PATH = "/usr/bin/java"

# --- User management ---
class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = str(id)
        self.username = username
        self.password_hash = password_hash
        self.role = role

    @staticmethod
    def load_all():
        if not os.path.exists(USERS_FILE):
            return {}
        with open(USERS_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_all(users):
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)

    @classmethod
    def get(cls, username):
        users = cls.load_all()
        for uid, u in users.items():
            if u['username'] == username:
                return cls(uid, u['username'], u['password_hash'], u['role'])
        return None

    @classmethod
    def get_by_id(cls, id):
        users = cls.load_all()
        u = users.get(str(id))
        if u:
            return cls(id, u['username'], u['password_hash'], u['role'])
        return None

    @classmethod
    def create(cls, username, password, role):
        users = cls.load_all()
        # assign new id
        new_id = max([int(i) for i in users.keys()] + [0]) + 1
        users[str(new_id)] = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'role': role
        }
        cls.save_all(users)
        return cls.get(username)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def delete(self):
        users = User.load_all()
        if self.id in users:
            del users[self.id]
            User.save_all(users)

# ------------------------------------------------- Flask-Login setup ---------------------------------------------------#
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ----------------------------------------------- Authentication routes -------------------------------#
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ----------------------------------------------- Utility to load/save other JSON files -------------------------------------------- #
def load_json(path):
    if not os.path.isfile(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ---------------------------------------------------- Routes for server management ---------------------------------------------------- #
# |||||||||||| Pages affichés |||||||||||| #
@app.route('/') # racine du projet
@login_required
def home():
    return render_template('index.html')

@app.route('/favicon.ico') # retour de l'icone
def favicon():
    return send_file('favicon.ico')

@app.route('/css/style.css') # retour du fichiers css
def send_css():
    return send_file('templates/css/style.css')

@app.route('/js/script.js') # retour du fichiers js
@login_required
def send_js():
    return send_file('templates/js/script.js')

@app.route('/server')
#@login_required
def server():
    return render_template('server.html')

@app.route('/servers')
#@login_required
def servers():
    return render_template('servers.html')

@app.route('/settings')
#@login_required
@role_required('root')
def settings():
    return render_template('settings.html')

@app.route('/users')
@login_required
@role_required('root')
def usersServe():
    return render_template('users.html')

def download_file(url, save_path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        expected_size = int(r.headers.get('content-length', 0))

        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        # Verify the file size
        current_size = os.path.getsize(save_path)
        if current_size == expected_size:
            print("File download completed.")
        else:
            print(f"File download incomplete. Expected size: {expected_size}, Actual size: {current_size}")

# |||||||||||| Nouveau serveur (API + PAGE) |||||||||||| #
@app.route('/new-server')
@login_required
def new_server():
    if request.args.get('serverName'):
        data = request.args
        name = data.get('serverName')
        cfg = {
            'type': data.get('serverType'),
            'version': data.get('serverVersion'),
            'ramMin': data.get('serverRamMin', '1G'),
            'ramMax': data.get('serverRamMax', '2G'),
            'port': data.get('serverPort', '25565'),
            'seed': data.get('serverSeed', ''),
            'maxPlayers': data.get('serverMaxPlayers', '20'),
            'dir': "./" + os.path.join('servers', name)
        }
        servers = load_json(SERVERS_FILE)
        servers[name] = cfg
        save_json(SERVERS_FILE, servers)
        os.makedirs(cfg['dir'], exist_ok=True)
        versions = load_json(VERSIONS_FILE)
        url = versions[cfg['type']][cfg['version']]
        jar_path = os.path.join(cfg['dir'], 'install.jar')
        download_file(url, jar_path)

        with open(os.path.join(cfg['dir'], 'eula.txt'), 'w') as f:
            f.write('eula=true')
        props = [
            f"server-port={cfg['port']}",
            f"level-seed={cfg['seed']}",
            f"max-players={cfg['maxPlayers']}"
        ]
        with open(os.path.join(cfg['dir'], 'server.properties'), 'w') as f:
            f.write("\n".join(props))

        commands = load_json(COMMANDS_FILE)
        command = commands[cfg['type']][cfg['version']]['install']
        print("Directory:", cfg['dir'])
        command = command.lstrip('java')
        cmd = JAVA_PATH + command
        print("Command to execute:", cmd)

        try:
            # Changer le répertoire de travail
            os.chdir(cfg['dir'])

            # Exécuter la commande
            result = os.popen(cmd).read()
            # result = subprocess.run(cmd, cwd=cfg['dir'], capture_output=True, text=True, check=True)
            print("Command executed successfully")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr}")

        files = glob.glob(os.path.join(cfg['dir'], 'minecraft_server.*.jar'))
        print("Found files:", files)
        if files:
            os.rename(files[0], os.path.join(cfg['dir'], 'server.jar'))

        return redirect(f"/server?name={name}")

    return render_template('new-server.html')

# |||||||||||| API pour controler un serveur |||||||||||| #
@app.route('/servers-ctrl') # Faire des actions sur un serveur
@login_required
def servers_ctrl():
    name = request.args.get('name')
    action = request.args.get('action')
    servers = load_json(SERVERS_FILE)
    commands = load_json(COMMANDS_FILE)
    if name not in servers:
        return jsonify({'error': 'Server not found'}), 404
    cfg = servers[name]
    if action == 'start': # Démarrer
        print(subprocess.run(commands[cfg['type']][cfg['version']]['start'], cwd=cfg['dir'], shell=True))
    elif action == 'stop': # Arreter
        with MCRcon('localhost', 25575, 'password') as mcr:
            mcr.command('stop')
    elif action == 'kill': # Tuer
        for p in psutil.process_iter():
            if p.name() == 'java' and cfg['dir'] in p.cmdline():
                p.kill()
                break
    elif action == 'delete': # Supprimer
        shutil.rmtree(cfg['dir'], ignore_errors=True)
        del servers[name]
        save_json(SERVERS_FILE, servers)
    return jsonify({'status': 'ok'})

# |||||||||||| API pour obtenir des infos sur un serveur |||||||||||| #
@app.route('/server-info')
@login_required
def server_info():
    server_name = request.args.get('name') # On recupère le paramètre
    with open('servers.json', 'r') as f:
        servers = json.load(f)
    if server_name in servers: # et on le compare avec la liste dans "servers.json"
        server = servers[server_name]
        # on récupère les infos du serveur
        server_dir = server['dir']
        server_ram_min = server['ramMin']
        server_ram_max = server['ramMax']
        server_port = server['port']
        server_type = server['type']
        server_version = server['version']

        server['status'] = 'inactive'
        server['ip'] = None
        
        for p in psutil.process_iter():
            if p.name() == 'java' and server['dir'] in p.cmdline():
                server['status'] = 'active'
                server['ramUsed'] = psutil.Process(p.pid).memory_info().rss / (1024**2)
                break
        try:
            status = mcstatus.MinecraftServer('localhost', int(server['port'])).status()
            server['players'] = status.players.online
        except:
            server['players'] = 0
        return jsonify(server) # et on renvoie en json
    print('Server not found')
    return jsonify({'error': 'Server not found'}), 404

def tail(file): # Fonction pour renvoyer le contenue d'un fichier en stream
    with open(file) as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield f"data:{line}\n\n"

# |||||||||||| API pour obtenir les logs d'un serveur [En developpement] |||||||||||| #
@app.route('/server-log_stream')
@login_required
def server_log(): # retourne un flux
    server_name = request.args.get("name")
    with open('servers.json') as j:
        servers = json.load(j)
    log_dir = servers[server_name]['log']
    return Response(tail(log_dir))

# |||||||||||| API pour modifier le fichier "properties" d'un serveur |||||||||||| #
app.route('/server-properties')
@login_required
def server_properties():
    server_name = request.args.get('name')
    with open('servers.json', 'r') as f:
        servers = json.load(f)
    if server_name in servers:
        server = servers[server_name]
        server_dir = server['dir']
        with open(f'{server_dir}/server.properties', 'r') as f:
            properties = f.read()
        return jsonify(properties)

# |||||||||||| API pour reevoir les versions d'un serveur |||||||||||| #
@app.route('/server-versions') # retour des versions des serveurs ()
@login_required
def server_versions():
    # chargé le fichier json des versions
    with open('versions.json', 'r') as f: 
        versions = json.load(f)
    if True : #request.args.get('type') in locals():
        response = versions[request.args.get('type')]
    else:
        response = ['error']
    return jsonify(response)

# |||||||||||| API pour obtenir les stats du SERVEUR |||||||||||| #
@app.route('/main-serverinfo') ## A transformer en stream
@login_required
def main_serverinfo():
    return jsonify({
        'diskUsage': psutil.disk_usage('/').percent,
        'memUsage': psutil.virtual_memory().percent,
        'cpuUsage': psutil.cpu_percent(interval=1),
        'bandwidth': psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
    })

# |||||||||||| API pour obtenir les infos des servers |||||||||||| #
@app.route('/servers-data')
@login_required
def servers_data():
    with open('servers.json', 'r') as f:
        servers = json.load(f)
    for server in servers:
        server_dir = servers[server]['dir']
        server_port = servers[server]['port']
        servers[server]['status'] = 'inactive'
        
        for process in psutil.process_iter():
            if process.name() == 'java' and server_dir in process.cmdline():
                servers[server]['status'] = 'active'
                break
        try:
            mc_server = mcstatus.MinecraftServer('localhost', int(server_port)).status()
            status = mc_server.status()
            servers[server]['players'] = len(mcstatus.MinecraftServer('localhost', int(server_port)).status().players.sample)
        except Exception as e:
            servers[server]['players'] = 0
    return jsonify(servers)

# |||||||||||| API pour changer les settings |||||||||||| #
@app.route('/settings-ctl')
@login_required
@role_required('root')
def settings_ctrl():
    action = request.args.get('action')
    if action == 'get':
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        return jsonify(settings)
    elif action == 'add':
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        settings.update(request.args)
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        return jsonify({'status': 'ok'})
    elif not action:
        with open('settings.json', 'w') as f:
            json.dump(request.args, f)
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'})

# |||||||||||| API pour modifier les utilisateurs |||||||||||| #
@app.route('/users-ctl')
@login_required
@role_required('root')
def users_ctl():
    action   = request.args.get('action')
    username = request.args.get('username')
    # Charge tout
    all_users = User.load_all()

    # 1) GET : liste des users + rôles
    if action == 'get':
        resp = { u['username']: {'role': u['role']} for u in all_users.values() }
        return jsonify(resp)

    # 2) ADD : créer un user
    elif action == 'add':
        username = request.args.get('username')
        password = request.args.get('password')
        role     = request.args.get('role')
        if not username or not password or not role:
            return jsonify({'status':'error', 'msg':'username, password et role requis'}), 400

        user = User.create(username, password, role)
        if not user:
            return jsonify({'status':'error', 'msg':'utilisateur existe déjà'}), 409

        return jsonify({'status':'ok', 'id': user.id})

    # 3) DELETE : supprimer un user
    elif action == 'delete':
        if not username:
            return jsonify({'status':'error', 'msg':'username requis'}), 400
        user = User.get(username)
        if not user:
            return jsonify({'status':'error', 'msg':'utilisateur non trouvé'}), 404
        user.delete()
        return jsonify({'status':'ok'})

    # 4) MODIFY : changer role et/ou password
    elif action == 'modify':
        if not username:
            return jsonify({'status':'error', 'msg':'username requis'}), 400
        user = User.get(username)
        if not user:
            return jsonify({'status':'error', 'msg':'utilisateur non trouvé'}), 404

        # nouvelle charge JSON
        users = User.load_all()
        rec = users[user.id]

        new_role = request.args.get('role')
        new_pwd  = request.args.get('password')

        if new_role:
            rec['role'] = new_role
        if new_pwd:
            rec['password_hash'] = generate_password_hash(new_pwd)

        User.save_all(users)
        return jsonify({'status':'ok'})

    # action inconnue
    return jsonify({'status':'error', 'msg':'action invalide'}), 400

@app.errorhandler(404)
#@login_required
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
#@login_required
def internal_server_error(error):
    return render_template('500.html'), 500

# --- WebDAV setup [En developpement] --- #
with app.app_context():
    dav_provider = FilesystemProvider(os.getcwd(), readonly=False)
    dav_app = WsgiDAVApp({
        'provider_mapping': {'/': dav_provider},
        'simple_dc': {'user_mapping': {'*': True}},
        'http_authenticator': {'accept_basic': True},
        'dir_browser': {'enable': True},
        'verbose': 1
    })
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/webdav': dav_app})

@app.route('/webdav')
@login_required
def webdav():
    return redirect('/webdav/')

if __name__ == '__main__':
    with open(SETTINGS_FILE, 'r') as f:
        settings_port = json.load(f)
        
    app.run(host='0.0.0.0', port=settings_port["port"], debug=True)
