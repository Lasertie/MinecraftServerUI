from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, abort, send_file, send_from_directory
import psutil
import json
import os
import subprocess
import requests
import mcstatus
from mcrcon import MCRcon
import glob

app = Flask(__name__)

@app.route('/favicon.ico') # retour de l'icone
def favicon():
    return send_file('favicon.ico')

@app.route('/css/style.css') # retour du fichiers css
def send_css():
    return send_file('templates/css/style.css')

@app.route('/js/script.js') # retour du fichiers js
def send_js():
    return send_file('templates/js/script.js')

@app.route('/') # retour de la page d'accueil
def home():
    return render_template('index.html')

@app.route('/new-server')
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
        # si le port est spécifié on le récupère
        if request.args.get('serverPort'):
            server_port = request.args.get('serverPort')
        else:
            server_port = '25565'
        # si le seed est spécifié on le récupère
        if request.args.get('serverSeed'):
            server_seed = request.args.get('serverSeed')
        else:
            server_seed = ''
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
            'dir': server_path
        }

        # Chemin du dossier du serveur
        server_path = f'servers/{server_name}'
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
        
        # on utilise la librairie subprocess pour lancer le serveur avec la commande trouvé dans le fichier commands.json selon le type de serveur
        command = commands[server_type][server_version]['install'] # ex pour forge: java -jar server.jar --installServer
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

        # lancer le serveur avec les paramètres de ram
        result = subprocess.run(['java', '-Xms' + server_ram_min,'G -Xmx' + server_ram_max,'G -jar', 'server.jar', 'nogui'], cwd=server_path, capture_output=True)
        print(result.stdout) # a changer pour fonctionner avec le fichier de commandes.json
                            # en: to change to work with the commands.json file
        print(result.stderr)
        # on sauvegarde les serveurs
        with open('servers.json', 'w') as f:
            json.dump(servers, f)
        return redirect('/server?name=' + server_name)
    return render_template('new-server.html')

@app.route('/servers-info') # infos sur un serveur
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

@app.route('/servers-ctrl') # controle d'un serveur
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
        return jsonify({'status': 'ok'})
    print('Server not found')
    return jsonify({'status': 'error'})

@app.route('/server-versions') # retour des versions des serveurs
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

@app.route('/server-info') # retour json de l'utilisation du disque dur, de la ram, du processeur, et de la bande passante
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
def servers_data():
    return send_file('servers.json')

@app.route('/server')
def server():
    return render_template('server.html')

@app.route('/servers')
def servers():
    return render_template('servers.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

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
if __name__ == '__main__':
    app.run(debug=True)