import json
import os
import sys
from app import create_app
import unittest

# Funzione per caricare i valori di configurazione da un file JSON.
def load_config(file_path, default_config=None):
    if default_config is None:
        default_config = {
            "host": "127.0.0.1",  # Default host
            "port": 5000,  # Default port
            "nodes_db": 3,  # Default fattore di replica
            "API_TOKEN": "your_api_token_here"  # Default API token 
        }
    
    # Se il file non esiste, crea la directory e il file con valori predefiniti.
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

if __name__ == '__main__':
    # Percorso del file di configurazione JSON
    file_path = 'config/config.json'

    # Carica l'intera configurazione (fattore di replica e token API)
    config = load_config(file_path)

    # Estrai i valori dell'host e della porta dalla configurazione
    host = config.get('host')
    port = config.get('port')

    # Crea l'app Flask
    app = create_app(config)

    if 'test' in sys.argv:
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    else:
        app.run(debug=True, host=host, port=port)
