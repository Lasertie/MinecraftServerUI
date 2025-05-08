from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file, Response
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

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Utility to load/save JSON files ---
JSON_DIR = os.path.abspath(os.path.dirname(__file__))
SERVERS_FILE = os.path.join(JSON_DIR, 'servers.json')
VERSIONS_FILE = os.path.join(JSON_DIR, 'versions.json')
COMMANDS_FILE = os.path.join(JSON_DIR, 'commands.json')
SETTINGS_FILE = os.path.join(JSON_DIR, 'settings.json')


def load_json(path):
    if not os.path.isfile(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/favicon.ico') # retour de l'icone
def favicon():
    return send_file('favicon.ico')

@app.route('/css/style.css') # retour du fichiers css
def send_css():
    return send_file('templates/css/style.css')

@app.route('/js/script.js') # retour du fichiers js
#@login_required
def send_js():
    return send_file('templates/js/script.js')

@app.route('/') # retour de la page d'accueil
# @login_required
def home():
    return render_template('index.html')

# --- Server creation ---
@app.route('/new-server')
def new_server():
    if request.method == 'GET' and request.args.get('serverName'):
        data = request.args
        name = data.get('serverName')
        # defaults
        cfg = {
            'type': data.get('serverType'),
            'version': data.get('serverVersion'),
            'ramMin': data.get('serverRamMin', '1G'),
            'ramMax': data.get('serverRamMax', '2G'),
            'port': data.get('serverPort', '25565'),
            'seed': data.get('serverSeed', ''),
            'maxPlayers': data.get('serverMaxPlayers', '20'),
            'dir': os.path.join('servers', name)
        }
        servers = load_json(SERVERS_FILE)
        servers[name] = cfg
        save_json(SERVERS_FILE, servers)

        os.makedirs(cfg['dir'], exist_ok=True)
        versions = load_json(VERSIONS_FILE)
        url = versions[cfg['type']][cfg['version']]
        jar_path = os.path.join(cfg['dir'], 'install.jar')
        # download server jar
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(jar_path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
        # eula
        with open(os.path.join(cfg['dir'], 'eula.txt'), 'w') as f:
            f.write('eula=true')
        # server.properties
        props = [
            f"server-port={cfg['port']}",
            f"level-seed={cfg['seed']}",
            f"max-players={cfg['maxPlayers']}"
        ]
        with open(os.path.join(cfg['dir'], 'server.properties'), 'w') as f:
            f.write("\n".join(props))
        # install server
        commands = load_json(COMMANDS_FILE)
        cmd = commands[cfg['type']][cfg['version']]['install']
        subprocess.run(cmd, cwd=cfg['dir'], capture_output=True)
        # rename jar
        files = glob.glob(os.path.join(cfg['dir'], 'minecraft_server.*.jar'))
        if files:
            os.rename(files[0], os.path.join(cfg['dir'], 'server.jar'))
        return redirect(f"/server?name={name}")
    return render_template('new-server.html')


# --- Server info endpoints ---
@app.route('/server-info')
def server_info():
    name = request.args.get('name')
    servers = load_json(SERVERS_FILE)
    if name not in servers:
        return jsonify({'error': 'Server not found'}), 404
    cfg = servers[name]
    info = {}
    # status
    info['status'] = 'inactive'
    for p in psutil.process_iter():
        if p.name() == 'java' and cfg['dir'] in p.cmdline():
            info['status'] = 'active'
            info['ramUsed'] = psutil.Process(p.pid).memory_info().rss / (1024**2)
            break
    # players
    try:
        status = mcstatus.MinecraftServer('localhost', int(cfg['port'])).status()
        info['players'] = status.players.online
    except:
        info['players'] = 0
    return jsonify(info)

@app.route('/servers-data')
def servers_data():
    servers = load_json(SERVERS_FILE)
    for name, cfg in servers.items():
        cfg['status'] = 'inactive'
        for p in psutil.process_iter():
            if p.name() == 'java' and cfg['dir'] in p.cmdline():
                cfg['status'] = 'active'
                break
        try:
            cfg['players'] = mcstatus.MinecraftServer('localhost', int(cfg['port'])).status().players.online
        except:
            cfg['players'] = 0
    return jsonify(servers)


# --- Control actions ---
@app.route('/servers-ctrl')
def servers_ctrl():
    name = request.args.get('name')
    action = request.args.get('action')
    servers = load_json(SERVERS_FILE)
    commands = load_json(COMMANDS_FILE)
    if name not in servers:
        return jsonify({'error': 'Server not found'}), 404
    cfg = servers[name]
    if action == 'start':
        subprocess.run(commands[cfg['type']][cfg['version']]['start'], cwd=cfg['dir'])
    elif action == 'stop':
        with MCRcon('localhost', 25575, 'password') as mcr:
            mcr.command('stop')
    elif action == 'kill':
        for p in psutil.process_iter():
            if p.name() == 'java' and cfg['dir'] in p.cmdline():
                p.kill()
                break
    elif action == 'delete':
        shutil.rmtree(cfg['dir'], ignore_errors=True)
        del servers[name]
        save_json(SERVERS_FILE, servers)
    return jsonify({'status': 'ok'})


# --- System metrics ---
@app.route('/main-serverinfo')
def main_serverinfo():
    return jsonify({
        'diskUsage': psutil.disk_usage('/').percent,
        'memUsage': psutil.virtual_memory().percent,
        'cpuUsage': psutil.cpu_percent(interval=1),
        'bandwidth': psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
    })


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

# --- WebDAV setup ---
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
def webdav():
    return redirect('/webdav/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
