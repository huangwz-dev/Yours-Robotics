from flask import Flask, jsonify
from flask_cors import CORS
from data_processor import load_and_process_data
import os

app = Flask(__name__)
CORS(app)

# Load data on startup
fleet_data = None

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    if fleet_data is None:
        return jsonify({'error': 'Data not loaded'}), 503
    return jsonify(fleet_data)

@app.route('/api/robot/<robot_id>', methods=['GET'])
def get_robot(robot_id):
    if fleet_data is None:
        return jsonify({'error': 'Data not loaded'}), 503
    
    for robot in fleet_data.get('robots', []):
        if robot['id'] == robot_id:
            return jsonify(robot)
    
    return jsonify({'error': 'Robot not found'}), 404

def startup():
    global fleet_data
    try:
        print('Loading data files...')
        fleet_data = load_and_process_data()
        print('Data loaded successfully')
        print(f"Loaded {fleet_data['summary']['totalRobots']} robots")
    except Exception as e:
        print(f'Failed to load data: {e}')
        raise

if __name__ == '__main__':
    startup()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
