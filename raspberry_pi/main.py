from hardware import motor, sprayer, camera
from network import communication
import config

def main():
    # Setup hardware
    motor.setup()
    sprayer.setup()
    cam = camera.setup()

    # Setup network
    communication.setup_connection()

    # Main application logic here
    # ...

    # Cleanup
    motor.cleanup()
    sprayer.cleanup()

if __name__ == "__main__":
    main()
