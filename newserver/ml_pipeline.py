import os
import time
import cv2
from tinydb import TinyDB, Query, where
from datetime import datetime
from itertools import groupby

ORIGINAL_DB_PATH ='db.json'
PROCESSED_DB_PATH = 'processed_image_metadata.json'
ORIGINAL_UPLOAD_FOLDER = 'storage/originalimage'
PROCESSED_UPLOAD_FOLDER = 'storage/processedimage'

# Ensure the processed upload folder exists
os.makedirs(PROCESSED_UPLOAD_FOLDER, exist_ok=True)

# Initialize the databases
original_db = TinyDB(ORIGINAL_DB_PATH)
processed_db = TinyDB(PROCESSED_DB_PATH)
metadata_table = original_db.table('metadata')
processed_table = processed_db.table('processed_metadata')

def process_image(image_path):
    print(f"Attempting to process image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: File does not exist: {image_path}")
        return None

    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Failed to read image: {image_path}")
            return None
        
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return gray_img
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")
        return None

def save_processed_image(processed_image, output_path):
    cv2.imwrite(output_path, processed_image)

def process_new_images():
    time.sleep(0.5)  # Wait for 0.5 seconds to allow new inserts to complete
    print("Resetting inconsistent batch_processing flags...")
    metadata_table.update({'batch_processing': False}, (Query().processed == False) & (Query().batch_processing == True))
    print("Checking for unprocessed images...")
    
    all_images = metadata_table.all()
    print(f"Total images in metadata_table: {len(all_images)}")
    
    unprocessed = metadata_table.search(where('processed') == False)
    not_batch_processing = metadata_table.search(where('batch_processing') == False)
    
    print(f"Images with processed == False: {len(unprocessed)}")
    print(f"Images with batch_processing == False: {len(not_batch_processing)}")
    
    # Let's check the individual conditions
    print("\nImages with processed == False:")
    for img in unprocessed:
        print(f"  - {img['filename']} (Batch ID: {img['batch_id']}, processed: {img['processed']}, batch_processing: {img['batch_processing']})")
    
    print("\nImages with batch_processing == False:")
    for img in not_batch_processing:
        print(f"  - {img['filename']} (Batch ID: {img['batch_id']}, processed: {img['processed']}, batch_processing: {img['batch_processing']})")
    
    # Now, let's try a different way to combine the queries
    unprocessed_images = [img for img in all_images if img.get('processed') == False and img.get('batch_processing') == False]
    print(f"\nFound {len(unprocessed_images)} unprocessed images using list comprehension")
    
    if not unprocessed_images:
        print("No new images to process")
        return
    
    print("Unprocessed images:")
    for img in unprocessed_images:
        print(f"  - {img['filename']} (Batch ID: {img['batch_id']}, processed: {img['processed']}, batch_processing: {img['batch_processing']})")
    
    # Group images by batch_id
    for batch_id, batch_images in groupby(unprocessed_images, key=lambda x: x['batch_id']):
        batch_images = list(batch_images)
        print(f"Processing batch {batch_id} with {len(batch_images)} images")
        
        # Mark batch as processing
        metadata_table.update({'batch_processing': True}, Query().batch_id == batch_id)
        
        for image_data in batch_images:
            original_path = image_data['path']
            filename = image_data['filename']
            
            # Process the image
            processed_image = process_image(original_path)
            if processed_image is None:
                print(f"Skipping image due to processing error: {filename}")
                continue
            
            # Save the processed image
            processed_filename = f"processed_{filename}"
            processed_path = os.path.join(PROCESSED_UPLOAD_FOLDER, processed_filename)
            save_processed_image(processed_image, processed_path)
            
            # Store metadata for processed image in the new database
            processed_table.insert({
                'original_filename': filename,
                'processed_filename': processed_filename,
                'original_path': original_path,
                'processed_path': processed_path,
                'batch_id': batch_id,
                'processing_time': datetime.now().isoformat()
            })
            
            # Update the original metadata to mark as processed
            metadata_table.update({'processed': True, 'batch_processing': False}, Query().filename == filename)
        
        print(f"Finished processing batch {batch_id}")
        
        # Only process one batch per function call
        break

def run_ml_operations():
    print("Starting ML pipeline monitor...")
    while True:
        print("Checking for new images...")
        try:
            process_new_images()
        except Exception as e:
            print(f"Error in ML pipeline: {str(e)}")
        time.sleep(2)  # Wait for 2 seconds before checking again