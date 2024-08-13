from picamera import PiCamera
from config import CAMERA_RESOLUTION

def setup():
    camera = PiCamera()
    camera.resolution = CAMERA_RESOLUTION
    return camera

# Add camera control functions here
