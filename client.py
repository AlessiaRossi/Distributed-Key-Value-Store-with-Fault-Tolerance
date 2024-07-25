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

    # Method to get the status of all nodes
      # Send a GET request to the server to get the status of all nodes

    # Method to recover all nodes
      # Send a POST request to the server to recover all failed nodes

    # Method for handling the response
    def handle_response(self, response):
        pass
