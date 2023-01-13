import unittest
from src.business.adapters.AckXML import AckXML


class TestAckXML(unittest.TestCase):
    """ Método chamado antes de cada teste """
    def setUp(self) -> None:
        pass

    """ Método chamado depois de cada teste """
    def tearDown(self) -> None:
        pass

    def test_read_return_tuple(self):
        result = AckXML.read(caminho="tests\\files\\", arquivo="TESTE.ack")
        self.assertTrue(
            type(result) == tuple
            and result[0] == "0"
            and result[1] == "OK")


if __name__ == '__main__':
    unittest.main(verbosity=2)
