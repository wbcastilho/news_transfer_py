import unittest
from src.business.adapters.VideoXML import VideoXML


class TestVideoXML(unittest.TestCase):
    """ Método chamado antes de cada teste """
    def setUp(self) -> None:
        pass

    """ Método chamado depois de cada teste """
    def tearDown(self) -> None:
        pass

    def test_create_write_xml_file(self):
        info = {
            'codigo': '000',
            'arquivo': 'Teste_arquivo',
            'titulo': 'Teste_arquivo',
            'grupo': 'Editores',
            'operador': 'Operador',
            'markIn': '000',
            'markOut': '000',
            'remover': '0'
        }

        VideoXML.create(caminho="tests\\files\\", arquivo="video.xml", dto=info)

        result = VideoXML.read(caminho="tests\\files\\", arquivo="video.xml")
        self.assertTrue(
            type(result) == tuple
            and result[0] == "000"
            and result[1] == "Teste_arquivo"
            and result[2] == "Teste_arquivo"
            and result[3] == "Editores"
            and result[4] == "Operador"
            and result[5] == "000"
            and result[6] == "000"
            and result[7] == "0")


if __name__ == '__main__':
    unittest.main(verbosity=2)
