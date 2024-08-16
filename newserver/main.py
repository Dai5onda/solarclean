import multiprocessing
from flask_cors import CORS
from server import app
from ml_pipeline import run_ml_operations

def run_server():
    CORS(app)
    app.run(host='192.168.112.118', port=5050)

if __name__ == '__main__':
    print("Starting server and ML processes...")
    server_process = multiprocessing.Process(target=run_server)
    ml_process = multiprocessing.Process(target=run_ml_operations)

    server_process.start()
    ml_process.start()

    print("Server and ML processes started")

    server_process.join()
    ml_process.join()