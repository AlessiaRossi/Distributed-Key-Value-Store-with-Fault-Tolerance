import sqlite3
import os

class ReplicaNode:
    def __init__(self, node_id, port):
        # Inizializza un nodo replica con un identificatore univoco e una porta.
        self.node_id = node_id
        self.port = port
        self.db_path = f'replica_{node_id}.db'  # Percorso del file del database per questo nodo.
        self.alive = True  # Stato iniziale del nodo è attivo.
        self._initialize_db()  # Inizializza il database se non esiste.

    def _initialize_db(self):
        # Crea la tabella 'kv_store' se non esiste già nel database.
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)  # Connessione al database.
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute('''CREATE TABLE IF NOT EXISTS kv_store (key TEXT PRIMARY KEY, value TEXT)''')  # Crea la tabella.
            conn.commit()  # Conferma le modifiche al database.
            conn.close()  # Chiude la connessione al database.

    def write(self, key, value):
        # Scrive una coppia chiave-valore nel database solo se il nodo è attivo.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Connessione al database.
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute('''INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)''', (key, value))  # Inserisce o aggiorna il dato.
            conn.commit()  # Conferma le modifiche al database.
            conn.close()  # Chiude la connessione al database.

    def read(self, key):
        # Legge il valore associato alla chiave dal database solo se il nodo è attivo.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Connessione al database.
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute('''SELECT value FROM kv_store WHERE key=?''', (key,))  # Seleziona il valore per la chiave.
            result = cursor.fetchone()  # Recupera il risultato della query.
            conn.close()  # Chiude la connessione al database.
            return result[0] if result else None  # Restituisce il valore se trovato, altrimenti None.

    def delete(self, key):
        # Elimina la coppia chiave-valore dal database solo se il nodo è attivo.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Connessione al database.
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute('''DELETE FROM kv_store WHERE key=?''', (key,))  # Elimina il dato associato alla chiave.
            conn.commit()  # Conferma le modifiche al database.
            conn.close()  # Chiude la connessione al database.

    def key_exists(self, key):
        # Verifica se una chiave esiste nel database solo se il nodo è attivo.
        if self.alive:
            conn = sqlite3.connect(self.db_path)  # Connessione al database.
            cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
            cursor.execute('''SELECT 1 FROM kv_store WHERE key=?''', (key,))  # Controlla se la chiave esiste.
            exists = cursor.fetchone() is not None  # Verifica se è stata trovata almeno una riga.
            conn.close()  # Chiude la connessione al database.
            return exists  # Restituisce True se la chiave esiste, altrimenti False.

    def fail(self):
        # Simula il fallimento del nodo impostando il suo stato su inattivo.
        self.alive = False

    def recover(self, active_nodes):
        # Recupera il nodo e sincronizza i dati con gli altri nodi attivi.
        if not self.alive:
            self.alive = True  # Imposta lo stato del nodo su attivo.
            self.sync_with_active_nodes(active_nodes)  # Sincronizza con gli altri nodi attivi.

    def is_alive(self):
        # Restituisce lo stato attuale del nodo.
        return self.alive

    def sync_with_active_nodes(self, active_nodes):
        # Sincronizza i dati del nodo con gli altri nodi attivi.
        for node in active_nodes:
            if node.is_alive() and node.node_id != self.node_id:
                conn = sqlite3.connect(node.db_path)  # Connessione al database dell'altro nodo.
                cursor = conn.cursor()  # Crea un cursore per eseguire comandi SQL.
                cursor.execute('''SELECT key, value FROM kv_store''')  # Seleziona tutte le coppie chiave-valore.
                rows = cursor.fetchall()  # Recupera tutte le righe.
                conn.close()  # Chiude la connessione al database.
                for key, value in rows:
                    self.write(key, value)  # Scrive ogni coppia chiave-valore nel database del nodo corrente.

class ReplicationManager:
    def __init__(self, replication_factor):
        # Inizializza il manager di replica con un fattore di replicazione specificato.
        self.replication_factor = replication_factor
        # Crea una lista di nodi replica con identificatori univoci e porte.
        self.nodes = [ReplicaNode(i, 5000 + i) for i in range(replication_factor)]

    def write_to_replicas(self, key, value):
        # Scrive una coppia chiave-valore in tutti i nodi replica attivi.
        for node in self.nodes:
            if node.is_alive():  # Verifica se il nodo è attivo.
                node.write(key, value)  # Scrive il dato nel nodo.

    def read_from_replicas(self, key):
        # Legge il valore associato a una chiave da nodi replica attivi.
        for node in self.nodes:
            if node.is_alive():  # Verifica se il nodo è attivo.
                result = node.read(key)  # Legge il valore dal nodo.
                if result is not None:  # Se il risultato non è None, restituisce il valore e un messaggio.
                    return {'value': result, 'message': f'Read from replica {node.node_id}'}
        # Se nessun nodo ha restituito un valore, restituisce un messaggio di errore.
        return {'value': None, 'message': 'All replicas failed or key not found'}

    def delete_from_replicas(self, key):
        # Elimina una chiave da tutti i nodi replica.
        for node in self.nodes:
            node.delete(key)  # Chiama il metodo delete su ogni nodo.

    def key_exists_in_replicas(self, key):
        # Verifica se una chiave esiste in almeno uno dei nodi replica attivi.
        for node in self.nodes:
            if node.is_alive() and node.key_exists(key):  # Controlla se la chiave esiste nel nodo attivo.
                return True  # Restituisce True se la chiave esiste.
        return False  # Restituisce False se la chiave non è trovata in nessun nodo attivo.

    def fail_node(self, node_id):
        # Simula il fallimento di un nodo specifico identificato da node_id.
        if 0 <= node_id < len(self.nodes):  # Verifica se l'ID del nodo è valido.
            self.nodes[node_id].fail()  # Chiama il metodo fail del nodo.

    def recover_node(self, node_id):
        # Recupera un nodo specifico e sincronizza i dati con gli altri nodi attivi.
        if 0 <= node_id < len(self.nodes):  # Verifica se l'ID del nodo è valido.
            self.nodes[node_id].recover(self.nodes)  # Chiama il metodo recover del nodo.

    def get_nodes_status(self):
        # Restituisce lo stato di tutti i nodi in una lista di dizionari.
        return [
            {
                'node_id': node.node_id,  # ID del nodo.
                'status': 'alive' if node.is_alive() else 'dead',  # Stato del nodo (attivo o inattivo).
                'port': node.port  # Porta del nodo.
            }
            for node in self.nodes
        ]
