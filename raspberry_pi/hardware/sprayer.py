import RPi.GPIO as GPIO
from config import SPRAYER_PIN

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPRAYER_PIN, GPIO.OUT)

def cleanup():
    GPIO.cleanup()

# Add sprayer control functions here
