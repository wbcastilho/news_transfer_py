import os
import unittest
from src.business.adapters.MyFile import MyFile


class TestMyFile(unittest.TestCase):
    """ Método chamado antes de cada teste """
    def setUp(self) -> None:
        arquivo = open("tests\\files\\file.xml", "a")

    """ Método chamado depois de cada teste """
    def tearDown(self) -> None:
        pass

    def test_excluir_arquivo_xml(self):
        MyFile.excluir_arquivo_xml('tests\\files\\', 'file')

        if not os.path.exists('tests\\files\\file.xml'):
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
