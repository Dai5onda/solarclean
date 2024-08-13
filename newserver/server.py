import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from tinydb import TinyDB, Query
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'storage/originalimage'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
DB_PATH = 'db.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = TinyDB(DB_PATH)
metadata_table = db.table('metadata')
config_table = db.table('config')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_next_batch_id():
    config = config_table.get(Query().key == 'batch_id')
    if config:
        next_id = config['value'] + 1
        config_table.update({'value': next_id}, Query().key == 'batch_id')
    else:
        next_id = 1
        config_table.insert({'key': 'batch_id', 'value': next_id})
    return next_id

@app.route('/upload_batch', methods=['POST'])
def upload_batch():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('files')
    batch_id = get_next_batch_id()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    uploaded_files = []
    for index, file in enumerate(files):
        if file and allowed_file(file.filename):
            filename = secure_filename(f"batch{batch_id}_{timestamp}_{index + 1}.jpg")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            metadata = {
                'filename': filename,
                'original_name': file.filename,
                'path': file_path,
                'batch_id': batch_id,
                'upload_time': datetime.now().isoformat(),
                'processed': False,
                'batch_processing': False
            }
            metadata_table.insert(metadata)
            print(f"Inserted metadata: {metadata}")
            
            # Verify the insert
            inserted = metadata_table.get((Query().filename == filename) & (Query().batch_id == batch_id))
            print(f"Verified inserted metadata: {inserted}")
            
            uploaded_files.append(filename)
    
    return jsonify({
        "message": f"Successfully uploaded {len(uploaded_files)} files",
        "batch_id": batch_id,
        "files": uploaded_files
    }), 200