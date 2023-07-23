import os
import pathlib


class MyFile:
    @staticmethod
    def _excluir(arquivo):
        try:
            if os.path.exists(arquivo):
                os.remove(arquivo)
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def _excluir_arquivo(cls, caminho, nome_arquivo, extensao):
        arquivo = os.path.join(caminho, f"{nome_arquivo}.{extensao}")
        cls._excluir(arquivo)

    @classmethod
    def excluir_arquivo_mxf(cls, caminho, nome_arquivo):
        cls._excluir_arquivo(caminho, nome_arquivo, "mxf")

    @classmethod
    def excluir_arquivo_xml(cls, caminho, nome_arquivo):
        cls._excluir_arquivo(caminho, nome_arquivo, "xml")

    @classmethod
    def excluir_arquivo_ack(cls, caminho, nome_arquivo):
        cls._excluir_arquivo(caminho, nome_arquivo, "ack")

    @staticmethod
    def extensao_arquivo(arquivo):
        print(arquivo)
        extensao = pathlib.Path(arquivo).suffix
        return extensao

