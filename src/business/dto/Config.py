class Config:
    def __init__(self, servidor, servidor2, habilitar_servidor2, timeout_ack, usuario, grupos, remover):
        self.servidor = servidor
        self.servidor2 = servidor2
        self.habilitar_servidor2 = habilitar_servidor2
        self.timeout_ack = timeout_ack
        self.usuario = usuario
        self.grupos = grupos
        self.remover = remover
