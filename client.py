import json
import os
import requests

# This script contains the definition of a client class to interact with the server

class DistributedKVClient:

    # Initialization of the client
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
    
    # Validation of the key and value
    def validate_key(self, key):  # Key should be a string
        if not key or key.strip() == "":
            print("Error: Key cannot be empty or whitespace.")
            return False
        return True

    # Validation of the value
    def validate_value(self, value):
        if not value or value.strip() == "":
            print("Error: Value cannot be empty or whitespace.")
            return False
        return True

    # Method to validate the node ID
    def validate_node_id(self, node_id):
        if not str(node_id).isdigit():  # Value should be a string
            print("Error: Node ID must be a valid integer.")
            return False
        return True

    # Method to set the replication strategy and replication factor
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

    # Method to write a key and value to the server
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

    # Method to read the value associated with a key
    def read(self, key):
        if not self.validate_key(key):
            return
        url = f"{self.base_url}/read/{key}"
        try:
            response = requests.get(url, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Method to delete a value associated with a key
    def delete(self, key):
        if not self.validate_key(key):
            return
        url = f"{self.base_url}/delete/{key}"
        try:
            response = requests.delete(url, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Method for node failure
    def fail_node(self, node_id):
        if not self.validate_node_id(node_id):
            return
        url = f"{self.base_url}/fail/{node_id}"
        try:
            response = requests.post(url, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Method for node recovery
    def recover_node(self, node_id):
        if not self.validate_node_id(node_id):
            return
        url = f"{self.base_url}/recover/{node_id}"
        try:
            response = requests.post(url, headers=self.headers)
            self.handle_response(response)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

    # Method to get the status of all nodes
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

    # Method to recover all nodes
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

    # Method for handling the response
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

# Function to load configuration values from a JSON file
def load_config(file_path, default_config=None):
    if default_config is None:
        default_config = {
            "host": "127.0.0.1",  # Default host
            "port": 5000,  # Default port
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

# This script is the entry point for a command-line interface (CLI) to interact with a distributed key-value store.
if __name__ == "__main__":
    # Path to the JSON configuration file
    file_path = 'config/config_client.json'

    # Load the entire configuration (replication factor and API token)
    config = load_config(file_path)

    # Extract the host and port values from the configuration
    host = config.get('host')
    port = config.get('port')
    api_token = config.get('API_TOKEN')

    # Base URL for the distributed key-value store API
    base_url = "http://" + str(host) + ":" + str(port)

    # Create an instance of the DistributedKVClient with the base URL and API token
    client = DistributedKVClient(base_url, api_token)

    if client.check_initialization():
        print("Client initialized successfully.")
        number_of_nodes = client.get_number_of_nodes()

        strategy = None

        # Infinite loop to display options and perform corresponding actions based on user input
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
            print("8. Demonstrate fail-recover behavior")
            print("9. Recover all nodes")
            print("10. Exit")


            # Prompt the user to enter their choice
            choice = input("Enter your choice: ")

            # Execute actions based on the user's choice
            if choice == '1':
                # Option to set the replication strategy
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
                # Option to write a key-value pair
                key = input("Enter key: ")
                value = input("Enter value: ")
                client.write(key, value)

            elif choice == '3':
                # Option to read a value by key
                key = input("Enter key: ")
                client.read(key)

            elif choice == '4':
                # Option to delete a key-value pair
                key = input("Enter key: ")
                client.delete(key)

            elif choice == '5':
                # Option to fail a specific node
                node_id = input("Enter node ID to fail: ")
                client.fail_node(node_id)

            elif choice == '6':
                # Option to recover a specific node
                node_id = input("Enter node ID to recover: ")
                client.recover_node(node_id)

            elif choice == '7':
                # Option to get the status of all nodes
                client.get_nodes()

            elif choice == '8':
                # Option to demonstrate the fail-recover behavior
                demonstrate_fail_recover_behavior(client)

            elif choice == '9':
                # Option to recover all nodes
                client.recover_all_nodes()

            elif choice == '10':
                # Exit the program
                break
            else:
                # Handle invalid choices
                print("Invalid choice. Please try again.")
