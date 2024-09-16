import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, replicas=None):
        self.replicas = replicas or len(nodes)  # Numero di repliche per nodo
        self.ring = dict()  # Dizionario hash -> nodo
        self.sorted_keys = []  # Lista ordinata per la ricerca binaria
        self.key_assignments = {}  # Traccia key -> nodo assegnato
        self.temp_key_storage = {}  # Traccia chiavi spostate temporaneamente durante il fallimento
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        """Genera un hash per una data chiave."""
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        """Aggiunge un nodo all'anello."""
        for i in range(self.replicas):
            key = self._hash(f'{node.node_id}:{i}') # Genera una chiave hash per ogni replica
            self.ring[key] = node # Mappa la chiave al nodo
            bisect.insort(self.sorted_keys, key) # Inserisci la chiave nella lista ordinata

    def remove_node(self, node):
        """Rimuove un nodo dall'anello e riassegna le sue chiavi."""
        for i in range(self.replicas):
            key = self._hash(f'{node.node_id}:{i}')
            del self.ring[key]
            self.sorted_keys.remove(key)
        #self._redistribute_keys(node)

    def get_node(self, key):
        """Ottiene il nodo responsabile per una chiave."""
        if not self.ring:
            return None
        hash_key = self._hash(key) # Calcola l'hash della chiave
        idx = bisect.bisect(self.sorted_keys, hash_key) # Trova l'indice della chiave hash
        if idx == len(self.sorted_keys): # Se l'indice è fuori dalla lista, torna al primo nodo
            idx = 0
        return self.ring[self.sorted_keys[idx]] # Restituisci il nodo responsabile

    def get_nodes_for_key(self, key):
        """Restituisce una lista di nodi responsabili per la replica della chiave."""
        if not self.ring:
            return []

        # Se il fattore di replicazione è uguale al numero di nodi, restituisci tutti i nodi
        if self.replicas >= len(self.ring):
            nodes = list(self.ring.values())
            print(f"Fattore di replicazione >= numero di nodi, restituisco tutti i nodi: {[node.node_id for node in nodes]}")
            return nodes

        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        nodes = []
        seen_nodes = set()  # Set per tracciare i nodi già aggiunti
        while len(nodes) < self.replicas:
            if idx == len(self.sorted_keys):
                idx = 0
            node = self.ring[self.sorted_keys[idx]]
            if node.node_id not in seen_nodes:  # Aggiungi solo se il nodo non è già stato aggiunto
                nodes.append(node)
                seen_nodes.add(node.node_id)
            idx += 1
        print(f"Nodi per la chiave '{key}': {[node.node_id for node in nodes]}")
        return nodes

    def get_next_node(self, key, exclude_node_id=None):
        """Ottieni il nodo successivo per una chiave, escludendo eventuali nodi specifici."""
        if not self.ring:
            return None

        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)

        # Cerca il prossimo nodo attivo nel ring, evitando il nodo specificato da escludere
        for i in range(len(self.sorted_keys)):
            next_idx = (idx + i) % len(self.sorted_keys)  # Cicla in avanti
            next_node = self.ring[self.sorted_keys[next_idx]]

            if next_node.is_alive() and next_node.node_id != exclude_node_id:  # Escludi il nodo specificato
                return next_node

        return None  # Se non trova nodi validi

    def redistribute_keys(self, node):
        """Ridistribuisce le chiavi di un nodo fallito al successivo nodo attivo."""
        # Ottieni il nodo successivo per tutte le chiavi del nodo fallito
        next_node = self.get_next_node(f'{node.node_id}:0', exclude_node_id=node.node_id)  # Il nodo successivo nel ring

        if next_node:
            print(f"Redistribuzione delle chiavi del nodo {node.node_id} al nodo {next_node.node_id}")
            for key, value in node.get_all_keys():  # Recupera tutte le chiavi dal nodo fallito
                # Controlla se il nodo successivo ha già la chiave
                if not next_node.key_exists(key):
                    # Se la chiave non esiste nel nodo successivo, spostala
                    next_node.write(key, value)  # Scrivi la chiave nel nuovo nodo
                    self.temp_key_storage[key] = (next_node.node_id, value)  # Traccia la chiave spostata con il valore
                    print(f"Chiave '{key}' scritta nel nodo {next_node.node_id}.")
                else:
                    print(f"La chiave '{key}' esiste già nel nodo {next_node.node_id}, nessuna scrittura necessaria.")

    def recover_node(self, node):
        """Recupera un nodo e ripristina le sue chiavi, rimuovendo le chiavi dai nodi ospitanti solo se necessario."""
        print(f"Recupero node {node.node_id}...")

        # Trova le chiavi che sono state spostate temporaneamente
        keys_to_recover = [
            key for key, (temp_node_id, value) in self.temp_key_storage.items()
            if temp_node_id != node.node_id #solo se chiavi non sono già presenti nel nodo
        ]
        print(f"Chiavi da recuperare: {keys_to_recover}")

        for key in keys_to_recover: # per ogni chiave da recuperare
            temp_node_id, value = self.temp_key_storage[key] # Ottieni ID nodo ospitante e il valore
            temp_node = self.get_node_by_id(temp_node_id) # Ottieni il nodo ospitante usando suo ID

            # Verifica se la chiave è una replica naturale del nodo
            naturally_responsible_nodes = self.get_nodes_for_key(key) # Nodi responsabili per la replica della chiave
            if temp_node and temp_node_id != node.node_id: # Se il nodo ospitante è diverso dal nodo recuperato
                print(f"Ripristino della chiave '{key}' nel nodo {node.node_id} dal nodo ospitante {temp_node_id}...")

                # Elimina la chiave solo se non è una replica naturale del nodo
                if temp_node not in naturally_responsible_nodes:
                    print(f"Eliminazione della chiave '{key}' dal nodo ospitante {temp_node_id} perché non è una replica originaria.")
                    temp_node.delete(key)  # Elimina dal DB del nodo ospitante
                else:
                    print(f"Saltata eliminazione della chiave '{key}' sul nodo {temp_node_id}, è una replica originaria.")

                # Scrivi la chiave e il valore nel nodo recuperato, solo se non esiste già
                if not node.key_exists(key):
                    print(f"Scrittura della chiave  '{key}' nel nodo recuperato {node.node_id}.")
                    node.write(key, value)
                else:
                    print(f"La chiave '{key}' esiste già nel nodo {node.node_id}, salto la scrittura.")

                # Rimuovi la chiave dalla memoria temporanea
                del self.temp_key_storage[key]

        print(f"Recupero del nodo {node.node_id} completato.")


    def get_node_by_id(self, node_id):
        """Ottieni un nodo dal suo ID."""
        for node in self.ring.values():
            if node.node_id == node_id:
                return node
        return None
