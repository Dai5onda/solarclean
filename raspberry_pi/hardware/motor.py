import RPi.GPIO as GPIO
from config import MOTOR_PIN_1, MOTOR_PIN_2

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTOR_PIN_1, GPIO.OUT)
    GPIO.setup(MOTOR_PIN_2, GPIO.OUT)

def cleanup():
    GPIO.cleanup()