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

    def validate_node_id(self, node_id):
        if not str(node_id).isdigit():  # Value should be a string
            print("Error: Node ID must be a valid integer.")
            return False
        return True

    # Method to write a key and value to the server
      # Send a POST request to the server with the key and value
    def write(self, key, value):
        if not self.validate_key(key):
            return
        url = f"{self.base_url}/write"
        data = {"key": key, "value": value}
        response = requests.post(url, json=data, headers=self.headers)
        self.handle_response(response)  

    # Method to read the value associated with a key
      # Send a GET request to the server
    def read(self, key):
        if not self.validate_key(key):
            return
        url = f"{self.base_url}/read/{key}"
        response = requests.get(url, headers=self.headers)
        self.handle_response(response)

    # Method to delete a value associated with a key
      # Send a DELETE request to the server
    def delete(self, key):
        if not self.validate_key(key):
            return
        url = f"{self.base_url}/delete/{key}"
        response = requests.delete(url, headers=self.headers)
        self.handle_response(response)

    # Method for node failure
      # Send a POST request to the server to mark a node as failed
    def fail_node(self, node_id):
        if not self.validate_node_id(node_id):
            return
        url = f"{self.base_url}/fail/{node_id}"
        response = requests.post(url, headers=self.headers)
        self.handle_response(response)

    # Method for node recovery
      # Send a POST request to the server to recover a failed node
    def recover_node(self, node_id):
        if not self.validate_node_id(node_id):
            return
        url = f"{self.base_url}/recover/{node_id}"
        response = requests.post(url, headers=self.headers)
        self.handle_response(response)

    # Method to get the status of all nodes
      # Send a GET request to the server to get the status of all nodes
    def get_nodes(self):
        url = f"{self.base_url}/nodes"
        response = requests.get(url, headers=self.headers)
        self.handle_response(response)

    # Method to recover all nodes
      # Send a POST request to the server to recover all failed nodes
    def recover_all_nodes(self):
        url = f"{self.base_url}/nodes"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            nodes_status = response.json().get('nodes', [])
            all_alive = True
            for node in nodes_status:
                if node['status'] == 'dead':
                    all_alive = False
                    self.recover_node(node['node_id'])
            if all_alive:
                print(
                    f"Success: 200, Status: success, Message: All nodes are already alive")
        else:
            self.handle_response(response)

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
                    print(f"Success: {response.status_code}, Status: {status}, Message: {message}, Value: {value}")
                elif nodes:
                    print(f"Success: {response.status_code}, Status: {status}")
                    for node in nodes:
                        print(f"Node ID: {node['node_id']}, Status: {node['status']}, Port: {node['port']}")
                else:
                    print(f"Success: {response.status_code}, Status: {status}, Message: {message}")
            else:
                error_message = data.get('error', 'Unknown error')
                detailed_message = data.get('message', 'No detailed message provided')
                print(f"Failed: {response.status_code}, Error: {error_message}, Message: {detailed_message}")
        except ValueError:
            print(f"Failed: {response.status_code}, Response: {response.text}")

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
