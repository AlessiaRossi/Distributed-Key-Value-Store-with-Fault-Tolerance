from flask import request, jsonify
from functools import wraps
from .models import ReplicaNode

API_TOKEN = "your_api_token_here"  # Sostituisci con un token sicuro

# Esempio con 3 repliche, ognuna con una porta specifica
nodes = [
    ReplicaNode(0, 5001),
    ReplicaNode(1, 5002),
    ReplicaNode(2, 5003)
]

def require_api_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('Authorization') != f"Bearer {API_TOKEN}":
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid API token'}), 403
        return f(*args, **kwargs)
    return decorated_function

def write_to_replicas(key, value):
    for node in nodes:
        node.write(key, value)

def read_from_replicas(key):
    for node in nodes:
        if node.is_alive():
            result = node.read(key)
            if result is not None:
                return {'value': result, 'message': f'Read from replica {node.node_id}'}
    return {'value': None, 'message': 'All replicas failed or key not found'}

def delete_from_replicas(key):
    for node in nodes:
        node.delete(key)

def key_exists_in_replicas(key):
    for node in nodes:
        if node.is_alive() and node.key_exists(key):
            return True
    return False

def register_routes(app):
    @app.route('/write', methods=['POST'])
    @require_api_token
    def write():
        data = request.json
        if 'key' not in data or 'value' not in data:
            return jsonify({'error': 'Invalid input', 'message': 'Key and value are required'}), 400
        key = data['key']
        value = data['value']
        try:
            if key_exists_in_replicas(key):
                return jsonify({'error': 'Key already exists', 'message': f'The key {key} already exists'}), 409
            write_to_replicas(key, value)
            return jsonify({'status': 'success', 'message': f'Key {key} written successfully'})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    @app.route('/read/<key>', methods=['GET'])
    @require_api_token
    def read(key):
        try:
            result = read_from_replicas(key)
            if result['value'] is not None:
                return jsonify({'key': key, 'value': result['value'], 'message': result['message'], 'status': 'success'})
            else:
                return jsonify({'error': 'Key not found', 'message': result['message']}), 404
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    @app.route('/delete/<key>', methods=['DELETE'])
    @require_api_token
    def delete(key):
        try:
            if not key_exists_in_replicas(key):
                return jsonify({'error': 'Key not found', 'message': 'Key does not exist'}), 404
            delete_from_replicas(key)
            return jsonify({'status': 'success', 'message': f'Key {key} deleted successfully'})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    @app.route('/fail/<int:node_id>', methods=['POST'])
    @require_api_token
    def fail_node(node_id):
        if 0 <= node_id < len(nodes):
            try:
                nodes[node_id].fail()
                return jsonify({'status': 'success', 'message': f'Node {node_id} failed'})
            except Exception as e:
                return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
        else:
            return jsonify({'error': 'Invalid node ID', 'message': 'Node ID must be between 0 and the number of nodes'}), 400

    @app.route('/recover/<int:node_id>', methods=['POST'])
    @require_api_token
    def recover_node(node_id):
        if 0 <= node_id < len(nodes):
            try:
                nodes[node_id].recover(nodes)
                return jsonify({'status': 'success', 'message': f'Node {node_id} recovered'})
            except Exception as e:
                return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
        else:
            return jsonify({'error': 'Invalid node ID', 'message': 'Node ID must be between 0 and the number of nodes'}), 400

    @app.route('/nodes', methods=['GET'])
    @require_api_token
    def get_nodes():
        try:
            nodes_status = [
                {
                    'node_id': node.node_id,
                    'status': 'alive' if node.is_alive() else 'dead',
                    'port': node.port
                }
                for node in nodes
            ]
            return jsonify({'status': 'success', 'nodes': nodes_status})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
