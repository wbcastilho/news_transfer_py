import json
from src.business.dto.Config import Config


class MyJSON:
    def __init__(self, file, configuration):
        self.file = file
        self.configuration = configuration

    def write(self) -> None:
        config = Config(self.configuration['servidor'],
                        self.configuration['servidor2'],
                        self.configuration['habilitar_servidor2'],
                        self.configuration['timeout_ack'],
                        self.configuration['usuario'],
                        self.configuration['grupos'],
                        self.configuration['remover'])

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
                self.configuration['servidor2'] = config.servidor2
                self.configuration['habilitar_servidor2'] = config.habilitar_servidor2
                self.configuration['timeout_ack'] = config.timeout_ack
                self.configuration['usuario'] = config.usuario
                self.configuration['grupos'] = config.grupos
                self.configuration['remover'] = config.remover
        except PermissionError:
            raise PermissionError("Sem permissão para abrir o arquivo de configuração.")
        except FileNotFoundError:
            raise FileNotFoundError("Arquivo de configuração não encontrado.")
        except Exception as error:
            raise Exception("Falha ao abrir arquivo de configuração.")
