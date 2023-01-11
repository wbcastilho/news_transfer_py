import os


class MyFile:
    @staticmethod
    def _excluir(arquivo):
        try:
            if os.path.exists(arquivo):
                os.remove(arquivo)
        except Exception as ex:
            raise Exception(ex)

    def _excluir_arquivo(self, caminho, nome_arquivo, extensao):
        arquivo = os.path.join(caminho, f"{nome_arquivo}.{extensao}")
        self._excluir(arquivo)

    def excluir_arquivo_mxf(self, caminho, nome_arquivo):
        self._excluir_arquivo(caminho, nome_arquivo, "mxf")

    def excluir_arquivo_xml(self, caminho, nome_arquivo):
        self._excluir_arquivo(caminho, nome_arquivo, "xml")

    def excluir_arquivo_ack(self, caminho, nome_arquivo):
        self._excluir_arquivo(caminho, nome_arquivo, "ack")

