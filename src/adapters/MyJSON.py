import json
from src.dto.Config import Config


class MyJSON:
    def __init__(self, file, configuration):
        self.file = file
        self.configuration = configuration

    def write(self) -> None:
        config = Config(self.configuration['servidor'])

        try:
            with open(self.file, 'w') as f:
                json.dump(config.__dict__, f)
        except Exception:
            raise Exception("Erro ao salvar arquivo de configuração.")

    def read(self) -> None:
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
                config = Config(**data)
                self.configuration['servidor'] = config.servidor
        except PermissionError:
            raise PermissionError("Sem permissão para abrir o arquivo de configuração.")
        except FileNotFoundError:
            raise FileNotFoundError("Arquivo de configuração não encontrado.")
        except Exception as error:
            raise Exception("Falha ao abrir arquivo de configuração.")