import requests

# This script contains the definition of a client class to interact with the server

class DistributedKVClient:

    # Initialization of the client
    def __init__(self, base_url, api_token):
        self.base_url = base_url # Server URL to interact with
        self.headers = {"Authorization": f"Bearer {api_token}"} # API token for authentication


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




# Method for demonstrate the behavior of a distributed key-value store system in scenarios of node failure and
# recovery
def demonstrate_fail_recover_behavior(client):
    print("\n--- Demonstrating Fail-Recover Behavior ---")

    # Step 1: Writing initial data
    print("\nStep 1: Writing initial data...")
    client.write('key1', 'value1')
    client.write('key2', 'value2')

    # Verifying the written data
    print("\nVerifying initial data...")
    client.read('key1')
    client.read('key2')

    # Step 2: Failing a node
    print("\nStep 2: Failing a node (node 1)...")
    client.fail_node(1)

    # Step 3: Verifying data availability after node failure
    print("\nStep 3: Verifying data availability after node failure...")
    client.read('key1')
    client.read('key2')

    # Step 4: Writing additional data during node failure
    print("\nStep 4: Writing additional data while node 1 is failed...")
    client.write('key3', 'value3')

    # Verifying the data written during node failure
    print("\nVerifying data written during node failure...")
    client.read('key3')

    # Step 5: Recovering the failed node
    print("\nStep 5: Recovering the failed node (node 1)...")
    client.recover_node(1)

    # Step 6: Verifying data synchronization after node recovery
    print("\nStep 6: Verifying data synchronization after node recovery...")
    client.read('key1')
    client.read('key2')
    client.read('key3')

    print("\n--- Demonstration Completed ---")


# This script is the entry point for a command-line interface (CLI) to interact with a distributed key-value store.
if __name__ == "__main__":
    # Base URL for the distributed key-value store API
    base_url = "http://127.0.0.1:5000"

    # API token for authentication (replace with the actual token)
    api_token = "your_api_token_here"

    # Create an instance of the DistributedKVClient with the base URL and API token
    client = DistributedKVClient(base_url, api_token)

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
                    replication_factor = int(input(f"Enter replication factor (<{number_of_nodes}): "))
                    if replication_factor < number_of_nodes:
                        break
                    else:
                        change_to_full = input("Replication factor must be less than the number of nodes.\nDo you want to switch to 'full' strategy? (yes/no): ").strip().lower()
                        if change_to_full == 'yes':
                            strategy = 'full'
                            replication_factor = None
                            break
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
