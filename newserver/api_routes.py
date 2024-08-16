from flask import Blueprint, jsonify, request
from tinydb import TinyDB, Query
from datetime import datetime
import json
import os
import logging
import requests

api = Blueprint('api', __name__)

# Initialize the database
db = TinyDB('db.json')
dashboard_table = db.table('dashboard')
schedule_table = db.table('schedule')
ml_output_table = db.table('ml_output')

# Add this constant at the top of the file, after the imports
RASPBERRY_PI_URL = "http://192.168.112.106:8082/execute_command"

@api.route('/dashboard', methods=['GET'])
def get_dashboard():
    dashboard_data = dashboard_table.all()
    if dashboard_data:
        return jsonify(dashboard_data[0]), 200
    return jsonify({"error": "Dashboard data not found"}), 404

@api.route('/cleaner/toggle', methods=['POST'])
def toggle_cleaner():
    data = request.json
    new_state = data.get('state')
    if new_state is None:
        return jsonify({"error": "State not provided"}), 400
    
    dashboard_table.update({'isCleanerOn': new_state})
    
    # Send command to Raspberry Pi
    try:
        response = requests.post(RASPBERRY_PI_URL, json={"command": "ON" if new_state else "OFF"})
        if response.status_code == 200:
            return jsonify({"success": True, "newState": new_state}), 200
        else:
            return jsonify({"error": "Failed to send command to Raspberry Pi"}), 500
    except requests.RequestException as e:
        return jsonify({"error": f"Error communicating with Raspberry Pi: {str(e)}"}), 500

@api.route('/cleaner/active', methods=['POST'])
def toggle_active():
    data = request.json
    new_active_state = data.get('active')
    if new_active_state is None:
        return jsonify({"error": "Active state not provided"}), 400
    
    dashboard_table.update({'isActive': new_active_state})
    return jsonify({"success": True, "newActiveState": new_active_state}), 200

@api.route('/batches', methods=['GET'])
def get_batches():
    try:
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')
        batches_per_page = 5

        # Load the processed metadata
        with open('processed_image_metadata.json', 'r') as f:
            processed_data = json.load(f)['processed_metadata']
        
        # Group images by batch_id
        batches = {}
        for image_id, image_data in processed_data.items():
            batch_id = str(image_data['batch_id'])
            if batch_id not in batches:
                batch_name = f"Batch {batch_id}"
                batch_date = datetime.strptime(image_data['processing_time'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d")
                if search.lower() in batch_name.lower() or search.lower() in batch_date.lower():
                    batches[batch_id] = {
                        'id': batch_id,
                        'name': batch_name,
                        'date': batch_date,
                        'damageCount': 0,
                        'images': []
                    }
            
            if batch_id in batches:
                # Add image to batch
                batches[batch_id]['images'].append({
                    'id': image_id,
                    'url': f"http://192.168.112.118:5050/images/{os.path.basename(image_data['processed_path'])}",
                    'damageCount': 0  # You'll need to add this information to your processed metadata
                })
                # Update batch damage count
                batches[batch_id]['damageCount'] += 0  # Update this when you have actual damage count data

        # Convert batches dict to list and sort by date (newest first)
        batches_list = sorted(batches.values(), key=lambda x: x['date'], reverse=True)
        
        # Calculate total count and paginate
        total_count = len(batches_list)
        start_index = (page - 1) * batches_per_page
        end_index = start_index + batches_per_page
        paginated_batches = batches_list[start_index:end_index]

        # Prepare the response
        response = {
            'batches': paginated_batches,
            'totalCount': total_count
        }
        
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in get_batches: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api.route('/schedule', methods=['GET'])
def get_schedule():
    schedule = schedule_table.all()
    return jsonify(schedule), 200

@api.route('/schedule', methods=['PUT'])
def update_schedule():
    new_schedule = request.json
    schedule_table.truncate()
    schedule_table.insert_multiple(new_schedule)
    return jsonify({"success": True, "updatedSchedule": new_schedule}), 200

@api.route('/schedule/<int:index>', methods=['DELETE'])
def delete_schedule_item(index):
    schedule = schedule_table.all()
    if 0 <= index < len(schedule):
        del schedule[index]
        schedule_table.truncate()
        schedule_table.insert_multiple(schedule)
        return jsonify({"success": True}), 200
    return jsonify({"error": "Invalid index"}), 400

@api.route('/schedule', methods=['POST'])
def add_schedule_item():
    new_item = request.json
    schedule_table.insert(new_item)
    return jsonify({"success": True, "newScheduleItem": new_item}), 200