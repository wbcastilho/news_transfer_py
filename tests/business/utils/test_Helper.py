import unittest
from src.business.utils.Helper import Helper


class TestHelper(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_substituir_espaco_por_underline(self):
        texto = "Teste 1"
        expected = "Teste_1"

        self.assertEqual(expected, Helper.substituir_espaco_por_underline(texto))

    def test_remover_acentuacao(self):
        texto = "Testéãç"
        expected = "Testeac"

        self.assertEqual(expected, Helper.remover_acentuacao(texto))

    def test_pegar_nome_do_arquivo(self):
        texto = "C:/Users/Manutencao.sm/Desktop/VIDEOS TESTE/2006_BDC_BO PETS CINOMOSE_.MXF"
        expected = "2006_BDC_BO PETS CINOMOSE_"

        self.assertEqual(expected, Helper.pegar_nome_do_arquivo(texto))

    def test_remover_caracteres_especiais(self):
        texto = "!Teste"
        expected = "Teste"

        self.assertEqual(expected, Helper.remover_caracteres_especiais(texto))

    def test_exibir_retranca(self):
        texto = "C:/Users/Manutencao.sm/Desktop/VIDEOS TESTE/2006_BDC_BO PETS !CINOMÔSE_.MXF"
        expected = "2006_BDC_BO_PETS_CINOMOSE_"

        self.assertEqual(expected, Helper.exibir_retranca(texto))

    def test_pegar_caminho_do_arquivo(self):
        texto = "C:/Users/Manutencao.sm/Desktop/VIDEOS TESTE/2006_BDC_BO PETS CINOMOSE_.MXF"
        expected = "C:/Users/Manutencao.sm/Desktop/VIDEOS TESTE"

        self.assertEqual(expected, Helper.pegar_caminho_do_arquivo(texto))


if __name__ == '__main__':
    unittest.main(verbosity=2)
