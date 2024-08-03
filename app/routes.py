from flask import request, jsonify
from functools import wraps
from .models import ReplicationManager

API_TOKEN = "your_api_token_here"  # Replace with a secure token

# Initialize the replication manager with a replication factor of 3
replication_manager = ReplicationManager(replication_factor=3)

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
