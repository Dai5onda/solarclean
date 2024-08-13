from tinydb import TinyDB
import os

# Define the path to the database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'solar_cell_data.json')

# Create a database instance
db = TinyDB(DB_PATH)

def get_db():
    """
    Returns the database instance.
    """
    return db

# You can define tables here if you need them
images_table = db.table('images')

def get_images_table():
    """
    Returns the images table.
    """
    return images_table