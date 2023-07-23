import re


class Helper:
    @staticmethod
    def possui_caractere_especial(texto: str) -> bool:
        # Definindo a expressão regular para encontrar caracteres especiais, exceto "_" e "-"
        padrao = r"[^a-zA-Z0-9_-]"

        if re.search(padrao, texto):
            return True
        else:
            return False
