### Je suis lla ohoihbljk
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, abort, send_file, send_from_directory, Response
import psutil
import json
import os
import time
import subprocess
import requests
import mcstatus
from mcrcon import MCRcon
import glob
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_httpauth import HTTPBasicAuth
from wsgidav.wsgidav_app import WsgiDAVApp
from wsgidav.fs_dav_provider import FilesystemProvider
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.wrappers import Request, Response

app = Flask(__name__)
auth = HTTPBasicAuth()
# clé generée aléatoirement a chaque fois que le serveur est lancé
app.secret_key = 'os.urandom(24)'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)

    def __init__(self, username, password, role):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            app.logger.warning(f'Failed login attempt for {username}')
    return render_template('login.html')

#@login_required
login_manager.unauthorized = lambda: redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

@app.route('/') # retour de la page d'accueil
@login_required
def home():
    return render_template('index.html')

@app.route('/new-server')
@login_required
def new_server():
    if request.args.get('serverName') and request.args.get('serverType') and request.args.get('serverVersion'):
        # recuperation des données du formulaire
        server_name = request.args.get('serverName')
        server_type = request.args.get('serverType')
        server_version = request.args.get('serverVersion')
        # si la ram est spécifié on la récupère
        if request.args.get('serverRamMin'):
            server_ram_min = request.args.get('serverRamMin')
        else:
            server_ram_min = '1G'
        if request.args.get('serverRamMax'):
            server_ram_max = request.args.get('serverRamMax')
        else:
            server_ram_max = '2G'
        if request.args.get('serverPort'):
            server_port = request.args.get('serverPort')
        else:
            server_port = '25565'
        if request.args.get('serverSeed'):
            server_seed = request.args.get('serverSeed')
        else:
            server_seed = ''
        if request.args.get('serverMaxPlayers'):
            server_maxPlayers = request.args.get('serverMaxPlayers')
        else:
            server_maxPlayers = '20'

        # Chemin du dossier du serveur
        server_path = f'servers/{server_name}'

        #On ajoute le serveur dans la liste des serveurs si le fichier n'existe pas on le crée
        if not os.path.isfile('servers.json'):
            with open('servers.json', 'w') as f:
                f.write('{}')
        with open('servers.json', 'r') as f:
            servers = json.load(f)
        # Vérifiez que servers est une liste

        servers[server_name] = {
            'type': server_type,
            'version': server_version,
            'ramMin': server_ram_min,
            'ramMax': server_ram_max,
            'port': server_port,
            'dir': server_path,
            'maxPlayers': server_maxPlayers
        }

        # on crée le dossier du serveur
        os.system(f'mkdir "{server_path}"')
        os.system(f'cd {server_path}')

        with open('versions.json', 'r') as f:
            versions = json.load(f)
        url = versions[server_type][server_version]
        file_dir = os.path.join(server_path, 'install.jar')
        print("Downloading file ...")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(file_dir, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.exceptions.HTTPError as http_err:
            print(f'Erreur HTTP: {http_err}')
        except requests.exceptions.ConnectionError as conn_err:
            print(f'Erreur HTTP: {conn_err}')
        except requests.exceptions.Timeout as timeout_err:
            print(f'Erreur HTTP: {timeout_err}')
        except requests.exceptions.RequestException as req_err:
            print(f'Erreur HTTP: {req_err}')
        except Exception as e:
            print(f'Erreur inconnue {e}')

        with open(server_path + '/eula.txt', 'w') as f:
            f.write('eula=true')
        
        # properties
        with open(f'{server_path}/server.properties', 'w') as f:
            f.write(f'server-port={server_port}\nlevel-seed={server_seed}\nmax-players=20\nserver-ip=\nwhite-list=false\nenable-command-block=false\nenable-rcon=false\nrcon.password=\nrcon.port=25575\nmotd=A Minecraft Server\nlevel-name=world\nlevel-type=DEFAULT\ngenerator-settings=\nforce-gamemode=false\nhardcore=false\npvp=true\ndifficulty=1\nallow-flight=false\nspawn-npcs=true\nspawn-animals=true\nspawn-monsters=true\ngenerate-structures=true\nspawn-protection=16\nmax-tick-time=60000\nview-distance=10\nmax-build-height=256\nserver-ip=\nresource-pack=\nresource-pack-sha1=\nonline-mode=true\nallow-nether=true\nbroadcast-rcon-to-ops=true\nenable-query=false\nplayer-idle-timeout=0\nop-permission-level=4\nprevent-proxy-connections=false\nresource-pack=\nentity-broadcast-range-percentage=100\nplayer-sampling=12\nplayer-queue-depth=3\nforce-resources=false\nfunction-permission-level=2\nrequire-resource-pack=false\n')

        with open('commands.json', 'r') as f:
            commands = json.load(f)
        
        # on utilise la librairy subprocess pour lancer le serveur avec la commande trouvé dans le fichier commands.json selon le type de serveur
        command = commands[server_type][server_version]['install'] # java -jar install.jar --installServer
        result = subprocess.run(command, cwd=server_path, capture_output=True)
        print(result.stdout)
        print(result.stderr)

        # del install ?

        # renommer le fichier minecraft_server.*.*.*.jar en server.jar peux importe la fin
        path = os.path.join(server_path, 'minecraft_server.*.jar')
        files = glob.glob(path)
        if files:
            old_name = files[0]
            new_name = os.path.join(server_path, 'server.jar')
            os.rename(old_name, new_name)
            print(f"Renamed {old_name} to {new_name}")

        # # lancer le serveur avec les paramètres de ram
        # result = subprocess.run(['java', '-Xms' + server_ram_min,'G -Xmx' + server_ram_max,'G -jar', 'server.jar', 'nogui'], cwd=server_path, capture_output=True)
        # print(result.stdout) # a changer pour fonctionner avec le fichier de commandes.json
        #                     # en: to change to work with the commands.json file
        # print(result.stderr)
        # on sauvegarde les serveurs
        with open('servers.json', 'w') as f:
            json.dump(servers, f)
        return redirect('/server?name=' + server_name)
    return render_template('new-server.html')

@app.route('/server-info') # infos sur un serveur
@login_required
def servers_info():
    server_name = request.args.get('name')
    with open('servers.json', 'r') as f:
        servers = json.load(f)
    if server_name in servers:
        server = servers[server_name]
        # on récupère les infos du serveur
        server_dir = server['dir']
        server_ram_min = server['ramMin']
        server_ram_max = server['ramMax']
        server_port = server['port']
        server_type = server['type']
        server_version = server['version']
        server_status = 'inactive'
        
        for process in psutil.process_iter():
            if process.name() == 'java' and server_dir in process.cmdline():
                server_status = 'active'
                break
        server['status'] = server_status
        try:
            server['players'] = len(mcstatus.MinecraftServer('localhost', int(server_port)).status().players.sample)
            server['ip'] = mcstatus.MinecraftServer('localhost', int(server_port)).status().players.sample[0].name
            server['ramUsed'] = psutil.Process(process.pid).memory_info().rss / 1024 / 1024
        except Exception as e:
            server['players'] = 0
            server['ip'] = 'none'
            server['ramUsed'] = 0
        return jsonify(server)
    print('Server not found')
    return jsonify({'name': 'Server not found'})

def tail(file):
    with open(file) as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield f"data:{line}\n\n"
    
@app.route('/server-log_stream')
@login_required
def server_log(): # retourne un flux
    server_name = request.args.get("name")
    with open('servers.json') as j:
        servers = json.load(j)
    log_dir = servers[server_name]['log']
    return Response(tail(log_dir))

@app.route('/servers-ctrl') # controle d'un serveur
@login_required
def servers_ctrl():
    server_name = request.args.get('name')
    action = request.args.get('action')
    with open('servers.json', 'r') as f:
        servers = json.load(f)
    with open('commands.json', 'r') as f:
        commands = json.load(f)
    if server_name in servers:
        server = servers[server_name]
        server_dir = server['dir']
        server_ram_min = server['ramMin']
        server_ram_max = server['ramMax']
        server_port = server['port']
        server_type = server['type']
        server_version = server['version']
        if action == 'start':
            result = subprocess.run(commands[server_type][server_version]['start'], cwd=server_dir, capture_output=True)
            print(result.stdout)
            print(result.stderr)
        elif action == 'stop':
            try:
                with MCRcon('localhost', 25575, 'password') as mcr:
                    resp = mcr.command('stop')
                    print(resp)
            except Exception as e:
                print(e)
        elif action == 'restart':
            try:
                with MCRcon('localhost', 25575, 'password') as mcr:
                    resp = mcr.command('stop')
                    print(resp)
            except Exception as e:
                print(e)
            result = subprocess.run(commands[server_type][server_version]['start'], cwd=server_dir, capture_output=True)
            print(result.stdout)
            print(result.stderr)
        elif action == 'kill':
            for process in psutil.process_iter():
                if process.name() == 'java' and server_dir in process.cmdline():
                    process.kill()
                    break
        elif action == 'delete':
            os.remove(server_dir)
            del servers[server_name]
            with open('servers.json', 'w') as f:
                json.dump(servers, f)
        return jsonify({'status': 'ok'})
    print('Server not found')
    return jsonify({'status': 'error'})

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

@app.route('/server-versions') # retour des versions des serveurs
@login_required
def server_versions():
    # chargé le fichier json des versions
    with open('versions.json', 'r') as f: 
        versions = json.load(f)
    server_type = request.args.get('type')### ! a ameliorer (boucle)
    if server_type == 'vanilla':
        response = versions['vanilla']
    elif server_type == 'spigot':
        response = versions['spigot']
    elif server_type == 'paper':
        response = versions['paper']
    elif server_type == 'forge':
        response = versions['forge']
    elif server_type == 'fabric':
        response = versions['fabric']
    else:
        response = ['error']
    return jsonify(response)

@app.route('/main-serverinfo') # retour json de l'utilisation du disque dur, de la ram, du processeur, et de la bande passante
@login_required
def server_info():
    data = {
        'diskUsage': psutil.disk_usage('/').percent,
        'memUsage': psutil.virtual_memory().percent,
        'cpuUsage': psutil.cpu_percent(interval=1),
        'bandwidth': psutil.net_io_counters().packets_recv + psutil.net_io_counters().packets_sent
        #'totalBandwith':
    }
    return jsonify(data)

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

@app.route('/server')
@login_required
def server():
    return render_template('server.html')

@app.route('/servers')
@login_required
def servers():
    return render_template('servers.html')

@app.route('/settings')
@login_required
@role_required('root')
def settings():
    return render_template('settings.html')

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

@app.route('/users')
@login_required
@role_required('root')
def usersServe():
    return render_template('users.html')

@app.route('/users-ctl')
@login_required
@role_required('root')
def users_ctl():
    username = request.args.get('username')
    action = request.args.get('action')
    if action == 'get':
        users = {}
        for user in User.query.all():
            users[user.username] = {
                'role': user.role
            }
        return jsonify(users)
    elif action == 'add':
        password = request.args.get('password')
        role = request.args.get('role')
        user = User(username, password, role)
        db.session.add(user)
        db.session.commit()
        return jsonify({'status': 'ok'})
    elif action == 'delete':
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'ok'})
    elif action == 'modify':
        if request.args.get('role'):
            user = User.query.filter_by(username=username).first()
            user.role = request.args.get('role')
            db.session.commit()
            return jsonify({'status': 'ok'})
        # password avec post
        if request.args.get('password'): # to change to post for security
            user = User.query.filter_by(username=username).first()
            user.password = generate_password_hash(request.args.get('password'))
            db.session.commit()
            return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'})

@app.errorhandler(404)
@login_required
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
@login_required
def internal_server_error(error):
    return render_template('500.html'), 500

###### WebDav ######
with app.app_context():
    dav_provider =  FilesystemProvider(os.path.abspath(os.path.dirname(__file__)), readonly=False)
    UsersEligibled = User.query.filter_by(role='root').all()
    # user_mapping = {user.username: user.password for user in UsersEligibled}
    # print(user_mapping)
    # if not user_mapping:
    #     user_mapping = {"root": "root"}  # Utilisateur par défaut si aucun utilisateur n'est trouvé

    dav_app = WsgiDAVApp({
        "provider_mapping": {"/": dav_provider},
        "simple_dc": {
            "user_mapping": {"*": True} #user_mapping,
        },
        "http_authenticator": {
            "domain_controller": None,
            "accept_basic": True,
            "accept_digest": False,
            "default_to_digest": False
        },
        "dir_browser": {"enable": True},
        "verbose": 1
    })

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/webdav': dav_app
})

@app.route('/webdav')
@login_required
def webdav():
    return redirect('/webdav/')

'''
@app.route('/test') # test the code
def codeTester():
    server_name = 'test'
    path = os.path.join(server_name, 'minecraft_server.*.jar')
    files = glob.glob(path)
    if files:
        old_name = files[0]
        print(old_name)
        new_name = os.path.join(server_name, 'server.jar')
        print(new_name)
        os.rename(old_name, new_name)
        print(f"Renamed {old_name} to {new_name}")
'''

# with app.app_context():
#     for rule in app.url_map.iter_rules():
#         print(f" route : {rule.endpoint}, URL :{rule}")

if __name__ == '__main__':
    run_simple('0.0.0.0', 5000, app, use_reloader=True, use_debugger=True, use_evalex=True)
    # #demarrer le serveur flask
    # flask_server = WSGIServer(bind_addr=('0.0.0.0', 5000), wsgi_app=app)
    # flask_server.prepare()

    # #demarrer le serveur webdav
    # dav_server = WSGIServer(bind_addr=('0.0.0.0', 8080), wsgi_app=dav_app)
    # dav_server.prepare()

    # try:
    #     flask_server.start()
    #     dav_server.start()
    # except KeyboardInterrupt:
    #     flask_server.stop()
    #     dav_server.stop()
    #     print('Server stopped')
    #     exit(0)
    # except Exception as e:
    #     print(e)
    #     exit(1)