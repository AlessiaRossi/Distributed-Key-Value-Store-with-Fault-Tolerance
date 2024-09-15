import unittest
import time
from app.models import ReplicationManager

# Test performance
class TestPerformance(unittest.TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.replication_manager = None
        self.range_to_test = 10
        self.nodes_db = 3
        self.replication_factor = 3

    def setUp(self):
        self.replication_manager_full = ReplicationManager(nodes_db=self.nodes_db, strategy='full', replication_factor=self.replication_factor)
        self.replication_manager_consistent = ReplicationManager(nodes_db=self.nodes_db, strategy='consistent', replication_factor=self.replication_factor)

    # Test performance of the write, read, fail, and recover operations for both replication strategies.
    def test_write_performance_full(self):
        start_time = time.time()
        for i in range(self.range_to_test):
            self.replication_manager_full.write_to_replicas(f'key_{i}', f'value_{i}')
        end_time = time.time()
        print(f'Write performance (full): {end_time - start_time} seconds')

    def test_read_performance_full(self):
        for i in range(self.range_to_test):
            self.replication_manager_full.write_to_replicas(f'key_{i}', f'value_{i}')
        start_time = time.time()
        for i in range(self.range_to_test):
            self.replication_manager_full.read_from_replicas(f'key_{i}')
        end_time = time.time()
        print(f'Read performance (full): {end_time - start_time} seconds')

    def test_fail_recover_performance_full(self):
        for i in range(self.range_to_test):
            self.replication_manager_full.write_to_replicas(f'key_{i}', f'value_{i}')
        start_time = time.time()
        for node_id in range(3):
            self.replication_manager_full.fail_node(node_id)
        end_time = time.time()
        print(f'Fail nodes performance (full): {end_time - start_time} seconds')
        start_time = time.time()
        for node_id in range(3):
            self.replication_manager_full.recover_node(node_id)
        end_time = time.time()
        print(f'Recover nodes performance (full): {end_time - start_time} seconds')

    def test_write_performance_consistent(self):
        start_time = time.time()
        for i in range(self.range_to_test):
            self.replication_manager_consistent.write_to_replicas(f'key_{i}', f'value_{i}')
        end_time = time.time()
        print(f'Write performance (consistent): {end_time - start_time} seconds')

    def test_read_performance_consistent(self):
        for i in range(self.range_to_test):
            self.replication_manager_consistent.write_to_replicas(f'key_{i}', f'value_{i}')
        start_time = time.time()
        for i in range(self.range_to_test):
            self.replication_manager_consistent.read_from_replicas(f'key_{i}')
        end_time = time.time()
        print(f'Read performance (consistent): {end_time - start_time} seconds')

    def test_fail_recover_performance_consistent(self):
        for i in range(self.range_to_test):
            self.replication_manager_consistent.write_to_replicas(f'key_{i}', f'value_{i}')
        start_time = time.time()
        for node_id in range(3):
            self.replication_manager_consistent.fail_node(node_id)
        end_time = time.time()
        print(f'Fail nodes performance (consistent): {end_time - start_time} seconds')
        start_time = time.time()
        for node_id in range(3):
            self.replication_manager_consistent.recover_node(node_id)
        end_time = time.time()
        print(f'Recover nodes performance (consistent): {end_time - start_time} seconds')


if __name__ == '__main__':
    unittest.main()