from app import create_app
import unittest

app = create_app()

# Test del sistema
class TestDistributedKVStore(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_write_read(self):
        response = self.client.post('/write', json={'key': 'key1', 'value': 'value1'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/read/key1')
        data = response.get_json()
        self.assertEqual(data['value'], 'value1')
        self.assertIn('Read from replica', data['message'])

    def test_fail_recover(self):
        # Scrivere il dato
        self.client.post('/write', json={'key': 'key2', 'value': 'value2'})

        # Fallimento di un nodo
        self.client.post('/fail/1')
        
        # Verifica che la chiave "key2" sia disponibile nelle altre repliche
        response = self.client.get('/read/key2')
        data = response.get_json()
        self.assertEqual(data['value'], 'value2')  # Il dato dovrebbe ancora essere presente nelle altre repliche
        self.assertIn('Read from replica', data['message'])

        # Recupero del nodo
        self.client.post('/recover/1')
        
        # Verifica che il nodo recuperato abbia recuperato i dati
        response = self.client.get('/read/key2')
        data = response.get_json()
        self.assertEqual(data['value'], 'value2')  # Il dato dovrebbe essere stato recuperato
        self.assertIn('Read from replica', data['message'])

    def test_fail_all_replicas(self):
        # Scrivere i dati
        self.client.post('/write', json={'key': 'key1', 'value': 'value1'})
        self.client.post('/write', json={'key': 'key2', 'value': 'value2'})

        # Fallimento di tutte le repliche
        self.client.post('/fail/0')
        self.client.post('/fail/1')
        self.client.post('/fail/2')
        
        # Verifica che la lettura fallisca
        response = self.client.get('/read/key1')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 'Key not found')
        self.assertEqual(data['message'], 'All replicas failed or key not found')

        # Recupero di una replica
        self.client.post('/recover/0')
        
        # Verifica che la replica recuperata abbia recuperato tutti i dati
        response = self.client.get('/read/key1')
        data = response.get_json()
        self.assertEqual(data['value'], 'value1')
        self.assertIn('Read from replica', data['message'])

        response = self.client.get('/read/key2')
        data = response.get_json()
        self.assertEqual(data['value'], 'value2')
        self.assertIn('Read from replica', data['message'])

if __name__ == '__main__':
    import sys
    if 'test' in sys.argv:
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    else:
        app.run(debug=True)
