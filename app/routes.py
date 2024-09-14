from flask import request, jsonify
from functools import wraps
from .models import ReplicationManager
import json
import os

# Function to load configuration values from a JSON file
def load_config(file_path, default_config=None):
    if default_config is None:
        default_config = {
            "replication_factor": 3,  # Default replication factor
            "API_TOKEN": "your_api_token_here"  # Default API token (replace with a secure value)
        }
    
    # If the file doesn't exist, create the directory and file with default values
    if not os.path.exists(file_path):
        dir_name = os.path.dirname(file_path)
        # Create the directory if it doesn't exist
        if not os.path.exists(dir_name) and dir_name != '':
            os.makedirs(dir_name)
        # Write the default values into the JSON file
        with open(file_path, 'w') as f:
            json.dump(default_config, f)
        return default_config
    
    # If the file exists, load the values from the JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Return the merged configuration (file + defaults for missing values)
            return {**default_config, **data}
    except (json.JSONDecodeError, KeyError):
        # If the JSON file is corrupted or doesn't contain the correct values, return the default config
        return default_config

# Path to the JSON configuration file
file_path = 'config/config.json'

# Load the entire configuration (replication factor and API token)
config = load_config(file_path)

# Extract specific values from the configuration
replication_factor = config.get('replication_factor')
API_TOKEN = config.get('API_TOKEN')

# Initialize the replication manager with the replication factor from the file
replication_manager = ReplicationManager(replication_factor=replication_factor)

# Decorator to require a valid API token
def require_api_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('Authorization') != f"Bearer {API_TOKEN}":
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid API token'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Function to register the routes with the Flask app
def register_routes(app):

    # Route for writing data
    @app.route('/write', methods=['POST'])
    @require_api_token
    def write():
        data = request.json
        if 'key' not in data or 'value' not in data:
            return jsonify({'error': 'Invalid input', 'message': 'Key and value are required'}), 400
        key = data['key']
        value = data['value']
        try:
            if replication_manager.key_exists_in_replicas(key):
                return jsonify({'error': 'Key already exists', 'message': f'The key {key} already exists'}), 409
            replication_manager.write_to_replicas(key, value)
            return jsonify({'status': 'success', 'message': f'Key {key} written successfully'})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route for reading data
    @app.route('/read/<key>', methods=['GET'])
    @require_api_token
    def read(key):
        try:
            result = replication_manager.read_from_replicas(key)
            if result['value'] is not None:
                return jsonify({'key': key, 'value': result['value'], 'message': result['message'], 'status': 'success'})
            else:
                return jsonify({'error': 'Key not found', 'message': result['message']}), 404
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route for deleting data
    @app.route('/delete/<key>', methods=['DELETE'])
    @require_api_token
    def delete(key):
        try:
            if not replication_manager.key_exists_in_replicas(key):
                return jsonify({'error': 'Key not found', 'message': 'Key does not exist'}), 404
            replication_manager.delete_from_replicas(key)
            return jsonify({'status': 'success', 'message': f'Key {key} deleted successfully'})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route for failing a node
    @app.route('/fail/<int:node_id>', methods=['POST'])
    @require_api_token
    def fail_node(node_id):
        try:
            replication_manager.fail_node(node_id)
            return jsonify({'status': 'success', 'message': f'Node {node_id} failed'})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route for recovering a node
    @app.route('/recover/<int:node_id>', methods=['POST'])
    @require_api_token
    def recover_node(node_id):
       try:
            replication_manager.recover_node(node_id)
            return jsonify({'status': 'success', 'message': f'Node {node_id} recovered'})
       except Exception as e:
           return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route for getting the status of all nodes
    @app.route('/nodes', methods=['GET'])
    @require_api_token
    def get_nodes():
        try:
            nodes_status = replication_manager.get_nodes_status()
            return jsonify({'status': 'success', 'nodes': nodes_status})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route for setting the replication strategy
    @app.route('/set_replication_strategy', methods=['POST'])
    @require_api_token
    def set_replication_strategy():
        data = request.json
        if 'strategy' not in data:
            return jsonify({'error': 'Invalid input', 'message': 'Replication strategy is required'}), 400
        strategy = data.get('strategy')
        replication_factor = data.get('replication_factor', replication_manager.replication_factor)
        try:
            replication_manager.set_replication_strategy(strategy, replication_factor)
            return jsonify({'status': 'success',
                            'message': f'Replication strategy set to {strategy} with factor {replication_factor}'})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route for getting the nodes responsible for a key
    @app.route('/nodes_for_key/<key>', methods=['GET'])
    @require_api_token
    def nodes_for_key(key):
        try:
            nodes = replication_manager.get_nodes_for_key(key)
            if nodes:
                return jsonify({'status': 'success', 'nodes': nodes})
            else:
                return jsonify({'error': 'Invalid strategy', 'message': 'Consistent hashing is not enabled'}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500