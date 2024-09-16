import sqlite3
import os
from .consistent_hash import ConsistentHash


class ReplicaNode:
    def __init__(self, node_id, port):
        # Inizializza un nodo replica con un identificatore univoco e una porta.
        self.node_id = node_id
        self.port = port
        self.name_db = f'replica_{node_id}.db'  # Nome del file del database per questo nodo.
        self.db_path = os.path.join('db', self.name_db)  # Percorso del file del database per questo nodo.
        self.alive = True  # Lo stato iniziale del nodo è attivo.
        self.create_db_directory()  # Crea la directory 'db' se non esiste già.
        self._initialize_db()  # Inizializza il db se non esiste già-

    def create_db_directory(self):
        # Crea la directory 'db' se non esiste già.
        if not os.path.exists('db'):
            os.makedirs('db')  # Crea la directory.

    def _initialize_db(self):
        # Crea la tabella 'kv_store' se non esiste già nel database.
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)  # Si connette al db
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS kv_store (key TEXT PRIMARY KEY, value TEXT)''')  # Crea la tabella
            conn.commit()  # Committa sul db
            conn.close()  # Chiude la connessione al db.

    def write(self, key, value):
        # Scrive una coppia chiave-valore nel database solo se il nodo è attivo.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Si connette al db
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute('''INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)''',
                           (key, value))  # Inserts or updates the data.
            conn.commit()  # Committa sul db
            conn.close()  # Chiude la connessione al db.

    def read(self, key):
        # Legge il valore associato a una chiave dal database solo se il nodo è attivo.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Si connette al db
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute('''SELECT value FROM kv_store WHERE key=?''', (key,))  # Seleziona la value per la key indicata.
            result = cursor.fetchone()  # Recupera il risultato della query.
            conn.close()  # Chiude la connessione al db.
            return result[0] if result else None  # Restituisce il valore se trovato, altrimenti None.

    def delete(self, key):
        # Elimina la coppia chiave-valore dal database solo se il nodo è attivo.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  #  Si connette al db
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute('''DELETE FROM kv_store WHERE key=?''', (key,))  #Elimina la coppia chiave-valore dal database solo se il nodo è attivo.
            conn.commit()  # Committa sul db
            conn.close()  # Chiude la connessione al db.

    def key_exists(self, key):
        # Verifica se una chiave esiste nel database solo se il nodo è attivo.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  #  Si connette al db
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute('''SELECT 1 FROM kv_store WHERE key=?''', (key,))  # Verifica se la chiave esiste.
            exists = cursor.fetchone() is not None  # Verifica se è stata trovata almeno una riga.
            conn.close()  # Chiude la connessione al db.
            return exists  # Restituisce True se trovato, altrimenti False.

    def fail(self):
        # Simula il fallimento del nodo impostando il suo stato su inattivo.
        self.alive = False

    def recover(self, active_nodes, strategy='full'):
        # Recupera il nodo e sincronizza i dati con gli altri nodi attivi.
        if not self.alive:
            self.alive = True  # Setta il nodo attivo
            if strategy == 'full':
                self.sync_with_active_nodes(active_nodes)  # Sincronizza con gli altri nodi attivi.

    def is_alive(self):
        # Restituisce lo stato corrente del nodo
        return self.alive

    def sync_with_active_nodes(self, active_nodes):
        # Sincronizza i dati del nodo con gli altri nodi attivi.
        all_keys = set()  # Inizializza un set per memorizzare tutte le chiavi.
        for node in active_nodes:
            if node.is_alive() and node.node_id != self.node_id:
                conn = sqlite3.connect(node.db_path)  # Si connette al database dell'altro nodo.
                cursor = conn.cursor()  #  Crea un cursore per eseguire comandi SQL.
                cursor.execute('''SELECT key, value FROM kv_store''')  # Seleziona tutte le coppie key-valore.
                rows = cursor.fetchall()  # Recupera tutte le righe.
                conn.close()  # Chiude la connessione al db
                for key, value in rows:
                    self.write(key, value)  # Scrive ogni coppia chiave-valore nel database del nodo corrente.
                    all_keys.add(key)  # Aggiunge la chiave all'insieme di tutte le chiavi.

        # Recupera tutte le chiavi.
        # si connette al nodo ricoverato e recupera tutte le chiavi al suo interno ,
        conn = sqlite3.connect(self.db_path)  # Si connette al database del nodo corrente.
        cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
        cursor.execute('''SELECT key FROM kv_store''')  # Seleziona tutte le key
        self_keys = cursor.fetchall()  # Recupera tutte le key
        conn.close()  # Chiude la connessione al db.

        # Rimuove le chiavi da self che non sono presenti negli altri nodi attivi.
        for (key,) in self_keys:
            if key not in all_keys:
                self.delete(key)  # Elimina la chiave dal database del nodo corrente.

    def get_all_keys(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT key, value FROM kv_store''')
        rows = cursor.fetchall()
        conn.close()
        return rows

class ReplicationManager:
    def __init__(self, nodes_db=3, port=5000, strategy='full', replication_factor=None):
        # Inizializza il gestore della replica con un fattore di replica specificato.
        self.nodes_db = nodes_db
        # Inizializza la strategia di replica a 'full' per impostazione predefinita.
        self.strategy = strategy
        # Crea un elenco di nodi replica con identificatori unici e porte.
        self.nodes = [ReplicaNode(i, port + i) for i in range(self.nodes_db)]
        # Inizializza la strategia di replica in base alla strategia specificata.
        self.consistent_hash = None

        if strategy == 'consistent':
            self.consistent_hash = ConsistentHash(self.nodes, replicas=replication_factor)

    def set_replication_strategy(self, strategy, replication_factor=None):
        self.strategy = strategy

        if strategy == 'consistent':
            self.consistent_hash = ConsistentHash(self.nodes, replicas=replication_factor)
            print(f"Setting replication strategy to {strategy} with replication factor {replication_factor}")
        else:
            self.consistent_hash = None

    def write_to_replicas(self, key, value):
        # Scrive una coppia chiave-valore su tutti i nodi replica attivi.
        if self.strategy == 'full':
            for node in self.nodes:
                if node.is_alive():  # Verifica se il nodo è attivo
                    print(f"Writing key '{key}' to node {node.node_id}")
                    node.write(key, value)  # Scrive sul nodo.
        # Se la strategia di replica è 'consistent', scrive sul nodo appropriato in base all'hash della chiave.
        elif self.strategy == 'consistent':
            nodes = self.consistent_hash.get_nodes_for_key(key)
            for node in nodes:
                if node.is_alive():
                    print(f"Writing key '{key}' to node {node.node_id}")
                    node.write(key, value)

    def read_from_replicas(self, key):
        # Legge il valore associato a una chiave dai nodi replica attivi.
        if self.strategy == 'full':
            for node in self.nodes:
                if node.is_alive():  # Verifica se il nodo è attivo
                    result = node.read(key)  # Legge il valore associato al nodo
                    if result is not None:  # Se il risultato non è None, Restituisce il valore e un messaggio..
                        return {'value': result, 'message': f'Read from replica {node.node_id}'}
        # Se la strategia di replica è 'consistent', scrive sul nodo appropriato in base all'hash della chiave.
        elif self.strategy == 'consistent':
            node = self.consistent_hash.get_node(key)
            if node and node.is_alive():
                result = node.read(key)
                if result is not None:
                    return {'value': result, 'message': f'Read from replica {node.node_id}'}
        # Se nessun nodo ha restituito un valore, restituisce un messaggio di errore.
        return {'value': None, 'message': 'All replicas failed or key not found'}

    def delete_from_replicas(self, key):
        # Elimina una chiave da tutti i nodi replica.
        for node in self.nodes:
            node.delete(key)  # Richiama il metodo di eliminazione su ciascun nodo.

    def key_exists_in_replicas(self, key):
        # Verifica se una chiave esiste in almeno uno dei nodi replica attivi.
        for node in self.nodes:
            if node.is_alive() and node.key_exists(key):  # Verifica se la chiave esiste nel nodo attivo.
                return True  # Ritorna True se la jey esiste.
        return False  # Restituisce False se la chiave non è stata trovata in nessun nodo attivo.

    def fail_node(self, node_id):
        # Simula il fallimento di un nodo specifico identificato da node_id.
        if 0 <= node_id < len(self.nodes):  # Fa un check per vedere se l'ID esiste.
            node = self.nodes[node_id]
            node.fail()
            if self.strategy == 'consistent':
                self.consistent_hash.redistribute_keys(node)

    def recover_node(self, node_id):
        """Recupera un nodo e ripristina le sue chiavi, eliminando le chiavi dal nodo ospitante."""
        if 0 <= node_id < len(self.nodes):
            node = self.nodes[node_id]
            node.recover(self.nodes, self.strategy)  # Recupera lo stato del nodo
            if self.strategy == 'consistent':
                print(f"Recovering node {node_id}...")
                self.consistent_hash.recover_node(node)  # Recupera le chiavi nel nodo consistent hash

    def get_nodes_status(self):
        # Restituisce lo stato di tutti i nodi in un elenco di dizionari.
        return [
            {
                'node_id': node.node_id,  # ID del nodo
                'status': 'alive' if node.is_alive() else 'dead',  # Stato del nodo (attivo o non ).
                'port': node.port  # Porta del nodo.
            }
            for node in self.nodes
        ]


    def get_nodes_for_key(self, key):
        # Returns the nodes responsible for the key based on the replication strategy.
        if self.strategy == 'consistent' and self.consistent_hash:
            return self.consistent_hash.get_nodes_for_key(key)
        else:
            return None
