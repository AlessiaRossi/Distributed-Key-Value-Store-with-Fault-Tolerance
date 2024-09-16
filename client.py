import json
import os
import requests

# Questo script contiene la definizione di una classe client per interagire con il server

class DistributedKVClient:

    # Inizializzazione del client
    def __init__(self, base_url, api_token):
        self.base_url = base_url # Server URL to interact with
        self.headers = {"Authorization": f"Bearer {api_token}"} # API token for authentication
        self.check_initialization()

    def check_initialization(self):
        if not self.base_url or not self.headers.get('Authorization'):
            print("Error: Client not initialized. Please provide the base URL and API token.")
            return False
        try:
            response = requests.get(self.base_url + '/nodes', headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to establish a connection to {self.base_url}. Please check the URL and your configuration.")
            exit()
            return False
        return True
    
    # Validazione della chiave e del valore
    def validate_key(self, key):  # Key deve essere una stringa
        if not key or key.strip() == "":
            print("Error: Key cannot be empty or whitespace.")
            return False
        return True

    # Validazione del valore
    def validate_value(self, value):
        if not value or value.strip() == "":
            print("Error: Value cannot be empty or whitespace.")
            return False
        return True

    # Metodo per validare l'id del nodo
    def validate_node_id(self, node_id):
        if not str(node_id).isdigit():  # Il valore deve essere una stringa
            print("Error: Node ID must be a valid integer.")
            return False
        return True

    # Metodo per impostare la strategia di replica e il fattore di replica
    def set_replication_strategy(self, strategy, replication_factor=None):
        strategy = strategy.strip()
        url = f"{self.base_url}/set_replication_strategy"
        data = {"strategy": strategy}
        if replication_factor:
            data["replication_factor"] = replication_factor
        try:
            response = requests.post(url, json=data, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Metodo per scrivere una chiave e un valore sul server
    def write(self, key, value, strategy='full', replication_factor=None):
        if not self.validate_key(key) or not self.validate_value(value):
            return
        url = f"{self.base_url}/write"
        data = {"key": key, "value": value, "strategy": strategy}
        if replication_factor:
            data["replication_factor"] = replication_factor
        try:
            response = requests.post(url, json=data, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Metodo per leggere il valore associato a una chiave
    def read(self, key):
        if not self.validate_key(key):
            return
        url = f"{self.base_url}/read/{key}"
        try:
            response = requests.get(url, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Metodo per eliminare un valore associato a una chiave
    def delete(self, key):
        if not self.validate_key(key):
            return
        url = f"{self.base_url}/delete/{key}"
        try:
            response = requests.delete(url, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Metodo per il fallimento di un nodo
    def fail_node(self, node_id):
        if not self.validate_node_id(node_id):
            return
        url = f"{self.base_url}/fail/{node_id}"
        try:
            response = requests.post(url, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Metodo per il recupero di un nodo
    def recover_node(self, node_id):
        if not self.validate_node_id(node_id):
            return
        url = f"{self.base_url}/recover/{node_id}"
        try:
            response = requests.post(url, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Metodo per ottenere lo stato di tutti i nodi
    def get_nodes(self):
        url = f"{self.base_url}/nodes"
        try:
            response = requests.get(url, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

      
    def get_number_of_nodes(self):
        url = f"{self.base_url}/nodes"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                nodes = response.json().get('nodes', [])
                return len(nodes)
            else:
                self.handle_response(response)
                return 0
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return 0

    # Metodo per recuperare tutti i nodi
    def recover_all_nodes(self):
        url = f"{self.base_url}/nodes"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                nodes_status = response.json().get('nodes', [])
                all_alive = True
                for node in nodes_status:
                    if node['status'] == 'dead':
                        all_alive = False
                        self.recover_node(node['node_id'])
                if all_alive:
                    print(f"Operation successful: all nodes are already active.")
            else:
                self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Metodo per gestire la risposta
    def handle_response(self, response):
        try:
            data = response.json()
            if response.status_code == 200:
                status = data.get('status', 'success')
                message = data.get('message', 'Operation completed successfully')
                value = data.get('value', '')
                nodes = data.get('nodes', [])
                if value:
                    print(f"Status Update: {message}, Value: {value}")
                elif nodes:
                    print(f"Status: {status}")
                    for node in nodes:
                        print(f"Node ID: {node['node_id']}, Status: {node['status']}, Port: {node['port']}")
                else:
                    print(f"Status Update: {message}")
            else:
                error_message = data.get('error', 'Unknown error')
                detailed_message = data.get('message', 'No detailed message provided')
                print(f"Error: {error_message}, Status Update: {detailed_message}")
        except ValueError:
            print(f"Response: {response.text}")

# Funzione per caricare i valori di configurazione da un file JSON
def load_config(file_path, default_config=None):
    if default_config is None:
        default_config = {
            "host": "127.0.0.1",  # Default host
            "port": 5000,  # Default port
            "API_TOKEN": "your_api_token_here"  # Default API token
        }
    
    # Se il file non esiste, crea la directory e il file con i valori predefiniti
    if not os.path.exists(file_path):
        dir_name = os.path.dirname(file_path)
        # Crea la directory se non esiste
        if not os.path.exists(dir_name) and dir_name != '':
            os.makedirs(dir_name)
        # Scrivi i valori predefiniti nel file JSON
        with open(file_path, 'w') as f:
            json.dump(default_config, f)
        return default_config
    
    # Se il file esiste, carica i valori dal file JSON
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Restituisci la configurazione unificata (file + valori predefiniti per quelli mancanti)
            return {**default_config, **data}
    except (json.JSONDecodeError, KeyError):
        # Se il file JSON è corrotto o non contiene i valori corretti, restituisci la configurazione predefinita
        return default_config

# Questo script è il punto di ingresso per un'interfaccia a riga di comando (CLI) per interagire con sistema di memorizzazione distribuita di coppie chiave-valore.
if __name__ == "__main__":
    # Percorso del file di configurazione JSON
    file_path = 'config/config_client.json'

    # Carica l'intera configurazione (fattore di replica e token API)
    config = load_config(file_path)

    # Estrai i valori dell'host e della porta dalla configurazione
    host = config.get('host')
    port = config.get('port')
    api_token = config.get('API_TOKEN')

    # URL di base per l'API del sistema di memorizzazione distribuita di coppie chiave-valore
    base_url = "http://" + str(host) + ":" + str(port)

    # Crea un'istanza di DistributedKVClient con l'URL di base e il token API
    client = DistributedKVClient(base_url, api_token)

    if client.check_initialization():
        print("Client initialized successfully.")
        number_of_nodes = client.get_number_of_nodes()

        strategy = None

        # Menu per visualizzare le opzioni e eseguire le azioni corrispondenti in base all'input dell'utente
        while True:
            # Print the available options to the user
            print("\nOptions:")
            if strategy is None:
                print("1. Set replication strategy consistent/full (default: full)")
            else:
                print(f"1. Set replication strategy consistent/full (actived: {strategy})")
            print("2. Write key-value")
            print("3. Read value by key")
            print("4. Delete key-value")
            print("5. Fail a node")
            print("6. Recover a node")
            print("7. Get nodes status")
            print("8. Recover all nodes")
            print("9. Exit")


            # Chiedi all'utente di inserire la propria scelta
            choice = input("Enter your choice: ")

            # Esegui l'azione in base alla scelta
            if choice == '1':
                # Opzione per impostare la strategia di replica
                strategy = input("Enter strategy (full/consistent): ")
                replication_factor = None
                if strategy == 'consistent':
                    while True:
                        replication_factor = int(input(f"Enter replication factor (<= {number_of_nodes}): "))
                        if replication_factor <= number_of_nodes:
                            break
                        else:
                            print(f"Replication factor must be less than or equal to the number of nodes ({number_of_nodes}).")
                if strategy in ['consistent', 'full']:
                    client.set_replication_strategy(strategy, replication_factor)
                else:
                    strategy = None
                    print("Invalid strategy. Please try again.")          

            elif choice == '2':
                # Opzione per scrivere una coppia chiave-valore
                key = input("Enter key: ")
                value = input("Enter value: ")
                client.write(key, value)

            elif choice == '3':
                # Opzione per leggere un valore tramite chiave
                key = input("Enter key: ")
                client.read(key)

            elif choice == '4':
                # Opzione per eliminare una coppia chiave-valore
                key = input("Enter key: ")
                client.delete(key)

            elif choice == '5':
                # Opzione per far fallire un nodo specifico
                node_id = input("Enter node ID to fail: ")
                client.fail_node(node_id)

            elif choice == '6':
                # Opzione per recuperare un nodo specifico
                node_id = input("Enter node ID to recover: ")
                client.recover_node(node_id)

            elif choice == '7':
                # Opzione per ottenere lo stato di tutti i nodi
                client.get_nodes()

            elif choice == '8':
                # Opzione per recuperare tutti i nodi
                client.recover_all_nodes()

            elif choice == '9':
                # Esci dal programma
                break
            else:
                # Gestire la scelta non valida
                print("Invalid choice. Please try again.")
