import os
import cv2
import pathlib
import shutil
import threading
import tkVideoPlayer
import tkinter as ttk1
from pathlib import Path
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import messagebox
from ttkbootstrap.constants import *

from src.app.forms.LogForm import LogsForm
from src.business.utils.Helper import Helper
from src.business.adapters.AckXML import AckXML
from src.business.adapters.MyJSON import MyJSON
from src.business.adapters.MyFile import MyFile
from src.business.utils.StopWatch import StopWatch
from src.app.forms.SettingsForm import SettingsForm
from src.business.adapters.VideoXML import VideoXML
from src.business.adapters.MyRandom import MyRandom
from src.business.utils.ConvertVideo import ConvertVideo
from src.business.services.LogService import LogService
from src.data.repository.LogRepository import LogRepository
from src.business.exceptions.SameFileError import SameFileError
from src.business.exceptions.CreateXMLError import CreateXMLError
from src.business.exceptions.TimeoutCopyError import TimeoutCopyError
from src.business.exceptions.TimeoutAckError import TimeoutAckError
from src.business.exceptions.SpecialFileError import SpecialFileError
from src.business.exceptions.ArquivoAckCanceladoError import ArquivoAckCanceladoError
from src.business.exceptions.ArquivoAckFalhaError import ArquivoAckFalhaError
from src.business.exceptions.ArquivoVideoInvalidoError import ArquivoVideoInvalidoError
from src.business.exceptions.ArquivoVideoNotFoundError import ArquivoVideoNotFoundError
from src.business.exceptions.CodigoMaterialError import CodigoMaterialError
from src.business.exceptions.CopiaCanceladaError import CopiaCanceladaError
from src.business.exceptions.TransferirArquivoFalhaError import TransferirArquivoFalhaError
from src.business.exceptions.CopiarArquivoError import CopiarArquivoError


class MainForm(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pack(fill=BOTH, expand=YES)
        self.configuration = {
            'servidor': "",
            'servidor2': "",
            'habilitar_servidor2': 0,
            'timeout_ack': 15,
            'usuario': "",
            'grupos': [],
            'remover': 0
        }

        # Constantes
        self.TRANSFERIDO_COM_SUCESSO = 0
        self.MATERIAL_JA_EXISTENTE = 4
        self.ARQUIVO_VIDEO_NAO_ENCONTRADO = 8
        self.ARQUIVO_VIDEO_INVALIDO = 9
        self.FALHA_TRANSFERIR_ARQUIVO = 10
        self.FALHA_AO_COPIAR_ARQUIVO = 100
        self.COPIA_CANCELADA = 101
        self.FALHA_AO_GERAR_XML = 102
        self.TIMEOUT_COPY_ERROR = 103
        self.ACK_RECEBIDO = 0
        self.RECEPCAO_ACK_CANCELADO = 201
        self.ACK_FALHA = 202
        self.TIMEOUT_ACK_ERROR = 203
        self.ERRO_DESCONHECIDO = 300

        self.photo_images = []
        self.enviar = False
        self.situacao_copia_servidor1 = False
        self.situacao_copia_servidor2 = False
        self.result_destino1 = False
        self.result_destino2 = False
        self.stop_watch = None

        self.arquivo = ttk.StringVar()
        self.titulo = ttk.StringVar()
        self.grupo = ttk.StringVar()
        self.progress_value = ttk.IntVar()

        self.grupo_values = []
        self.button_action = None
        self.button_browse = None
        self.entry_arquivo = None
        self.entry_titulo = None
        self.combobox_grupo = None
        self.progressbar = None
        self.progressbar2 = None
        self.label_porcent = None
        self.label_porcent2 = None
        self.progress_slider = None
        self.video = None
        self.button_play_pause = None
        self.label_thumbnail = None

        self.init_database()
        self.read_config()
        self.init_combobox()
        self.associate_icons()
        self.create_buttonbar()
        self.create_labels_frame()
        self.create_progressbar_frame()

    @staticmethod
    def init_database():
        try:
            LogRepository.create_table()
        except Exception as err:
            messagebox.showwarning(title="Atenção", message=f"Falha ao se conectar com o banco de dados. {err}")

    def associate_icons(self) -> None:
        image_files = {
            # 'play-icon': 'icons8-reproduzir-24.png',
            'play-icon': 'icons8-play-24.png',
            'pause-icon': 'icons8-pausa-24.png',
            'stop-icon': 'icons8-parar-24.png',
            'settings-icon': 'icons8-configuracoes-24.png',
            'log-icon': 'icons8-log-24.png'
        }

        img_path = Path(__file__).parent / '../assets'
        for key, val in image_files.items():
            _path = img_path / val
            self.photo_images.append(ttk.PhotoImage(name=key, file=_path))

    def init_combobox(self) -> None:
        for item in self.configuration["grupos"]:
            self.grupo_values.append(item)

    def create_buttonbar(self) -> None:
        buttonbar = ttk.Frame(self, style='primary.TFrame')
        buttonbar.pack(fill=X, pady=1, side=TOP)

        btn = ttk.Button(
            master=buttonbar,
            text='Configurações',
            image='settings-icon',
            compound=LEFT,
            command=self.on_settings
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=(1, 0), pady=1)

        btn = ttk.Button(
            master=buttonbar,
            text='Logs',
            image='log-icon',
            compound=LEFT,
            command=self.on_logs
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=0, pady=1)

    def create_labels_frame(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x")

        self.create_enviar_frame(frame)
        self.create_preview_frame(frame)

    def create_enviar_frame(self, parent) -> None:
        label_frame = ttk.Labelframe(parent, text='Enviar')
        label_frame.pack(side=LEFT, padx=(20, 0), pady=(5, 15))
        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=15)

        label = ttk.Label(frame, text="Arquivo", font=("Helvetica", 10))
        label.grid(row=0, column=0, padx=1, sticky=ttk.NE)

        self.entry_arquivo = ttk1.Text(frame, width=70, height=3, wrap=WORD, state="disabled", font=("Helvetica", 10),
                                       foreground="red")
        self.entry_arquivo.grid(row=0, column=1, padx=2, sticky=ttk.W)

        self.button_browse = ttk.Button(frame, text="Selecionar Arquivo", bootstyle=(INFO, OUTLINE),
                                        command=self.on_browse, style='primary.Outline.TButton')
        self.button_browse.grid(row=0, column=2, padx=2, sticky=ttk.NE)

        label = ttk.Label(frame, text="Retranca / Título", font=("Helvetica", 10))
        label.grid(row=1, column=0, padx=1, pady=(20, 0), sticky=ttk.E)
        self.entry_titulo = ttk.Entry(frame, width=50, textvariable=self.titulo, font=("Helvetica", 10))
        self.entry_titulo.grid(row=1, column=1, padx=2, pady=(20, 0), sticky=ttk.W)

        # Evento ao perder o focu - retira os espaços do início e do fim do titulo
        self.entry_titulo.bind("<FocusOut>", lambda event: self.titulo.set(self.titulo.get().strip()))
        self.titulo.trace('w', self.transform_uppercase)

        label = ttk.Label(frame, text="Grupo", font=("Helvetica", 10))
        label.grid(row=2, column=0, padx=1, pady=(20, 0), sticky=ttk.E)
        self.combobox_grupo = ttk.Combobox(frame, width=20, justify="center", textvariable=self.grupo,
                                           font=("Helvetica", 10), values=self.grupo_values)
        self.combobox_grupo.grid(row=2, column=1, padx=2, pady=(20, 0), sticky=ttk.W)
        self.combobox_grupo.bind("<<ComboboxSelected>>",
                                 lambda event:  self.combobox_grupo.configure(bootstyle="default"))

        self.button_action = ttk.Button(frame, width=100, text='Enviar ao servidor', command=lambda: self.on_action(),
                                        bootstyle='primary', style='primary.TButton')
        self.button_action.grid(row=3, column=0, columnspan=3, padx=0, pady=(20, 0))

    def create_preview_frame(self, parent):
        label_frame = ttk.Labelframe(parent, text='Preview', height=200)
        label_frame.pack(side=RIGHT, padx=20, pady=(5, 15), anchor=ttk.N)

        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=35)

        video_frame = ttk.Frame(frame, bootstyle="dark", width=275, height=140)
        video_frame.grid(row=0)

        self.video = tkVideoPlayer.TkinterVideo(video_frame, scaled=True, background="black")
        self.video.bind("<<Duration>>", self.update_duration)
        self.video.bind("<<SecondChanged>>", self.update_scale)
        self.video.bind("<<Ended>>", self.video_ended)

        player_frame = ttk.Frame(frame)
        player_frame.grid(row=1, pady=(10, 4))

        self.button_play_pause = ttk.Button(
            master=player_frame,
            image='play-icon',
            bootstyle="light",
            compound=LEFT,
            command=self.play
        )
        self.button_play_pause.pack(side=LEFT, padx=(0, 10))

        self.progress_slider = ttk1.Scale(player_frame, variable=self.progress_value, length=150,
                                          orient="horizontal", command=self.seek)
        self.progress_slider.pack(side=RIGHT)
        self.progress_slider.configure(state="disabled")

        self.label_thumbnail = ttk.Label(frame, bootstyle="info")

    def create_progressbar_frame(self):
        frame = ttk.Frame(self, height=20)
        frame.pack(side=LEFT, padx=20, pady=(5, 15))

        self.progressbar = ttk.Progressbar(
            master=frame,
            length=300,
            bootstyle="success"
        )
        self.progressbar.pack_forget()

        self.label_porcent = ttk.Label(frame, text="0%")
        self.label_porcent.pack_forget()

        frame2 = ttk.Frame(self, height=20)
        frame2.pack(side=LEFT, padx=20, pady=(5, 15))

        self.progressbar2 = ttk.Progressbar(
            master=frame2,
            length=300,
            bootstyle="success"
        )
        self.progressbar2.pack_forget()

        self.label_porcent2 = ttk.Label(frame2, text="0%")
        self.label_porcent2.pack_forget()

    def load_video(self, file_path):
        if file_path:
            print(file_path)
            self.video.load(file_path)
            self.video.place(x=0, y=0, width=275, height=140)
            self.generate_thumbnail(file_path)

    def play(self):
        if self.arquivo.get() != '':
            if self.button_play_pause['image'] == ('play-icon',):
                self.button_play_pause['image'] = 'pause-icon'
                self.progress_slider.configure(state="normal")
                self.video.play()
            else:
                self.button_play_pause['image'] = 'play-icon'
                self.video.pause()

            self.label_thumbnail.place_forget()
        else:
            messagebox.showwarning(title="Atenção", message="Para reproduzir em Preview selecione antes um arquivo.")

    def stop(self):
        self.video.pause()
        self.progress_slider.set(0)
        self.progress_slider.configure(state="disabled")
        self.button_play_pause['image'] = 'play-icon'

    def seek(self, value):
        self.video.seek(int(value))

    def update_scale(self, event):
        self.progress_value.set(int(self.video.current_duration()))

    def update_duration(self, event):
        duration = self.video.video_info()["duration"]
        self.progress_slider["to"] = duration

    def video_ended(self, event):
        self.progress_slider.set(self.progress_slider["to"])
        self.progress_slider.set(0)
        self.label_thumbnail.place(x=0, y=0)
        self.progress_slider.configure(state="disabled")
        self.button_play_pause['image'] = 'play-icon'

    def generate_thumbnail(self, video_path):
        cap = cv2.VideoCapture(video_path)

        # Verificar se o vídeo foi aberto corretamente
        if not cap.isOpened():
            print("Erro ao abrir o vídeo.")
            return

        # Ler o primeiro quadro do vídeo
        ret, frame = cap.read()

        # Converter o quadro para o formato RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Criar uma imagem PIL a partir do quadro
        image = Image.fromarray(frame_rgb)

        # Definir as dimensões
        width = 275
        height = 140

        # # Calcular a altura proporcionalmente à largura desejada
        # aspect_ratio = image.width / image.height
        # height = int(width / aspect_ratio)

        # Redimensionar a imagem para o tamanho desejado
        image = image.resize((width, height))

        # Exibir a imagem no Tkinter
        image_tk = ImageTk.PhotoImage(image)
        self.label_thumbnail.configure(image=image_tk)
        self.label_thumbnail.image = image_tk
        self.label_thumbnail.place(x=0, y=0)

        # Liberar os recursos
        cap.release()

    def transform_uppercase(self, *args):
        self.entry_titulo.configure(bootstyle="default")
        self.titulo.set(self.titulo.get().upper())

    def read_config(self) -> None:
        try:
            if not os.path.exists('config.json'):
                return

            my_json = MyJSON('config.json', self.configuration)
            my_json.read()
        except PermissionError as err:
            messagebox.showwarning(title="Atenção", message=err)
        except FileNotFoundError as err:
            messagebox.showwarning(title="Atenção", message=err)
        except Exception as err:
            messagebox.showwarning(title="Atenção", message=err)

    def on_settings(self) -> None:
        if not self.enviar:
            setting_form = ttk.Toplevel()
            setting_form.title("Configurações")
            setting_form.iconbitmap('src/app/assets/favicon.ico')
            setting_form.grab_set()
            setting_form.resizable(False, False)
            SettingsForm(setting_form, self)
        else:
            messagebox.showwarning(title="Atenção", message="Para abrir a janela de configurações é necessário antes "
                                                            "parar a monitoração clicando no botão Parar.")

    @staticmethod
    def on_logs():
        logs_form = ttk.Toplevel()
        logs_form.title("Logs")
        logs_form.iconbitmap('src/app/assets/favicon.ico')
        logs_form.grab_set()
        logs_form.geometry("800x400")
        logs_form.resizable(False, False)
        LogsForm(logs_form)

    def on_browse(self) -> None:
        filetypes = (
            ('MXF Files', '*.mxf'),
        )

        filename = filedialog.askopenfilename(title='Selecionar Arquivo', initialdir='c:/', filetypes=filetypes)

        if filename:
            self.arquivo.set(filename)

            # Habilita a edição de texto
            self.entry_arquivo.config(state=NORMAL)

            # Limpa o texto
            self.entry_arquivo.delete("1.0", END)

            # Insere o texto
            self.entry_arquivo.insert(END, filename)

            # Intervalo do texto que deseja alterar a cor
            self.entry_arquivo.tag_add("color_tag", "1.0", END)

            # Altera a cor do texto
            self.entry_arquivo.tag_config("color_tag", foreground="#BBB")

            # Desabilita a edição de texto
            self.entry_arquivo.config(state=DISABLED)

            self.load_video(filename)

    def on_action(self) -> None:
        if not self.enviar:
            if self.validate():
                self.enviar = True
                self.change_button_action_state(False)
                self.show_progressbar(True)

                if self.configuration["habilitar_servidor2"] == 1:
                    self.show_progressbar(True, 2)

                t = threading.Thread(daemon=True, target=self.background_worker)
                t.start()
        else:
            self.enviar = False
            self.change_button_action_state(True)

    def background_worker(self):
        self.situacao_copia_servidor1 = self.FALHA_AO_COPIAR_ARQUIVO
        self.situacao_copia_servidor2 = self.FALHA_AO_COPIAR_ARQUIVO
        self.result_destino1 = self.FALHA_TRANSFERIR_ARQUIVO
        self.result_destino2 = self.FALHA_TRANSFERIR_ARQUIVO

        self.change_form_action_state(False)

        try:
            self.stop_watch = StopWatch()
            self.video.stop()

            codigo_material = MyRandom.gerar_codigo()

            thread1 = threading.Thread(daemon=True,
                                       target=self.copiar_servidor_2,
                                       args=(self.configuration["servidor2"],
                                             self.titulo.get(),
                                             self.arquivo.get(),
                                             "Servidor 2",
                                             codigo_material))

            thread2 = threading.Thread(daemon=True,
                                       target=self.copiar_servidor_1,
                                       args=(self.configuration["servidor"], self.titulo.get(),
                                             self.arquivo.get(),
                                             "Servidor 1", codigo_material))

            # Inicia as threads 1 e 2
            thread1.start()
            thread2.start()

            # Aguarda o término das threads 1 e 2
            thread1.join()
            thread2.join()

            thread3 = threading.Thread(daemon=True, target=self.checar_ack_servidor_2)
            thread4 = threading.Thread(daemon=True, target=self.checar_ack_servidor_1)

            # Inicia as threads 3 e 4
            thread3.start()
            thread4.start()

            # Aguarda o término das threads 3 e 4
            thread3.join()
            thread4.join()

            self.show_progressbar(False)
            self.show_progressbar(False, 2)
            self.update_label_progressbar(True, "100%")
            self.update_label_progressbar(True, "100%", 2)
            self.change_button_action_state(True)

            self.exibir_messagebox_e_log_concluido(self.result_destino1, self.result_destino2)

            if self.configuration["habilitar_servidor2"] == 1:
                MyFile.excluir_arquivo_ack(self.configuration["servidor2"], self.titulo.get())
            MyFile.excluir_arquivo_ack(self.configuration["servidor"], self.titulo.get())

            self.clean_fields()
            self.label_thumbnail.place_forget()
            self.video.place_forget()
        except Exception as ex:
            self.show_progressbar(False)
            self.show_progressbar(False, 2)
            self.set_progressbar_determinate(True)
            self.set_progressbar_determinate(True, 2)
            self.label_porcent["text"] = "0%"
            self.label_porcent2["text"] = "0%"
            self.change_button_action_state(True)
            LogService.save_error(f"{ex}")
            messagebox.showerror(title="Erro", message=ex)
        finally:
            self.enviar = False
            self.change_form_action_state(True)
            self.stop()

    def checar_ack_servidor_2(self):
        if self.configuration["habilitar_servidor2"] == 1:
            self.result_destino2 = self.ERRO_DESCONHECIDO

            try:
                if self.situacao_copia_servidor2 == self.FALHA_AO_COPIAR_ARQUIVO \
                        or self.situacao_copia_servidor2 == self.COPIA_CANCELADA\
                        or self.situacao_copia_servidor2 == self.FALHA_AO_GERAR_XML\
                        or self.situacao_copia_servidor2 == self.TIMEOUT_COPY_ERROR:
                    self.result_destino2 = self.situacao_copia_servidor2
                else:
                    self.label_porcent2["text"] = "Aguardando arquivo ACK do Servidor 2"

                    self.result_destino2 = self.checar_ack(self.configuration["servidor2"], self.titulo.get(), 2)

                    if self.result_destino2 == self.ACK_RECEBIDO:
                        self.progressbar2.pack_forget()
                        self.label_porcent2["text"] = "Arquivo ACK do Servidor 2 recebido com sucesso"
                    elif self.result_destino2 == self.ACK_FALHA:
                        self.progressbar2.pack_forget()
                        self.label_porcent2["text"] = "Erro desconhecido ao receber arquivo ACK Servidor 2"
                        self.excluir_arquivos(self.configuration["servidor2"], self.titulo.get())
            except ArquivoAckCanceladoError as ex:
                self.progressbar2.pack_forget()
                self.label_porcent2["text"] = "Cancelando checagem ACK no Servidor 2"
                self.excluir_arquivos(self.configuration["servidor2"], self.titulo.get())
                self.result_destino2 = self.RECEPCAO_ACK_CANCELADO
            except TimeoutAckError as ex:
                self.excluir_arquivos(self.configuration["servidor2"], self.titulo.get())
                self.result_destino2 = self.TIMEOUT_ACK_ERROR
            except ArquivoAckFalhaError as ex:
                self.progressbar2.pack_forget()
                self.label_porcent2["text"] = "Falha ao receber arquivo ACK no Servidor 2"
                self.excluir_arquivos(self.configuration["servidor2"], self.titulo.get())
                self.result_destino2 = self.ACK_FALHA
            except CodigoMaterialError as ex:
                self.progressbar2.pack_forget()
                self.label_porcent2["text"] = "Falha código material já existente no Servidor 2"
                self.excluir_arquivos(self.configuration["servidor2"], self.titulo.get())
                self.result_destino2 = self.MATERIAL_JA_EXISTENTE
            except ArquivoVideoNotFoundError as ex:
                self.progressbar2.pack_forget()
                self.label_porcent2["text"] = "Falha arquivo de vídeo não encontrado no Servidor 2"
                self.excluir_arquivos(self.configuration["servidor2"], self.titulo.get())
                self.result_destino2 = self.ARQUIVO_VIDEO_NAO_ENCONTRADO
            except ArquivoVideoInvalidoError as ex:
                self.progressbar2.pack_forget()
                self.label_porcent2["text"] = "Falha arquivo de vídeo inválido no Servidor 2"
                self.excluir_arquivos(self.configuration["servidor2"], self.titulo.get())
                self.result_destino2 = self.ARQUIVO_VIDEO_INVALIDO
            except TransferirArquivoFalhaError as ex:
                self.progressbar2.pack_forget()
                self.label_porcent2["text"] = "Falha ao transferir arquivo para o Servidor 2"
                self.excluir_arquivos(self.configuration["servidor2"], self.titulo.get())
                self.result_destino2 = self.FALHA_TRANSFERIR_ARQUIVO

    def checar_ack_servidor_1(self):
        try:
            self.result_destino1 = self.ERRO_DESCONHECIDO

            if self.situacao_copia_servidor1 == self.FALHA_AO_COPIAR_ARQUIVO \
                    or self.situacao_copia_servidor1 == self.COPIA_CANCELADA \
                    or self.situacao_copia_servidor1 == self.FALHA_AO_GERAR_XML \
                    or self.situacao_copia_servidor1 == self.TIMEOUT_COPY_ERROR:
                self.result_destino1 = self.situacao_copia_servidor1
            else:
                self.label_porcent["text"] = "Aguardando arquivo ACK do Servidor 1"

                self.result_destino1 = self.checar_ack(self.configuration["servidor"], self.titulo.get())

                if self.result_destino1 == self.ACK_RECEBIDO:
                    self.progressbar.pack_forget()
                    self.label_porcent["text"] = "Arquivo ACK do Servidor 1 recebido com sucesso"
                elif self.result_destino1 == self.ACK_FALHA:
                    self.progressbar.pack_forget()
                    self.label_porcent["text"] = "Erro desconhecido ao receber arquivo ACK Servidor 1"
                    self.excluir_arquivos(self.configuration["servidor"], self.titulo.get())
        except ArquivoAckCanceladoError as ex:
            self.progressbar.pack_forget()
            self.label_porcent["text"] = "Cancelando checagem ACK no Servidor 1"
            self.excluir_arquivos(self.configuration["servidor"], self.titulo.get())
            self.result_destino1 = self.RECEPCAO_ACK_CANCELADO
        except TimeoutAckError as ex:
            self.excluir_arquivos(self.configuration["servidor"], self.titulo.get())
            self.result_destino1 = self.TIMEOUT_ACK_ERROR
        except ArquivoAckFalhaError as ex:
            self.progressbar.pack_forget()
            self.label_porcent["text"] = "Falha ao receber arquivo ACK no Servidor 1"
            self.excluir_arquivos(self.configuration["servidor"], self.titulo.get())
            self.result_destino1 = self.ACK_FALHA
        except CodigoMaterialError as ex:
            self.progressbar.pack_forget()
            self.label_porcent["text"] = "Falha código material já existente no Servidor 1"
            self.excluir_arquivos(self.configuration["servidor"], self.titulo.get())
            self.result_destino1 = self.MATERIAL_JA_EXISTENTE
        except ArquivoVideoNotFoundError as ex:
            self.progressbar.pack_forget()
            self.label_porcent["text"] = "Falha arquivo de vídeo não encontrado no Servidor 1"
            self.excluir_arquivos(self.configuration["servidor"], self.titulo.get())
            self.result_destino1 = self.ARQUIVO_VIDEO_NAO_ENCONTRADO
        except ArquivoVideoInvalidoError as ex:
            self.progressbar.pack_forget()
            self.label_porcent["text"] = "Falha arquivo de vídeo inválido no Servidor 1"
            self.excluir_arquivos(self.configuration["servidor"], self.titulo.get())
            self.result_destino1 = self.ARQUIVO_VIDEO_INVALIDO
        except TransferirArquivoFalhaError as ex:
            self.progressbar.pack_forget()
            self.label_porcent["text"] = "Falha ao transferir arquivo para o Servidor 1"
            self.excluir_arquivos(self.configuration["servidor"], self.titulo.get())
            self.result_destino1 = self.FALHA_TRANSFERIR_ARQUIVO

    def copiar_servidor_2(self, destino, titulo, arquivo, server, codigo_material):
        if self.configuration["habilitar_servidor2"] == 1:
            print("Copia servidor 2")
            try:
                self.copiar_arquivo_e_gerar_xml(destino, titulo, arquivo, server, codigo_material, 2)
                self.situacao_copia_servidor2 = self.TRANSFERIDO_COM_SUCESSO
            except CopiaCanceladaError as ex:
                self.progressbar2.pack_forget()
                self.label_porcent2["text"] = "Cancelando copia para o Servidor 2"
                self.excluir_arquivos(destino, titulo)
                self.situacao_copia_servidor2 = self.COPIA_CANCELADA
            except TimeoutCopyError as ex:
                self.excluir_arquivos(destino, titulo)
                self.situacao_copia_servidor2 = self.TIMEOUT_COPY_ERROR
            except CreateXMLError as ex:
                self.progressbar2.pack_forget()
                self.label_porcent2["text"] = "Falha ao gerar arquivo XML para o Servidor 2"
                self.excluir_arquivos(destino, titulo)
                self.situacao_copia_servidor2 = self.FALHA_AO_GERAR_XML
            except (Exception, FileNotFoundError, SpecialFileError, ValueError) as ex:
                self.progressbar2.pack_forget()
                self.label_porcent2["text"] = "Falha ao copiar arquivo para o Servidor 2"
                self.excluir_arquivos(destino, titulo)
                self.situacao_copia_servidor2 = self.FALHA_AO_COPIAR_ARQUIVO

    def copiar_servidor_1(self, destino, titulo, arquivo, server, codigo_material):
        print("Copia servidor 1")
        try:
            self.copiar_arquivo_e_gerar_xml(destino, titulo, arquivo, server, codigo_material)
            self.situacao_copia_servidor1 = self.TRANSFERIDO_COM_SUCESSO
        except CopiaCanceladaError as ex:
            self.progressbar.pack_forget()
            self.label_porcent["text"] = "Cancelando copia para Servidor 1"
            self.excluir_arquivos(destino, titulo)
            self.situacao_copia_servidor1 = self.COPIA_CANCELADA
        except TimeoutCopyError as ex:
            self.excluir_arquivos(destino, titulo)
            self.situacao_copia_servidor1 = self.TIMEOUT_COPY_ERROR
        except CreateXMLError as ex:
            self.progressbar.pack_forget()
            self.label_porcent["text"] = "Falha ao gerar arquivo XML para o Servidor 1"
            self.excluir_arquivos(destino, titulo)
            self.situacao_copia_servidor1 = self.FALHA_AO_GERAR_XML
        except (Exception, FileNotFoundError, SpecialFileError, ValueError) as ex:
            self.progressbar.pack_forget()
            self.label_porcent["text"] = "Falha ao copiar arquivo para o Servidor 1"
            self.excluir_arquivos(destino, titulo)
            self.situacao_copia_servidor1 = self.FALHA_AO_COPIAR_ARQUIVO

    def copiar_arquivo_e_gerar_xml(self, destino, titulo, arquivo, server_name, codigo_material, server=1):
        self.update_label_progressbar(True, "0%", server)
        self.copy_with_callback(arquivo,
                                f'{destino}\\{titulo}.mxf',
                                server_name,
                                None,
                                False,
                                server
                                )

        self.update_label_progressbar(False, f"Gerando arquivo xml {server_name}", server)
        print("Gerar xml " + str(server))
        self.gerar_xml(destino, titulo, arquivo, codigo_material)

    def copy_with_callback(self, src, dest, server_name, callback=None, follow_symlinks=True, server=1):
        buffer_size = 4096 * 1024
        srcfile = pathlib.Path(src)
        destpath = pathlib.Path(dest)

        if not srcfile.is_file():
            raise FileNotFoundError(f"Arquivo de origem `{src}` não existe")

        destfile = destpath / srcfile.name if destpath.is_dir() else destpath

        if destfile.exists() and srcfile.samefile(destfile):
            raise SameFileError(f"Arquivo de origem `{src}` e arquivo de destino `{dest}` são iguais.")

        # check for special files, lifted from shutil.copy source
        for fname in [srcfile, destfile]:
            try:
                st = os.stat(str(fname))
            except OSError:
                # File most likely does not exist
                pass
            else:
                if shutil.stat.S_ISFIFO(st.st_mode):
                    raise SpecialFileError(f"`{fname}` is a named pipe")

        if callback is not None and not callable(callback):
            raise ValueError("callback is not callable")

        if not follow_symlinks and srcfile.is_symlink():
            if destfile.exists():
                os.unlink(destfile)
            os.symlink(os.readlink(str(srcfile)), str(destfile))
        else:
            size = os.stat(src).st_size
            with open(srcfile, "rb") as fsrc:
                with open(destfile, "wb") as fdest:
                    self.copy_file(fsrc, fdest, server_name, callback, size, buffer_size, server)
        shutil.copymode(str(srcfile), str(destfile))
        return str(destfile)

    def copy_file(self, fsrc, fdest, server_name, callback, total, length, server=1):
        copied = 0
        while True:
            if not self.enviar:
                raise CopiaCanceladaError(f"Cópia cancelada")

            if not self.stop_watch.check(self.configuration["timeout_ack"]):
                raise TimeoutCopyError(f"Tempo de espera excedido para realizar a copia do arquivo.")

            buf = fsrc.read(length)
            if not buf:
                break

            fdest.write(buf)
            copied += len(buf)

            if server == 1:
                self.update_progress(copied, total, server_name)
            else:
                self.update_progress(copied, total, server_name, 2)

            if callback is not None:
                callback(len(buf), copied, total)

    def gerar_xml(self, servidor, titulo, arquivo, codigo):
        try:
            dto = {
                'codigo': codigo,
                'arquivo': f"{titulo}.mxf",
                'titulo': titulo,
                'grupo': self.grupo.get(),
                'operador': self.configuration["usuario"],
                'markIn': '000',
                'markOut': ConvertVideo.get_duration(arquivo),
                'remover': str(self.configuration["remover"])
            }
            VideoXML.create(caminho=servidor, arquivo=f'{titulo}.xml', dto=dto)
        except Exception as ex:
            raise CreateXMLError(f"Falha ao gerar arquivo xml. {ex}")

    def checar_ack(self, caminho, nome_arquivo, server=1) -> int:
        print("checar_ack " + str(server))

        arquivo = os.path.join(caminho, f"{nome_arquivo}.ack")

        while True:
            if not self.enviar:
                raise ArquivoAckCanceladoError(f"Recepção do arquivo ACK cancelado")

            if not self.stop_watch.check(self.configuration["timeout_ack"]):
                raise TimeoutAckError(f"Tempo de espera excedido para receber o arquivo ACK do servidor")

            if os.path.exists(arquivo):
                while True:
                    if not self.enviar:
                        raise ArquivoAckCanceladoError(f"Recepção do arquivo ACK cancelado")

                    try:
                        result = AckXML.read(caminho=caminho, arquivo=f"{nome_arquivo}.ack")
                        break
                    except Exception:
                        if self.stop_watch.check(self.configuration["timeout_ack"]):
                            continue
                        else:
                            raise ArquivoAckFalhaError(f"Falha ao receber arquivo ACK do servidor")

                if int(result[0]) == self.ACK_RECEBIDO:
                    return self.TRANSFERIDO_COM_SUCESSO
                elif int(result[0]) == self.MATERIAL_JA_EXISTENTE:
                    raise CodigoMaterialError(f"O código do material já existe")
                elif int(result[0]) == self.ARQUIVO_VIDEO_NAO_ENCONTRADO:
                    raise ArquivoVideoNotFoundError(f"Arquivo de vídeo não encontrado")
                elif int(result[0]) == self.ARQUIVO_VIDEO_INVALIDO:
                    raise ArquivoVideoInvalidoError(f"Arquivo de vídeo não encontrado")
                elif int(result[0]) == self.FALHA_TRANSFERIR_ARQUIVO:
                    raise TransferirArquivoFalhaError(f"Falha ao copiar arquivo")
                else:
                    return self.ACK_FALHA

    def exibir_messagebox_e_log_concluido(self, result_destino1, result_destino2) -> None:
        message_messagebox, message_log, type_message = self.montar_mensagens_conclusao(result_destino1,
                                                                                        result_destino2)

        if type_message == "info":
            messagebox.showinfo(title="Atenção", message=message_messagebox)
            LogService.save_info(message_log)
        elif type_message == "warning":
            messagebox.showwarning(title="Atenção", message=message_messagebox)
            LogService.save_warning(message_log)
        elif type_message == "error":
            messagebox.showerror(title="Atenção", message=message_messagebox)
            LogService.save_error(message_log)

    def montar_mensagens_conclusao(self, result_destino1: int, result_destino2) -> tuple:
        message_messagebox = ""
        message_log = ""
        type_message = "info"

        if self.configuration["habilitar_servidor2"] == 1:
            if result_destino1 == self.TRANSFERIDO_COM_SUCESSO and result_destino2 == self.TRANSFERIDO_COM_SUCESSO:
                message_messagebox = f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para ambos os " \
                                     f"servidores. "
                message_log = f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}."
                type_message = "info"
            elif result_destino1 == self.MATERIAL_JA_EXISTENTE and result_destino2 == self.MATERIAL_JA_EXISTENTE:
                message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para ambos os servidores. " \
                                     f"Código do material já existente."
                message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}. " \
                              f"Código do material já existente. (Error Code: {self.MATERIAL_JA_EXISTENTE})"
                type_message = "error"
            elif result_destino1 == self.ARQUIVO_VIDEO_NAO_ENCONTRADO \
                    and result_destino2 == self.ARQUIVO_VIDEO_NAO_ENCONTRADO:
                message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para ambos os servidores. " \
                                     f"Arquivo de vídeo não encontrado."
                message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}. " \
                              f"Arquivo de vídeo não encontrado. (Error Code: {self.ARQUIVO_VIDEO_NAO_ENCONTRADO})"
                type_message = "error"
            elif result_destino1 == self.ARQUIVO_VIDEO_INVALIDO \
                    and result_destino2 == self.ARQUIVO_VIDEO_INVALIDO:
                message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para ambos os servidores. " \
                                     f"Arquivo de vídeo inválido."
                message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}. " \
                              f"Arquivo de vídeo inválido. (Error Code: {self.ARQUIVO_VIDEO_INVALIDO})"
                type_message = "error"
            elif result_destino1 == self.FALHA_TRANSFERIR_ARQUIVO \
                    and result_destino2 == self.FALHA_TRANSFERIR_ARQUIVO:
                message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para ambos os servidores. "
                message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}. " \
                              f"(Error Code: {self.FALHA_TRANSFERIR_ARQUIVO})"
                type_message = "error"
            elif result_destino1 == self.FALHA_AO_COPIAR_ARQUIVO \
                    and result_destino2 == self.FALHA_AO_COPIAR_ARQUIVO:
                message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para ambos os servidores. " \
                                     f"Falha no processo de cópia."
                message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}. " \
                              f"Falha no processo de cópia."
                type_message = "error"
            elif result_destino1 == self.COPIA_CANCELADA \
                    and result_destino2 == self.COPIA_CANCELADA:
                message_messagebox = f"Cópia do arquivo {self.titulo.get()}.mxf cancelada para ambos os servidores."
                message_log = f"Cópia do arquivo {self.titulo.get()}.mxf cancelada para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}."
                type_message = "warning"
            elif result_destino1 == self.FALHA_AO_GERAR_XML \
                    and result_destino2 == self.FALHA_AO_GERAR_XML:
                message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para ambos os servidores. " \
                                     f"Falha ao gerar arquivo xml."
                message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}. " \
                              f"Falha ao gerar arquivo xml."
                type_message = "error"
            elif result_destino1 == self.TIMEOUT_COPY_ERROR \
                    and result_destino2 == self.TIMEOUT_COPY_ERROR:
                message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para ambos os servidores. " \
                                     f"Timeout error na copia do arquivo."
                message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}. " \
                              f"Timeout error na copia do arquivo."
                type_message = "error"
            elif result_destino1 == self.RECEPCAO_ACK_CANCELADO \
                    and result_destino2 == self.RECEPCAO_ACK_CANCELADO:
                message_messagebox = f"Recepção do arquivo de confirmação cancelada para captura do " \
                                     f"arquivo {self.titulo.get()}.mxf em " \
                                     f"ambos os servidores. Verifique manualmente nos servidores."
                message_log = f"Recepção do arquivo de confirmação cancelada para captura do " \
                              f"arquivo {self.titulo.get()}.mxf em " \
                              f"{self.configuration['servidor']} e {self.configuration['servidor2']}. " \
                              f"Verifique manualmente nos servidores."
                type_message = "warning"
            elif result_destino1 == self.ACK_FALHA \
                    and result_destino2 == self.ACK_FALHA:
                message_messagebox = f"Arquivo de confirmação corrompido para a captura do " \
                                     f"arquivo {self.titulo.get()}.mxf em ambos os servidores. " \
                                     f"Verifique manualmente nos servidores."
                message_log = f"Arquivo de confirmação corrompido para a captura do " \
                              f"arquivo {self.titulo.get()}.mxf em " \
                              f"{self.configuration['servidor']} e {self.configuration['servidor2']}."
                type_message = "error"
            elif result_destino1 == self.TIMEOUT_ACK_ERROR \
                    and result_destino2 == self.TIMEOUT_ACK_ERROR:
                message_messagebox = f"Falha ao receber arquivo de confirmação para a captura do arquivo " \
                                     f"{self.titulo.get()}.mxf em ambos os servidores. " \
                                     f"Timeout error na recepção do arquivo de confirmação."
                message_log = f"Falha ao receber arquivo de confirmação para a captura do arquivo " \
                              f"{self.titulo.get()}.mxf para " \
                              f"{self.configuration['servidor']} e para {self.configuration['servidor2']}. " \
                              f"Timeout error na recepção do arquivo de confirmação."
                type_message = "error"
            elif result_destino1 == self.ERRO_DESCONHECIDO \
                    and result_destino2 == self.ERRO_DESCONHECIDO:
                message_messagebox = f"Erro desconhecido ao transferir arquivo {self.titulo.get()}.mxf ou na " \
                                     f"recepção do arquivo de confirmação."
                message_log = f"Erro desconhecido ao transferir arquivo {self.titulo.get()}.mxf ou na recepção do " \
                              f"arquivo de confirmação."
                type_message = "error"
            else:
                message_messagebox_aux, message_log_aux, type_message_aux = self.exibir_mensagens_conclusao(
                    result_destino1,
                    1)
                message_messagebox, message_log, type_message = self.exibir_mensagens_conclusao(result_destino2, 2)

                return message_messagebox_aux + message_messagebox, message_log_aux + message_log, 'warning'
        else:
            message_messagebox, message_log, type_message = self.exibir_mensagens_conclusao(result_destino1, 1)

        return message_messagebox, message_log, type_message

    def exibir_mensagens_conclusao(self, result_destino, server=1):
        message_messagebox = ""
        message_log = ""
        type_message = "info"

        path_servidor = self.configuration['servidor2']
        if server == 1:
            path_servidor = self.configuration['servidor']

        if result_destino == self.TRANSFERIDO_COM_SUCESSO:
            message_messagebox = f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para o Servidor {server}. "
            message_log = f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para {path_servidor}. "
            type_message = "info"
        elif result_destino == self.MATERIAL_JA_EXISTENTE:
            message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para o Servidor {server}. " \
                                 f"Código do material já existente. "
            message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para {path_servidor}. " \
                          f"Código do material já existente. (Error Code: {self.MATERIAL_JA_EXISTENTE}) "
            type_message = "error"
        elif result_destino == self.ARQUIVO_VIDEO_NAO_ENCONTRADO:
            message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para o Servidor {server}. " \
                                 f"Arquivo de vídeo não encontrado. "
            message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para {path_servidor}. " \
                          f"Arquivo de vídeo não encontrado. (Error Code: {self.ARQUIVO_VIDEO_NAO_ENCONTRADO}) "
            type_message = "error"
        elif result_destino == self.ARQUIVO_VIDEO_INVALIDO:
            message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para o Servidor {server}. " \
                                 f"Arquivo de vídeo inválido. "
            message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para " \
                          f"{path_servidor}. " \
                          f"Arquivo de vídeo inválido. (Error Code: {self.ARQUIVO_VIDEO_INVALIDO}) "
            type_message = "error"
        elif result_destino == self.FALHA_TRANSFERIR_ARQUIVO:
            message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para o Servidor {server}. "
            message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para " \
                          f"{path_servidor}. (Error Code: {self.FALHA_TRANSFERIR_ARQUIVO}) "
            type_message = "error"
        elif result_destino == self.FALHA_AO_COPIAR_ARQUIVO:
            message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para o Servidor {server}. " \
                                 f"Falha no processo de cópia. "
            message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para {path_servidor}. " \
                          f"Falha no processo de cópia. "
            type_message = "error"
        elif result_destino == self.COPIA_CANCELADA:
            message_messagebox = f"Cópia do arquivo {self.titulo.get()}.mxf cancelada para o Servidor {server}. "
            message_log = f"Cópia do arquivo {self.titulo.get()}.mxf cancelada para {path_servidor}. "
            type_message = "warning"
        elif result_destino == self.FALHA_AO_GERAR_XML:
            message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para o Servidor {server}. " \
                                 f"Falha ao gerar arquivo xml. "
            message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para {path_servidor}. " \
                          f"Falha ao gerar arquivo xml. "
            type_message = "error"
        elif result_destino == self.TIMEOUT_COPY_ERROR:
            message_messagebox = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para o Servidor {server}. " \
                                 f"Timeout error na copia do arquivo. "
            message_log = f"Falha ao transferir arquivo {self.titulo.get()}.mxf para {path_servidor}. " \
                          f"Timeout error na copia do arquivo. "
            type_message = "error"
        elif result_destino == self.RECEPCAO_ACK_CANCELADO:
            message_messagebox = f"Recepção do arquivo de confirmação cancelada para captura do " \
                                 f"arquivo {self.titulo.get()}.mxf no Servidor {server}. " \
                                 f"Verifique manualmente no servidor."
            message_log = f"Recepção do arquivo de confirmação cancelada para captura do " \
                          f"arquivo {self.titulo.get()}.mxf em {path_servidor}. " \
                          f"Verifique manualmente no servidor."
            type_message = "warning"
        elif result_destino == self.ACK_FALHA:
            message_messagebox = f"Arquivo de confirmação corrompido para a captura do " \
                                 f"arquivo {self.titulo.get()}.mxf no Servidor {server}. " \
                                 f"Verifique manualmente no servidor. "
            message_log = f"Arquivo de confirmação corrompido para a captura do " \
                          f"arquivo {self.titulo.get()}.mxf em {path_servidor}. "
            type_message = "error"
        elif result_destino == self.TIMEOUT_ACK_ERROR:
            message_messagebox = f"Falha ao receber arquivo de confirmação para a captura do arquivo " \
                                 f"{self.titulo.get()}.mxf no servidor {server}. " \
                                 f"Timeout error na recepção do arquivo de confirmação. "
            message_log = f"Falha ao receber arquivo de confirmação para a captura do arquivo " \
                          f"{self.titulo.get()}.mxf para {path_servidor}. " \
                          f"Timeout error na recepção do arquivo de confirmação. "
            type_message = "error"
        else:
            message_messagebox = f"Erro desconhecido ao transferir arquivo {self.titulo.get()}.mxf ou na recepção do " \
                                 f"arquivo de confirmação para o Servidor {server}. "
            message_log = f"Erro desconhecido ao transferir arquivo {self.titulo.get()}.mxf ou na recepção do " \
                          f"arquivo de confirmação para {path_servidor}. "
            type_message = "error"

        return message_messagebox, message_log, type_message

    def excluir_arquivos_servidores(self) -> None:
        self.excluir_arquivos(self.configuration["servidor"], self.titulo.get())

        if self.configuration["habilitar_servidor2"] == 1:
            self.excluir_arquivos(self.configuration["servidor2"], self.titulo.get())

    @staticmethod
    def excluir_arquivos(caminho, nome_arquivo) -> None:
        MyFile.excluir_arquivo_mxf(caminho, nome_arquivo)
        MyFile.excluir_arquivo_xml(caminho, nome_arquivo)
        MyFile.excluir_arquivo_ack(caminho, nome_arquivo)

    def update_progress(self, copied: float, total: float, server_name: str, server=1) -> None:
        porcent = int((copied * 100) / total)

        if server == 1:
            if self.progressbar['value'] < 100:
                self.progressbar['value'] = porcent
                self.label_porcent["text"] = f"{porcent}% - Transferindo para {server_name}"
        else:
            if self.progressbar2['value'] < 100:
                self.progressbar2['value'] = porcent
                self.label_porcent2["text"] = f"{porcent}% - Transferindo para {server_name}"

    def show_progressbar(self, value: bool, server=1) -> None:
        if server == 1:
            if value:
                self.progressbar.pack(side=LEFT, padx=1, expand=YES)
                self.label_porcent.pack(side=LEFT, padx=1, expand=YES)
            else:
                self.progressbar.pack_forget()
                self.label_porcent.pack_forget()
        else:
            if value:
                self.progressbar2.pack(side=LEFT, padx=1, expand=YES)
                self.label_porcent2.pack(side=LEFT, padx=1, expand=YES)
            else:
                self.progressbar2.pack_forget()
                self.label_porcent2.pack_forget()

    def set_progressbar_determinate(self, value: bool, server=1) -> None:
        if server == 1:
            if value:
                self.progressbar.stop()
                self.progressbar["mode"] = "determinate"
            else:
                self.progressbar["mode"] = "indeterminate"
                self.progressbar.start()
        else:
            if value:
                self.progressbar2.stop()
                self.progressbar2["mode"] = "determinate"
            else:
                self.progressbar2["mode"] = "indeterminate"
                self.progressbar2.start()

    def update_label_progressbar(self, determinate: bool, text: str, server=1) -> None:
        if server == 1:
            self.set_progressbar_determinate(determinate)
            self.label_porcent["text"] = text
        else:
            self.set_progressbar_determinate(determinate, 2)
            self.label_porcent2["text"] = text

    def change_button_action_state(self, value: bool) -> None:
        if value:
            self.button_action['text'] = 'Enviar ao servidor'
            self.button_action.configure(bootstyle="primary", style="primary.TButton")
        else:
            self.button_action['text'] = 'Cancelar transferência'
            self.button_action.configure(bootstyle="danger", style="danger.TButton")

    def change_form_action_state(self, value: bool) -> None:
        if value:
            self.entry_titulo['state'] = 'enabled'
            self.combobox_grupo['state'] = 'enabled'
            self.button_browse["state"] = "enabled"
        else:
            self.entry_titulo['state'] = 'disabled'
            self.combobox_grupo['state'] = 'disabled'
            self.button_browse["state"] = "disabled"

    def clean_fields(self) -> None:
        self.arquivo.set("")

        self.entry_arquivo.config(state=NORMAL)
        self.entry_arquivo.delete("1.0", END)
        self.entry_arquivo.config(state=DISABLED)

        self.titulo.set("")
        self.grupo.set("")

    def validate(self) -> bool:
        if self.configuration["servidor"] is None or self.configuration["servidor"] == "":
            messagebox.showwarning(title="Atenção", message="Em configurações o campo Caminho Servidor 1 devem ser "
                                                            "preenchido.")
            return False
        if self.configuration["usuario"] is None or self.configuration["usuario"] == "":
            messagebox.showwarning(title="Atenção", message="Em configurações o campo Usuário devem ser preenchido.")
            return False
        if self.arquivo.get() is None or self.arquivo.get() == "":
            messagebox.showwarning(title="Atenção", message="O campo Arquivo deve ser selecionado.")
            return False
        if MyFile.extensao_arquivo(self.arquivo.get()) != ".MXF" \
                and MyFile.extensao_arquivo(self.arquivo.get()) != ".mxf":
            messagebox.showwarning(title="Atenção", message="O arquivo selecionado deve ser um arquivo com extensão "
                                                            ".mxf.")
            return False
        if self.titulo.get() is None or self.titulo.get() == "":
            self.entry_titulo.configure(bootstyle="danger")
            self.entry_titulo.focus()
            messagebox.showwarning(title="Atenção", message="O campo Retranca/Título deve ser preenchido.")
            return False
        if Helper.possui_caractere_especial(self.titulo.get()):
            self.entry_titulo.configure(bootstyle="danger")
            self.entry_titulo.focus()
            messagebox.showwarning(title="Atenção", message="Não são permitidos acentos e caracteres especiais no "
                                                            "campo Retranca/Título. Só são permitidos letras, números, "
                                                            "underline e hífen.")
            return False
        if self.grupo.get() is None or self.grupo.get() == "":
            self.combobox_grupo.configure(bootstyle="danger")
            self.combobox_grupo.focus()
            messagebox.showwarning(title="Atenção", message="O campo Grupo dever ser selecionado.")
            return False
        if self.grupo.get() not in self.configuration["grupos"]:
            self.combobox_grupo.configure(bootstyle="danger")
            self.combobox_grupo.focus()
            messagebox.showwarning(title="Atenção", message="O valor selecionado é inválido para o campo Grupo.")
            return False
        if not os.path.exists('ffmpeg.exe'):
            messagebox.showwarning(title="Atenção", message="Arquivo ffmpeg.exe não encontrado.")
            return False
        return True

