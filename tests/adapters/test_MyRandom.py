import unittest
from src.adapters.MyRandom import MyRandom


class TestMyJSON(unittest.TestCase):
    """ Método chamado antes de cada teste """
    def setUp(self) -> None:
        pass

    """ Método chamado depois de cada teste """
    def tearDown(self) -> None:
        pass

    def test_gerar_codigo_retorna_str_com_10_caracteres_e_inicio_igual_a_ENL_(self):
        result = MyRandom.gerar_codigo()
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0:4], 'ENL_')


if __name__ == '__main__':
    unittest.main(verbosity=2)
