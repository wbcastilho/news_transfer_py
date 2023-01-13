from random import randrange


class MyRandom:
    @staticmethod
    def gerar_codigo():
        codigo = randrange(0, 999999)
        return f"ENL_{str(codigo).zfill(6)}"

