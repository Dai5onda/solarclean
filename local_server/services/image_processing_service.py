import os
from PIL import Image
from local_server.database.db import get_images_table
from local_server.API.models import ImageModel

class ImageProcessingService:
    def __init__(self):
        self.images_table = get_images_table()
        self.original_images_path = 'storage/original_images/'
        self.processed_images_path = 'storage/processed_images/'

    def process_batch(self, image_files):
        processed_images = []
        for image_file in image_files:
            original_path = self.save_original_image(image_file)
            processed_path = self.process_image(original_path)
            image_data = self.store_image_data(original_path, processed_path)
            processed_images.append(image_data)
        return processed_images

    def save_original_image(self, image_file):
        filename = image_file.filename
        path = os.path.join(self.original_images_path, filename)
        image_file.save(path)
        return path

    def process_image(self, original_path):
        # Placeholder for ML/AI processing
        # For now, we'll just create a copy in the processed folder
        filename = os.path.basename(original_path)
        processed_path = os.path.join(self.processed_images_path, f"processed_{filename}")
        Image.open(original_path).save(processed_path)
        return processed_path

    def store_image_data(self, original_path, processed_path):
        image_data = {
            'original_path': original_path,
            'processed_path': processed_path,
            'status': 'processed'
        }
        image_id = self.images_table.insert(image_data)
        return ImageModel(id=image_id, **image_data)

    def retrieve_images(self, query=None):
        if query:
            results = self.images_table.search(query)
        else:
            results = self.images_table.all()
        return [ImageModel(id=item.doc_id, **item) for item in results]
