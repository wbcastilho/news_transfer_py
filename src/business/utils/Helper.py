import re
from unidecode import unidecode


class Helper:
    @staticmethod
    def possui_caractere_especial(texto: str) -> bool:
        # Definindo a expressão regular para encontrar caracteres especiais, exceto "_" e "-"
        padrao = r"[^a-zA-Z0-9_-]"

        if re.search(padrao, texto):
            return True
        else:
            return False

    @staticmethod
    def substituir_espaco_por_underline(texto: str) -> str:
        return texto.replace(" ", "_")

    @staticmethod
    def remover_acentuacao(texto: str) -> str:
        return unidecode(texto)

    @staticmethod
    def pegar_nome_do_arquivo(texto: str) -> str:
        arquivo = texto.split('/')
        nome_arquivo = arquivo[-1].split('.')
        return nome_arquivo[0]

    @staticmethod
    def remover_caracteres_especiais(texto):
        """
        Remove caracteres especiais exceto underline e hífen
        :param texto:
        :return:
        """
        texto_limpo = re.sub(r'[^\w\s-]', '', texto)
        return texto_limpo

    @staticmethod
    def exibir_retranca(texto):
        return Helper.remover_caracteres_especiais(
            Helper.remover_acentuacao(
                Helper.substituir_espaco_por_underline(
                    Helper.pegar_nome_do_arquivo(texto)
                )
            )
        )

    @staticmethod
    def pegar_caminho_do_arquivo(texto: str) -> str:
        arquivo = texto.split('/')
        caminho_arquivo = arquivo[:-1]
        result = "/".join(caminho_arquivo)
        return result
