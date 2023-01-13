import unittest
from src.business.adapters.MyJSON import MyJSON


class TestMyJSON(unittest.TestCase):
    """ Método chamado antes de cada teste """
    def setUp(self) -> None:
        self.configuration = {
            'servidor': "C:/",
            'servidor2': "D:/",
            'habilitar_servidor2': 0,
            'timeout_ack': 15
        }

    """ Método chamado depois de cada teste """
    def tearDown(self) -> None:
        pass

    def test_read(self):
        self.configuration['servidor'] = ''
        my_json = MyJSON('tests\\files\\configuration.json', self.configuration)
        my_json.read()
        self.assertTrue(self.configuration["servidor"] == "C:/")
        self.assertTrue(self.configuration["servidor2"] == "D:/")
        self.assertEqual(self.configuration["habilitar_servidor2"], 0)
        self.assertEqual(self.configuration["timeout_ack"], 15)

    def test_write(self):
        my_json = MyJSON('tests\\files\\configuration_write.json', self.configuration)
        my_json.write()

        my_json.read()
        self.assertTrue(self.configuration["servidor"] == "C:/")
        self.assertTrue(self.configuration["servidor2"] == "D:/")
        self.assertEqual(self.configuration["habilitar_servidor2"], 0)
        self.assertEqual(self.configuration["timeout_ack"], 15)


if __name__ == '__main__':
    unittest.main(verbosity=2)
