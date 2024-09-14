import hashlib
import bisect


class ConsistentHash:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
        self.ring = dict()
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                print(f'Adding node {node.node_id} to the ring')
                self.add_node(node)

    # Hash function to generate a hash key for a given input key
    def _hash(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    # Add a node to the ring
    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f'{node.node_id}:{i}')
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    # Remove a node from the ring
    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f'{node.node_id}:{i}')
            del self.ring[key]
            self.sorted_keys.remove(key)
        self._redistribute_keys(node)

    # Get the node responsible for the given key
    def get_node(self, key):
        if not self.ring:
            return None
        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]

    def get_nodes_for_key(self, key):
        # Logic to determine the nodes responsible for the given key
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
        if not self.ring:
            return None
        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0
        next_idx = (idx + 1) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[next_idx]]

    def redistribute_keys(self, node):
        self._redistribute_keys(node)

    def _redistribute_keys(self, node):
        for i in range(self.replicas):
            next_node = self.get_next_node(f'{node.node_id}:{i}')
            if next_node:
                for key, value in node.get_all_keys():
                    next_node.write(key, value)
