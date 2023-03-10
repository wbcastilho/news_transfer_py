import pathlib
import shutil
from tkinter import filedialog
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pathlib import Path
import threading
import os

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

        self.arquivo = ttk.StringVar()
        self.titulo = ttk.StringVar()
        self.grupo = ttk.StringVar()

        self.grupo_values = []
        self.button_action = None
        self.button_browse = None
        self.entry_arquivo = None
        self.entry_titulo = None
        self.combobox_grupo = None
        self.progressbar = None
        self.label_porcent = None

        self.init_database()
        self.read_config()
        self.init_combobox()
        self.associate_icons()
        self.create_buttonbar()
        self.create_enviar_frame()
        self.create_progressbar_frame()

    @staticmethod
    def init_database():
        try:
            LogRepository.create_table()
        except Exception as err:
            messagebox.showwarning(title="Aten????o", message=f"Falha ao se conectar com o banco de dados. {err}")

    def associate_icons(self) -> None:
        image_files = {
            'play-icon': 'icons8-reproduzir-24.png',
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
            text='Configura????es',
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

    def create_enviar_frame(self) -> None:
        label_frame = ttk.Labelframe(self, text='Enviar')
        label_frame.pack(fill="x", padx=10, pady=(5, 15))
        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=15)

        label = ttk.Label(frame, text="Arquivo", font=("Helvetica", 10))
        label.grid(row=0, column=0, padx=1, sticky=ttk.E)
        self.entry_arquivo = ttk.Entry(frame, width=100, textvariable=self.arquivo, state="disabled", font=("Helvetica", 10))
        self.entry_arquivo.grid(row=0, column=1, padx=2, sticky=ttk.W)
        self.button_browse = ttk.Button(frame, text="Selecionar Arquivo", bootstyle=(INFO, OUTLINE),
                                        command=self.on_browse, style='primary.Outline.TButton')
        self.button_browse.grid(row=0, column=2, padx=2)

        label = ttk.Label(frame, text="Retranca / T??tulo", font=("Helvetica", 10))
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

        self.button_action = ttk.Button(frame, width=120, text='Enviar ao servidor', command=lambda: self.on_action(),
                                        bootstyle='primary', style='primary.TButton')
        self.button_action.grid(row=3, column=0, columnspan=3, padx=0, pady=(20, 0))

    def create_progressbar_frame(self):
        frame = ttk.Frame(self)
        frame.pack(side=LEFT, padx=10, pady=(5, 15))

        self.progressbar = ttk.Progressbar(
            master=frame,
            length=300,
            bootstyle="success"
        )
        self.progressbar.pack_forget()

        self.label_porcent = ttk.Label(frame, text="0%")
        self.label_porcent.pack_forget()

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
            messagebox.showwarning(title="Aten????o", message=err)
        except FileNotFoundError as err:
            messagebox.showwarning(title="Aten????o", message=err)
        except Exception as err:
            messagebox.showwarning(title="Aten????o", message=err)

    def on_settings(self) -> None:
        if not self.enviar:
            setting_form = ttk.Toplevel()
            setting_form.title("Configura????es")
            setting_form.iconbitmap('src/app/assets/favicon.ico')
            setting_form.grab_set()
            setting_form.resizable(False, False)
            SettingsForm(setting_form, self)
        else:
            messagebox.showwarning(title="Aten????o", message="Para abrir a janela de configura????es ?? necess??rio antes "
                                                            "parar a monitora????o clicando no bot??o Parar.")

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
        result_destino2 = False
        self.change_form_action_state(False)

        try:
            self.copiar_arquivo_e_gerar_xml(self.configuration["servidor"], self.titulo.get(), self.arquivo.get(),
                                            "Servidor 1")

            if self.configuration["habilitar_servidor2"] == 1:
                self.copiar_arquivo_e_gerar_xml(self.configuration["servidor2"], self.titulo.get(), self.arquivo.get(),
                                                "Servidor 2")

            result_destino1 = self.checar_ack(self.configuration["servidor"], self.titulo.get())

            if self.configuration["habilitar_servidor2"] == 1:
                result_destino2 = self.checar_ack(self.configuration["servidor2"], self.titulo.get())

            self.show_progressbar(False)
            self.update_label_progressbar(True, "100%")
            self.change_button_action_state(True)

            if self.enviar:
                self.exibir_messagebox_concluido(result_destino1, result_destino2)
                self.clean_fields()
            else:
                self.excluir_arquivos_servidores()
                LogService.save_warning(f"Transfer??ncia cancelada pelo usu??rio.")
                messagebox.showwarning(title="Aten????o", message="Transfer??ncia cancelada pelo usu??rio.")
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

    def copiar_arquivo_e_gerar_xml(self, destino, titulo, arquivo, server):
        self.update_label_progressbar(True, "0%")
        self.copy_with_callback(arquivo,
                                f'{destino}\\{titulo}.mxf',
                                server,
                                follow_symlinks=False,
                                callback=None
                                )
        self.update_label_progressbar(False, f"Gerando arquivo xml {server}")
        self.gerar_xml(destino, titulo, arquivo)

    def copy_with_callback(self, src, dest, server, callback=None, follow_symlinks=True):
        try:
            buffer_size = 4096 * 1024
            srcfile = pathlib.Path(src)
            destpath = pathlib.Path(dest)

            if not srcfile.is_file():
                raise FileNotFoundError(f"Arquivo de origem `{src}` n??o existe")

            destfile = destpath / srcfile.name if destpath.is_dir() else destpath

            if destfile.exists() and srcfile.samefile(destfile):
                raise SameFileError(
                    f"Arquivo de origem `{src}` e arquivo de destino `{dest}` s??o iguais."
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

    def gerar_xml(self, servidor, titulo, arquivo):
        try:
            dto = {
                'codigo': MyRandom.gerar_codigo(),
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
            self.label_porcent["text"] = "Aguardando arquivo de confirma????o..."
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
                        raise Exception(f"Falha ao receber arquivo de confirma????o. {result[1]}")
                    else:
                        raise Exception("Erro desconhecido ao receber arquivo de confirma????o.")
        except Exception as ex:
            raise Exception(ex)

    def exibir_messagebox_concluido(self, result_destino1, result_destino2) -> None:
        if self.configuration["habilitar_servidor2"] == 0 and result_destino1:
            LogService.save_info(f"Arquivo {self.titulo.get()}.mxf transferido com sucesso "
                                 f"para {self.configuration['servidor']}")
            messagebox.showinfo(title="Aten????o", message=f"Arquivo {self.titulo.get()}.mxf "
                                                         f"transferido com sucesso para o Servidor 1!")
        elif self.configuration["habilitar_servidor2"] == 0 and not result_destino1:
            LogService.save_info("Falha ao transferir arquivo.")
            messagebox.showinfo(title="Aten????o", message="Falha ao transferir arquivo.")
        elif result_destino1 and result_destino2:
            LogService.save_info(f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para "
                                 f"{self.configuration['servidor']} e para {self.configuration['servidor2']}")
            messagebox.showinfo(title="Aten????o", message=f"Arquivo {self.titulo.get()}.mxf "
                                                         f"transferido com sucesso para os dois Servidores.")
        elif result_destino1:
            LogService.save_info(f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para "
                                 f"{self.configuration['servidor']} mas apresentou falha o ser transferido para "
                                 f"{self.configuration['servidor2']}")
            messagebox.showwarning(title="Aten????o",
                                   message=f"Arquivo {self.titulo.get()}.mxf "
                                           f"transferido com sucesso para o Servidor 1 mas "
                                           f"apresentou falha ao ser transferido ao Servidor 2.")
        elif result_destino2:
            LogService.save_info(f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para "
                                 f"{self.configuration['servidor2']} mas apresentou falha o ser transferido para "
                                 f"{self.configuration['servidor']}")
            messagebox.showwarning(title="Aten????o",
                                   message=f"Arquivo {self.titulo.get()}.mxf transferido com sucesso para o "
                                           f"Servidor 2 mas apresentou falha ao ser transferido ao Servidor 1.")
        else:
            LogService.save_info(f"Falha ao transferir arquivo {self.titulo.get()}.mxf para "
                                 f"{self.configuration['servidor']} e para {self.configuration['servidor2']}.")
            messagebox.showwarning(title="Aten????o",
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

    def update_progress(self, copied: float, total: float, server: str) -> None:
        porcent = int((copied * 100) / total)
        if self.progressbar['value'] < 100:
            self.progressbar['value'] = porcent
            self.label_porcent["text"] = f"{porcent}% - Transferindo para {server}"

    def show_progressbar(self, value: bool) -> None:
        if value:
            self.progressbar.pack(side=LEFT, padx=1, expand=YES)
            self.label_porcent.pack(side=LEFT, padx=1, expand=YES)
        else:
            self.progressbar.pack_forget()
            self.label_porcent.pack_forget()

    def set_progressbar_determinate(self, value: bool) -> None:
        if value:
            self.progressbar.stop()
            self.progressbar["mode"] = "determinate"
        else:
            self.progressbar["mode"] = "indeterminate"
            self.progressbar.start()

    def update_label_progressbar(self, determinate: bool, text: str) -> None:
        self.set_progressbar_determinate(determinate)
        self.label_porcent["text"] = text

    def change_button_action_state(self, value: bool) -> None:
        if value:
            self.button_action['text'] = 'Enviar ao servidor'
            self.button_action.configure(bootstyle="primary", style="primary.TButton")
        else:
            self.button_action['text'] = 'Parar transfer??ncia'
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
            messagebox.showwarning(title="Aten????o", message="Em configura????es o campo Caminho Servidor 1 devem ser "
                                                            "preenchido.")
            return False
        if self.configuration["usuario"] is None or self.configuration["usuario"] == "":
            messagebox.showwarning(title="Aten????o", message="Em configura????es o campo Usu??rio devem ser preenchido.")
            return False
        if self.arquivo.get() is None or self.arquivo.get() == "":
            self.entry_arquivo.configure(bootstyle="danger")
            messagebox.showwarning(title="Aten????o", message="O campo arquivo deve ser selecionado.")
            return False
        if MyFile.extensao_arquivo(self.arquivo.get()) != ".MXF" \
                and MyFile.extensao_arquivo(self.arquivo.get()) != ".mxf":
            messagebox.showwarning(title="Aten????o", message="O arquivo selecionado deve ser um arquivo com extens??o "
                                                            ".mxf.")
            return False
        if self.titulo.get() is None or self.titulo.get() == "":
            self.entry_titulo.configure(bootstyle="danger")
            self.entry_titulo.focus()
            messagebox.showwarning(title="Aten????o", message="O campo t??tulo deve ser preenchido.")
            return False
        if self.grupo.get() is None or self.grupo.get() == "":
            self.combobox_grupo.configure(bootstyle="danger")
            self.combobox_grupo.focus()
            messagebox.showwarning(title="Aten????o", message="O campo Grupo dever ser selecionado.")
            return False
        return True

