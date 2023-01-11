import os


class MyFile:
    @staticmethod
    def excluir_arquivo(arquivo):
        try:
            if os.path.exists(arquivo):
                os.remove(arquivo)
        except Exception as ex:
            raise Exception(ex)

    def excluir_arquivo_xml(self, caminho, nome_arquivo):
        arquivo = os.path.join(caminho, f"{nome_arquivo}.xml")
        self.excluir_arquivo(arquivo)

    def excluir_arquivo_ack(self, caminho, nome_arquivo):
        arquivo = os.path.join(caminho, f"{nome_arquivo}.ack")
        self.excluir_arquivo(arquivo)