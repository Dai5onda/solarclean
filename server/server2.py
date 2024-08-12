from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
from datetime import datetime
import requests
import os

app = Flask(__name__)

# Initialize the database
db = TinyDB('data.json')
state_table = db.table('state')
images_table = db.table('images')
logs_table = db.table('logs')
commands_table = db.table('commands')

# Raspberry Pi URL
raspberry_pi_url = "http://192.168.112.101:8080/command"

def add_command(command):
    command_id = commands_table.insert({'command': command, 'timestamp': datetime.now().isoformat(), 'status': 'pending'})
    try:
        response = requests.post(raspberry_pi_url, json={"command": command, "command_id": command_id})
        print("Command sent to Raspberry Pi:", response.json())
    except requests.RequestException as e:
        print(f"Error sending command to Raspberry Pi: {e}")
        commands_table.update({'status': 'failed'}, doc_ids=[command_id])

@app.route('/state', methods=['POST'])
def receive_state():
    state_data = request.json
    current_state = state_data.get('current_state')
    state_table.upsert({'current_state': current_state, 'timestamp': datetime.now().isoformat()}, Query().current_state.exists())
    return jsonify({"status": "received"})

@app.route('/image', methods=['POST'])
def receive_image():
    image_data = request.files['image']
    metadata = request.form.to_dict()
    timestamp = datetime.now().isoformat()
    image_dir = 'images'
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, f'image_{timestamp}.jpg')
    image_data.save(image_path)
    images_table.insert({'path': image_path, 'timestamp': timestamp, 'metadata': metadata})
    return jsonify({"status": "received"})

@app.route('/logs', methods=['POST'])
def receive_log():
    log_data = request.json
    timestamp = datetime.now().isoformat()
    logs_table.insert({'timestamp': timestamp, 'message': log_data['message']})
    return jsonify({"status": "received"})

@app.route('/command', methods=['POST'])
def send_command():
    command_data = request.json
    command = command_data.get('command')
    add_command(command)
    return jsonify({"status": "command received"})

@app.route('/command_status', methods=['POST'])
def update_command_status():
    data = request.json
    command_id = data.get('command_id')
    status = data.get('status')
    if command_id and status:
        commands_table.update({'status': status}, doc_ids=[command_id])
        return jsonify({"status": "updated"})
    return jsonify({"status": "error", "message": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
