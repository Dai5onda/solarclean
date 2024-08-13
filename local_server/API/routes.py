from flask import Blueprint, request, jsonify
from local_server.services.image_processing_service import ImageProcessingService
from local_server.API.models import ImageModel

api = Blueprint('api', __name__)
image_service = ImageProcessingService()

@api.route('/process_images', methods=['POST'])
def process_images():
    if 'images' not in request.files:
        return jsonify({'error': 'No images in the request'}), 400
    
    image_files = request.files.getlist('images')
    processed_images = image_service.process_batch(image_files)
    
    return jsonify([img.dict() for img in processed_images]), 200

@api.route('/images', methods=['GET'])
def get_images():
    images = image_service.retrieve_images()
    return jsonify([img.dict() for img in images]), 200
