import pathlib
import shutil
from tkinter import filedialog
from tkinter import messagebox
import tkinter as ttk1
import ttkbootstrap as ttk
import tkVideoPlayer
from ttkbootstrap.constants import *
from pathlib import Path
import threading
import os
import cv2
from PIL import Image, ImageTk

from src.app.forms.LogForm import LogsForm
from src.app.forms.SettingsForm import SettingsForm
from src.business.adapters.MyJSON import MyJSON
from src.business.adapters.VideoXML import VideoXML
from src.business.adapters.MyRandom import MyRandom
from src.business.adapters.AckXML import AckXML
from src.business.utils.ConvertVideo import ConvertVideo
from src.business.utils.StopWatch import StopWatch
from src.business.adapters.MyFile import MyFile
from src.business.services.LogService import LogService
from src.data.repository.LogRepository import LogRepository
from src.business.exceptions.SameFileError import SameFileError
from src.business.exceptions.SpecialFileError import SpecialFileError


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
            'grupos': []
        }
        self.photo_images = []
        self.enviar = False
        self.situacao_copia_servidor1 = False
        self.situacao_copia_servidor2 = False

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
        self.label_porcent = None
        self.progressbar2 = None
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
        # self.create_enviar_frame()
        # self.create_preview_frame()
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
        label.grid(row=0, column=0, padx=1, sticky=ttk.E)
        self.entry_arquivo = ttk.Entry(frame, width=70, textvariable=self.arquivo, state="disabled",
                                       font=("Helvetica", 10))
        self.entry_arquivo.grid(row=0, column=1, padx=2, sticky=ttk.W)
        self.button_browse = ttk.Button(frame, text="Selecionar Arquivo", bootstyle=(INFO, OUTLINE),
                                        command=self.on_browse, style='primary.Outline.TButton')
        self.button_browse.grid(row=0, column=2, padx=2)

        label = ttk.Label(frame, text="Retranca / Título", font=("Helvetica", 10))
        label.grid(row=1, column=0, padx=1, pady=(20, 0), sticky=ttk.E)
        self.entry_titulo = ttk.Entry(frame, width=50, textvariable=self.titulo, font=("Helvetica", 10))
        self.entry_titulo.grid(row=1, column=1, padx=2, pady=(20, 0), sticky=ttk.W)
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
        label_frame = ttk.Labelframe(parent, text='Preview')
        label_frame.pack(side=RIGHT, padx=20, pady=(5, 15), anchor=ttk.N)

        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=15)

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
        # self.label_thumbnail.place(x=0, y=0)

    def create_progressbar_frame(self):
        frame = ttk.Frame(self, height=20)
        frame.pack(side=LEFT, padx=20, pady=(5, 15))

        self.progressbar = ttk.Progressbar(
            master=frame,
            length=300,
            # mode='indeterminate',
            bootstyle="success"
        )
        self.progressbar.pack_forget()
        # self.progressbar.pack(side=LEFT)

        self.label_porcent = ttk.Label(frame, text="0%")
        self.label_porcent.pack_forget()
        # self.label_porcent.pack(side=LEFT)

        frame2 = ttk.Frame(self, height=20)
        frame2.pack(side=LEFT, padx=20, pady=(5, 15))

        self.progressbar2 = ttk.Progressbar(
            master=frame2,
            length=300,
            # mode='indeterminate',
            bootstyle="success"
        )
        self.progressbar2.pack_forget()
        # self.progressbar2.pack(side=LEFT)

        self.label_porcent2 = ttk.Label(frame2, text="0%")
        self.label_porcent2.pack_forget()
        # self.label_porcent2.pack(side=LEFT)

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
            self.entry_arquivo.configure(bootstyle="default")
            self.load_video(filename)

    def on_action(self) -> None:
        if not self.enviar:
            if self.validate():
                self.enviar = True
                self.change_button_action_state(False)
                self.show_progressbar(True)

                t = threading.Thread(daemon=True, target=self.background_worker)
                t.start()
        else:
            self.enviar = False
            self.change_button_action_state(True)

    def background_worker(self):
        self.situacao_copia_servidor1 = False
        self.situacao_copia_servidor2 = False

        self.change_form_action_state(False)

        try:
            self.video.stop()

            codigo_material = MyRandom.gerar_codigo()

            thread1 = threading.Thread(daemon=True,
                                       target=self.copiar_servidor_2,
                                       args=(self.configuration["servidor2"], self.titulo.get(), self.arquivo.get(),
                                             "Servidor 2", codigo_material))

            thread2 = threading.Thread(daemon=True,
                                       target=self.copiar_servidor_1,
                                       args=(self.configuration["servidor"], self.titulo.get(), self.arquivo.get(),
                                             "Servidor 1", codigo_material))

            # Inicia as threads
            thread1.start()
            thread2.start()

            # Aguarda o término das threads
            thread1.join()
            thread2.join()

            if self.configuration["habilitar_servidor2"] == 1 and self.situacao_copia_servidor2:
                result_destino2 = self.checar_ack(self.configuration["servidor2"], self.titulo.get())
            else:
                result_destino2 = False

            if self.situacao_copia_servidor1:
                result_destino1 = self.checar_ack(self.configuration["servidor"], self.titulo.get())
            else:
                result_destino1 = False

            self.show_progressbar(False)
            self.update_label_progressbar(True, "100%")
            self.change_button_action_state(True)

            if self.enviar:
                self.exibir_messagebox_concluido(result_destino1, result_destino2)
                self.clean_fields()
            else:
                self.excluir_arquivos_servidores()
                LogService.save_warning(f"Transferência cancelada pelo usuário.")
                messagebox.showwarning(title="Atenção", message="Transferência cancelada pelo usuário.")
        except Exception as ex:
            self.excluir_arquivos_servidores()
            self.show_progressbar(False)
            self.set_progressbar_determinate(True)
            self.label_porcent["text"] = "0%"
            self.change_button_action_state(True)
            LogService.save_error(f"{ex}")
            messagebox.showerror(title="Erro", message=ex)
        finally:
            self.enviar = False
            self.change_form_action_state(True)
            self.label_thumbnail.place_forget()
            self.video.place_forget()

    def copiar_servidor_2(self, destino, titulo, arquivo, server, codigo_material):
        if self.configuration["habilitar_servidor2"] == 1:
            try:
                self.copiar_arquivo_e_gerar_xml(destino, titulo, arquivo, server, codigo_material)
                self.situacao_copia_servidor2 = True
            except:
                self.situacao_copia_servidor2 = False

    def copiar_servidor_1(self, destino, titulo, arquivo, server, codigo_material):
        try:
            self.copiar_arquivo_e_gerar_xml(destino, titulo, arquivo, server, codigo_material)
            self.situacao_copia_servidor1 = True
        except:
            self.situacao_copia_servidor1 = False

    def copiar_arquivo_e_gerar_xml(self, destino, titulo, arquivo, server, codigo_material):
        self.update_label_progressbar(True, "0%")
        self.copy_with_callback(arquivo,
                                f'{destino}\\{titulo}.mxf',
                                server,
                                follow_symlinks=False,
                                callback=None
                                )
        self.update_label_progressbar(False, f"Gerando arquivo xml {server}")
        self.gerar_xml(destino, titulo, arquivo, codigo_material)

    def copy_with_callback(self, src, dest, server, callback=None, follow_symlinks=True):
        try:
            buffer_size = 4096 * 1024
            srcfile = pathlib.Path(src)
            destpath = pathlib.Path(dest)

            if not srcfile.is_file():
                raise FileNotFoundError(f"Arquivo de origem `{src}` não existe")

            destfile = destpath / srcfile.name if destpath.is_dir() else destpath

            if destfile.exists() and srcfile.samefile(destfile):
                raise SameFileError(
                    f"Arquivo de origem `{src}` e arquivo de destino `{dest}` são iguais."
                )

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
                        self.copy_file(
                            fsrc, fdest, server, callback=callback, total=size, length=buffer_size
                        )
            shutil.copymode(str(srcfile), str(destfile))
            return str(destfile)
        except Exception as ex:
            raise Exception(f"Falha ao copiar arquivo. {ex}")

    def copy_file(self, fsrc, fdest, server, callback, total, length):
        copied = 0
        while True:
            if not self.enviar:
                self.set_progressbar_determinate(False)
                self.label_porcent["text"] = "Cancelando..."
                break

            buf = fsrc.read(length)
            if not buf:
                break

            fdest.write(buf)
            copied += len(buf)

            self.update_progress(copied, total, server)

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
                'remover': '0'
            }
            VideoXML.create(caminho=servidor, arquivo=f'{titulo}.xml', dto=dto)
        except Exception as ex:
            raise Exception(f"Falha ao gerar arquivo xml. {ex}")

    def checar_ack(self, caminho, nome_arquivo) -> bool:
        try:
            self.label_porcent["text"] = "Aguardando arquivo de confirmação..."
            arquivo = os.path.join(caminho, f"{nome_arquivo}.ack")
            stop_watch = StopWatch()

            while True:
                if not self.enviar:
                    self.set_progressbar_determinate(False)
                    self.label_porcent["text"] = "Cancelando..."
                    return False

                if not stop_watch.check(self.configuration["timeout_ack"]):
                    raise Exception(f"Tempo de espera excedido para receber o arquivo de checagem.")

                if os.path.exists(arquivo):
                    while True:
                        if not self.enviar:
                            self.set_progressbar_determinate(False)
                            self.label_porcent["text"] = "Cancelando..."
                            return False

                        try:
                            result = AckXML.read(caminho=caminho, arquivo=f"{nome_arquivo}.ack")
                            os.remove(arquivo)
                            break
                        except Exception:
                            if stop_watch.check(self.configuration["timeout_ack"]):
                                continue
                            else:
                                raise Exception(f"Falha ao receber excluir arquivo {nome_arquivo}.ack")

                    if result[0] == "0":
                        return True
                    elif result[0] == "4" \
                            or result[0] == "8" \
                            or result[0] == "9" \
                            or result[0] == "10":
                        raise Exception(f"Falha ao receber arquivo de confirmação. {result[1]}")
                    else:
                        raise Exception("Erro desconhecido ao receber arquivo de confirmação.")
        except Exception as ex:
            raise Exception(ex)

    def exibir_messagebox_concluido(self, result_destino1, result_destino2) -> None:
        if self.configuration["habilitar_servidor2"] == 0 and result_destino1:
            LogService.save_info(f"Arquivo {self.titulo.get()}.mxf transferido com sucesso "
                                 f"para {self.configuration['servidor']}")
            messagebox.showinfo(title="Atenção", message=f"Arquivo {self.titulo.get()}.mxf "
                                                         f"transferido com sucesso para o Servidor 1!")
        elif self.configuration["habilitar_servidor2"] == 0 and not result_destino1:
            LogService.save_info("Falha ao transferir arquivo.")
            messagebox.showinfo(title="Atenção", message="Falha ao transferir arquivo.")
        elif result_destino1 and result_destino2:
            LogService.save_info(f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para "
                                 f"{self.configuration['servidor']} e para {self.configuration['servidor2']}")
            messagebox.showinfo(title="Atenção", message=f"Arquivo {self.titulo.get()}.mxf "
                                                         f"transferido com sucesso para os dois Servidores.")
        elif result_destino1:
            LogService.save_info(f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para "
                                 f"{self.configuration['servidor']} mas apresentou falha o ser transferido para "
                                 f"{self.configuration['servidor2']}")
            messagebox.showwarning(title="Atenção",
                                   message=f"Arquivo {self.titulo.get()}.mxf "
                                           f"transferido com sucesso para o Servidor 1 mas "
                                           f"apresentou falha ao ser transferido ao Servidor 2.")
        elif result_destino2:
            LogService.save_info(f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para "
                                 f"{self.configuration['servidor2']} mas apresentou falha o ser transferido para "
                                 f"{self.configuration['servidor']}")
            messagebox.showwarning(title="Atenção",
                                   message=f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para o "
                                           f"Servidor 2 mas apresentou falha ao ser transferido ao Servidor 1.")
        else:
            LogService.save_info(f"Falha ao transferir arquivo {self.titulo.get()}.mxf para "
                                 f"{self.configuration['servidor']} e para {self.configuration['servidor2']}.")
            messagebox.showwarning(title="Atenção",
                                   message=f"Falha ao transferir arquivo para os dois Servidores selecionados.")

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
            self.button_action['text'] = 'Parar transferência'
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
            self.entry_arquivo.configure(bootstyle="danger")
            messagebox.showwarning(title="Atenção", message="O campo arquivo deve ser selecionado.")
            return False
        if MyFile.extensao_arquivo(self.arquivo.get()) != ".MXF" \
                and MyFile.extensao_arquivo(self.arquivo.get()) != ".mxf":
            messagebox.showwarning(title="Atenção", message="O arquivo selecionado deve ser um arquivo com extensão "
                                                            ".mxf.")
            return False
        if self.titulo.get() is None or self.titulo.get() == "":
            self.entry_titulo.configure(bootstyle="danger")
            self.entry_titulo.focus()
            messagebox.showwarning(title="Atenção", message="O campo título deve ser preenchido.")
            return False
        if self.grupo.get() is None or self.grupo.get() == "":
            self.combobox_grupo.configure(bootstyle="danger")
            self.combobox_grupo.focus()
            messagebox.showwarning(title="Atenção", message="O campo Grupo dever ser selecionado.")
            return False
        return True

