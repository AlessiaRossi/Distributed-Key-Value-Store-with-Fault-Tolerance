import unittest
import time
from app.models import ReplicationManager

# Test performance
class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.replication_manager = ReplicationManager(replication_factor=3)

# Test performance of the write, read, fail, and recover operations
    def test_write_performance(self):
        start_time = time.time()
        for i in range(100):
            self.replication_manager.write_to_replicas(f'key_{i}', f'value_{i}')
        end_time = time.time()
        print(f'Write performance: {end_time - start_time} seconds')

    def test_read_performance(self):
        for i in range(100):
            self.replication_manager.write_to_replicas(f'key_{i}', f'value_{i}')
        start_time = time.time()
        for i in range(100):
            self.replication_manager.read_from_replicas(f'key_{i}')
        end_time = time.time()
        print(f'Read performance: {end_time - start_time} seconds')

    def test_fail_recover_performance(self):
        for i in range(100):
            self.replication_manager.write_to_replicas(f'key_{i}', f'value_{i}')

        start_time = time.time()
        for node_id in range(3):
            self.replication_manager.fail_node(node_id)
        end_time = time.time()
        print(f'Fail nodes performance: {end_time - start_time} seconds')

        start_time = time.time()
        for node_id in range(3):
            self.replication_manager.recover_node(node_id)
        end_time = time.time()
        print(f'Recover nodes performance: {end_time - start_time} seconds')


if __name__ == '__main__':
    unittest.main()