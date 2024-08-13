import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Blueprint, request, jsonify
from local_server.services.image_processing_service import ImageProcessingService
from local_server.API.models import ImageModel
import io

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

# Simulation function
def simulate_process_images():
    # Create mock image files
    mock_images = [
        ('image1.jpg', io.BytesIO(b'fake image data 1')),
        ('image2.png', io.BytesIO(b'fake image data 2')),
        ('image3.jpg', io.BytesIO(b'fake image data 3'))
    ]

    # Simulate the request.files.getlist('images')
    class MockFileStorage:
        def __init__(self, filename, stream):
            self.filename = filename
            self.stream = stream

    image_files = [MockFileStorage(name, stream) for name, stream in mock_images]

    # Process the images
    processed_images = image_service.process_batch(image_files)

    # Print the results
    print(f"Processed {len(processed_images)} images:")
    for img in processed_images:
        print(f"- {img.filename}: {img.status}")

# Run the simulation
if __name__ == '__main__':
    simulate_process_images()