import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
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
            key = self._hash(f'{node.node_id}:{i}')
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node):
        """Rimuove un nodo dall'anello e riassegna le sue chiavi."""
        for i in range(self.replicas):
            key = self._hash(f'{node.node_id}:{i}')
            del self.ring[key]
            self.sorted_keys.remove(key)
        self._redistribute_keys(node)

    def get_node(self, key):
        """Ottiene il nodo responsabile per una chiave."""
        if not self.ring:
            return None
        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]
    
    def get_nodes_for_key(self, key):
        """Restituisce una lista di nodi responsabili per la replica della chiave."""
        if not self.ring:
            return []
        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        nodes = []
        for i in range(self.replicas):
            if idx == len(self.sorted_keys):
                idx = 0
            nodes.append(self.ring[self.sorted_keys[idx]])
            idx += 1
        return nodes

    def get_next_node(self, key):
        """Ottieni il nodo successivo per una chiave."""
        if not self.ring:
            return None
        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0
        next_idx = (idx + 1) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[next_idx]]

    def redistribute_keys(self, node):
        """Ridistribuisce le chiavi di un nodo fallito al successivo nodo attivo."""
        # Ottieni il nodo successivo per tutte le chiavi del nodo fallito
        next_node = self.get_next_node(f'{node.node_id}:0')  # Il nodo successivo nel ring

        if next_node:
            print(f"Redistribuzione delle chiavi del nodo {node.node_id} al nodo {next_node.node_id}")
            for key, value in node.get_all_keys():  # Recupera tutte le chiavi dal nodo fallito
                next_node.write(key, value)  # Scrivi le chiavi nel nuovo nodo
                self.temp_key_storage[key] = next_node.node_id  # Traccia le chiavi spostate

    def recover_node(self, node):
        """Recupera un nodo e ripristina le sue chiavi, rimuovendo le chiavi dai nodi ospitanti."""
        print(f"Recovering node {node.node_id}...")

        # Trova le chiavi che sono state ospitate temporaneamente
        keys_to_recover = [key for key, temp_node_id in self.temp_key_storage.items() if temp_node_id != node.node_id]
        print(f"Keys to recover: {keys_to_recover}")

        for key in keys_to_recover:
            # Identifica il nodo ospitante
            temp_node_id = self.temp_key_storage[key]
            temp_node = self.get_node_by_id(temp_node_id)

            if temp_node and temp_node_id != node.node_id:
                # Leggi il valore dal nodo temporaneo
                value = temp_node.read(key)  # Leggi il valore dal nodo ospitante
                if value is not None:
                    # Elimina la chiave dal nodo ospitante
                    temp_node.delete(key)  # Elimina dal DB del nodo ospitante

                    # Scrivi la chiave e il valore nel nodo recuperato
                    node.write(key, value)  # Ripristina la chiave e il valore nel DB del nodo recuperato

                    # Rimuovi la chiave dalla memoria temporanea
                    del self.temp_key_storage[key]

        print(f"Node {node.node_id} recovery complete.")

    def get_node_by_id(self, node_id):
        """Ottieni un nodo dal suo ID."""
        for node in self.ring.values():
            if node.node_id == node_id:
                return node
        return None
