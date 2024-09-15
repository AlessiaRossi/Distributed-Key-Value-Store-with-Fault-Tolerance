import os
import sys
import unittest
import time

# Aggiungi il percorso del progetto alla variabile sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import ReplicationManager

# Test delle performance per il ReplicationManager
class TestPerformance(unittest.TestCase):
    results = {}  # Trasformato in attributo di classe

    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.replication_manager_full = None
        self.replication_manager_consistent = None
        self.range_to_test = 100  # Numero di operazioni da eseguire durante i test
        self.nodes_db = 3  # Numero di nodi
        self.replication_factor = 2  # Fattore di replicazione

    def setUp(self):
        # Inizializza i manager di replicazione con le due strategie
        self.replication_manager_full = ReplicationManager(nodes_db=self.nodes_db, strategy='full', replication_factor=self.replication_factor)
        self.replication_manager_consistent = ReplicationManager(nodes_db=self.nodes_db, strategy='consistent', replication_factor=self.replication_factor)

    def test_write_performance_full(self):
        start_time = time.time()
        for i in range(self.range_to_test):
            self.replication_manager_full.write_to_replicas(f'key_{i}', f'value_{i}')
        end_time = time.time()
        TestPerformance.results['Write performance (full)'] = end_time - start_time

    def test_read_performance_full(self):
        for i in range(self.range_to_test):
            self.replication_manager_full.write_to_replicas(f'key_{i}', f'value_{i}')
        start_time = time.time()
        for i in range(self.range_to_test):
            self.replication_manager_full.read_from_replicas(f'key_{i}')
        end_time = time.time()
        TestPerformance.results['Read performance (full)'] = end_time - start_time

    def test_fail_recover_performance_full(self):
        for i in range(self.range_to_test):
            self.replication_manager_full.write_to_replicas(f'key_{i}', f'value_{i}')
        start_time = time.time()
        for node_id in range(self.nodes_db):
            self.replication_manager_full.fail_node(node_id)
        fail_end_time = time.time()
        TestPerformance.results['Fail nodes performance (full)'] = fail_end_time - start_time

        start_time = time.time()
        for node_id in range(self.nodes_db):
            self.replication_manager_full.recover_node(node_id)
        recover_end_time = time.time()
        TestPerformance.results['Recover nodes performance (full)'] = recover_end_time - start_time

    def test_write_performance_consistent(self):
        start_time = time.time()
        for i in range(self.range_to_test):
            self.replication_manager_consistent.write_to_replicas(f'key_{i}', f'value_{i}')
        end_time = time.time()
        TestPerformance.results['Write performance (consistent)'] = end_time - start_time

    def test_read_performance_consistent(self):
        for i in range(self.range_to_test):
            self.replication_manager_consistent.write_to_replicas(f'key_{i}', f'value_{i}')
        start_time = time.time()
        for i in range(self.range_to_test):
            self.replication_manager_consistent.read_from_replicas(f'key_{i}')
        end_time = time.time()
        TestPerformance.results['Read performance (consistent)'] = end_time - start_time

    def test_fail_recover_performance_consistent(self):
        for i in range(self.range_to_test):
            self.replication_manager_consistent.write_to_replicas(f'key_{i}', f'value_{i}')
        start_time = time.time()
        for node_id in range(self.nodes_db):
            self.replication_manager_consistent.fail_node(node_id)
        fail_end_time = time.time()
        TestPerformance.results['Fail nodes performance (consistent)'] = fail_end_time - start_time

        start_time = time.time()
        for node_id in range(self.nodes_db):
            self.replication_manager_consistent.recover_node(node_id)
        recover_end_time = time.time()
        TestPerformance.results['Recover nodes performance (consistent)'] = recover_end_time - start_time

    @classmethod
    def tearDownClass(cls):
        # Riepilogo finale dei risultati
        print("\n\n--- Performance Results ---")
        for test, duration in cls.results.items():
            print(f'{test}: {duration:.4f} seconds')

if __name__ == '__main__':
    unittest.main()
