from flask import Flask, request, Response, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    command = data.get('command', '')
    print(command)
    response = "\n"#f"Commande reçue: {command}"
    return {'response': response}

@app.route('/stream')
def stream():
    def event_stream():
        # Ici, vous pouvez ajouter la logique pour envoyer des mises à jour en continu
        # Par exemple, lire la sortie d'un processus et l'envoyer au client
        import time
        while True:
            time.sleep(1)
            yield 'data:'

    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
