import json
import os
import sys
from app import create_app
import unittest

# Function to load configuration values from a JSON file
def load_config(file_path, default_config=None):
    if default_config is None:
        default_config = {
            "host": "127.0.0.1",  # Default host
            "port": 5000,  # Default port
            "nodes_db": 3,  # Default replication factor
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

if __name__ == '__main__':
    # Path to the JSON configuration file
    file_path = 'config/config.json'

    # Load the entire configuration (replication factor and API token)
    config = load_config(file_path)

    # Extract the host and port values from the configuration
    host = config.get('host')
    port = config.get('port')

    # Create the Flask app
    app = create_app(config)

    if 'test' in sys.argv:
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    else:
        app.run(debug=True, host=host, port=port)
