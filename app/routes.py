from flask import request, jsonify
from functools import wraps
from .models import ReplicationManager
import json
import os

# Definisce i valori di configurazione predefiniti.
nodes_db = 3
port = 5000
API_TOKEN = "your_api_token_here"

# Decorator per richiedere un token API valido.
def require_api_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('Authorization') != f"Bearer {API_TOKEN}":
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid API token'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Funzione per registrare le routes con l'app Flask
def register_routes(app, config):

    # Estrai valori specifici dalla configurazione.
    global nodes_db
    global port
    global API_TOKEN

    nodes_db = config.get('nodes_db')
    port = config.get('port')
    API_TOKEN = config.get('API_TOKEN')

    # Inizializza il gestore della replica con il fattore di replica dal file.
    replication_manager = ReplicationManager(nodes_db=nodes_db, port=port)

    # Route per scrivere i dati.
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

    # Route per leggere i dati
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

    # Route per eliminare dati.
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

    # Route per far fallire un nodo.
    @app.route('/fail/<int:node_id>', methods=['POST'])
    @require_api_token
    def fail_node(node_id):
        try:
            replication_manager.fail_node(node_id)
            return jsonify({'status': 'success', 'message': f'Node {node_id} failed'})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route per recuperare un nodo.
    @app.route('/recover/<int:node_id>', methods=['POST'])
    @require_api_token
    def recover_node(node_id):
       try:
            replication_manager.recover_node(node_id)
            return jsonify({'status': 'success', 'message': f'Node {node_id} recovered'})
       except Exception as e:
           return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route per recuperare lo stato di un nodo.
    @app.route('/nodes', methods=['GET'])
    @require_api_token
    def get_nodes():
        try:
            nodes_status = replication_manager.get_nodes_status()
            return jsonify({'status': 'success', 'nodes': nodes_status})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route per settare la strategia di replicazione.
    @app.route('/set_replication_strategy', methods=['POST'])
    @require_api_token
    def set_replication_strategy():
        data = request.json
        if 'strategy' not in data:
            return jsonify({'error': 'Invalid input', 'message': 'Replication strategy is required'}), 400
        strategy = data.get('strategy')
        replication_factor = data.get('replication_factor')
        try:
            replication_manager.set_replication_strategy(strategy, replication_factor)
            return jsonify({'status': 'success',
                            'message': f'Replication strategy set to {strategy} with factor {replication_factor}'})
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Route per ottenere i nodi responsabili di una chiave
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
