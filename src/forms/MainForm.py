import pathlib
import shutil
from tkinter import filedialog
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pathlib import Path
import threading
import time
import os
from src.forms.SettingsForm import SettingsForm
from src.adapters.MyJSON import MyJSON
from src.adapters.VideoXML import VideoXML
from src.adapters.MyRandom import MyRandom
from src.adapters.AckXML import AckXML
from src.utils.ConvertVideo import ConvertVideo


class SameFileError(OSError):
    """Raised when source and destination are the same file."""


class SpecialFileError(OSError):
    """Raised when trying to do a kind of operation (e.g. copying) which is
    not supported on a special file (e.g. a named pipe)"""


class MainForm(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pack(fill=BOTH, expand=YES)
        self.configuration = {
            'servidor': ""
        }
        self.photo_images = []
        self.enviar = False
        self.BUFFER_SIZE = 4096 * 1024

        self.arquivo = ttk.StringVar()
        self.titulo = ttk.StringVar()
        self.grupo = ttk.StringVar()

        self.grupo_values = []
        self.button_action = None
        self.button_browse = None
        self.combobox_grupo = None
        self.progressbar = None
        self.label_porcent = None

        self.associate_icons()
        self.init_combobox()
        self.create_buttonbar()
        self.create_enviar_frame()
        self.create_progressbar_frame()
        self.read_config()

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
        self.grupo_values.append("BDC CIDADE")
        self.grupo_values.append("EPTV 1")
        self.grupo_values.append("EPTV 2")
        self.grupo_values.append("FUTSAL")
        self.grupo_values.append("GELADEIRA")
        self.grupo_values.append("PASSAGENS")
        self.grupo_values.append("VINHETAS BDC")
        self.grupo_values.append("VINHETAS EPTV 1")
        self.grupo_values.append("VINHETAS EPTV 2")

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

    def create_enviar_frame(self) -> None:
        label_frame = ttk.Labelframe(self, text='Enviar')
        label_frame.pack(fill="x", padx=10, pady=(5, 15))
        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=15)

        label = ttk.Label(frame, text="Arquivo")
        label.grid(row=0, column=0, padx=1, sticky=ttk.E)
        arquivo = ttk.Entry(frame, width=100, textvariable=self.arquivo, state="disabled")
        arquivo.grid(row=0, column=1, padx=2, sticky=ttk.W)
        self.button_browse = ttk.Button(frame, text="Selecionar Arquivo", bootstyle=(INFO, OUTLINE),
                                        command=self.on_browse)
        self.button_browse.grid(row=0, column=2, padx=2)

        label = ttk.Label(frame, text="Retranca / Título")
        label.grid(row=1, column=0, padx=1, pady=(20, 0), sticky=ttk.E)
        titulo = ttk.Entry(frame, width=50, textvariable=self.titulo)
        titulo.grid(row=1, column=1, padx=2, pady=(20, 0), sticky=ttk.W)

        label = ttk.Label(frame, text="Grupo")
        label.grid(row=2, column=0, padx=1, pady=(20, 0), sticky=ttk.E)
        self.combobox_grupo = ttk.Combobox(frame, width=20, justify="center", textvariable=self.grupo,
                                           values=self.grupo_values)
        self.combobox_grupo.grid(row=2, column=1, padx=2, pady=(20, 0), sticky=ttk.W)

        self.button_action = ttk.Button(frame, width=100, text='Enviar ao servidor', command=lambda: self.on_action())
        self.button_action.grid(row=3, column=1, padx=2, pady=(20, 0), sticky=ttk.W)

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

    def read_config(self) -> None:
        try:
            my_json = MyJSON('config.json', self.configuration)
            my_json.read()
        except PermissionError as err:
            # SimpleLog.save(err)
            messagebox.showwarning(title="Atenção", message=err)
        except FileNotFoundError as err:
            # SimpleLog.save(err)
            messagebox.showwarning(title="Atenção", message=err)
        except Exception as err:
            # SimpleLog.save(err)
            messagebox.showwarning(title="Atenção", message=err)

    def on_settings(self) -> None:
        if not self.enviar:
            setting_form = ttk.Toplevel()
            setting_form.title("Configurações")
            setting_form.iconbitmap('src/assets/favicon.ico')
            setting_form.grab_set()
            setting_form.resizable(False, False)
            SettingsForm(setting_form, self.configuration)
        else:
            messagebox.showwarning(title="Atenção", message="Para abrir a janela de configurações é necessário antes "
                                                            "parar a monitoração clicando no botão Parar.")

    def on_logs(self):
        pass

    def on_browse(self) -> None:
        filetypes = (
            ('MXF Files', '*.mxf'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(title='Selecionar Arquivo', initialdir='c:/', filetypes=filetypes)
        if filename:
            self.arquivo.set(filename)

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
        try:
            bufsize = self.BUFFER_SIZE
            follow = False

            dest = self.copy_with_callback(self.arquivo.get(),
                                           f'{self.configuration["servidor"]}\\{self.titulo.get()}.mxf',
                                           follow_symlinks=follow,
                                           callback=None,
                                           buffer_size=bufsize,
                                           )
            self.gerar_xml(self.configuration["servidor"], self.titulo.get(), self.arquivo.get())
            self.checar_ack(self.configuration["servidor"], self.titulo.get())

            if self.enviar:
                self.enviar = False
                self.clean_fields()
                messagebox.showinfo(title="Atenção", message=f"Arquivo {dest} copiado com sucesso.")
            else:
                messagebox.showwarning(title="Atenção", message="Transferência cancelada pelo usuário")
        except Exception as ex:
            messagebox.showerror(title="Erro", message=ex)
        finally:
            self.show_progressbar(False)
            self.set_progressbar_determinate(True)
            self.label_porcent["text"] = "0%"
            self.change_button_action_state(True)

    def copy_with_callback(self, src, dest, callback=None, follow_symlinks=True, buffer_size=4096 * 1024):
        try:
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
                            fsrc, fdest, callback=callback, total=size, length=buffer_size
                        )
            shutil.copymode(str(srcfile), str(destfile))
            return str(destfile)
        except Exception as ex:
            raise Exception(f"Falha ao copiar arquivo. {ex}")

    def copy_file(self, fsrc, fdest, callback, total, length):
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

            self.update_progress(copied, total)

            if callback is not None:
                callback(len(buf), copied, total)

    def gerar_xml(self, servidor, titulo, arquivo):
        try:
            self.set_progressbar_determinate(False)
            self.label_porcent["text"] = "Gerando arquivo xml..."

            dto = {
                'codigo': MyRandom.gerar_codigo(),
                'arquivo': titulo,
                'titulo': titulo,
                'grupo': 'Editores',
                'operador': 'Operador',
                'markIn': '000',
                'markOut': ConvertVideo.get_duration(arquivo),
                'remover': '0'
            }
            VideoXML.create(caminho=servidor, arquivo=f'{titulo}.xml', dto=dto)
        except Exception as ex:
            raise Exception(f"Falha ao gerar arquivo xml. {ex}")

    def checar_ack(self, caminho, nome_arquivo):
        try:
            self.label_porcent["text"] = "Aguardando arquivo de confirmação..."
            size_aux = 0
            arquivo = os.path.join(caminho, f"{nome_arquivo}.ack")

            while True:
                if not self.enviar:
                    self.set_progressbar_determinate(False)
                    self.label_porcent["text"] = "Cancelando..."
                    return

                if os.path.isfile(arquivo):
                    size = os.stat(arquivo).st_size
                    if size_aux < size:
                        size_aux = size
                        continue

                    result = AckXML.read(caminho=caminho, arquivo=f"{nome_arquivo}.ack")
                    os.remove(arquivo)

                    if result[0] == "0":
                        return
                    elif result[0] == "4" \
                            or result[0] == "8" \
                            or result[0] == "9" \
                            or result[0] == "10":
                        raise Exception(f"Falha ao receber arquivo de confirmação. {result[1]}")
                    else:
                        raise Exception("Erro desconhecido ao receber arquivo de confirmação.")
        except Exception as ex:
            raise Exception(ex)

    def update_progress(self, copied: float, total: float) -> None:
        porcent = int((copied * 100) / total)
        if self.progressbar['value'] < 100:
            self.progressbar['value'] = porcent
            self.label_porcent["text"] = f"{porcent}%"

    def show_progressbar(self, value: bool) -> None:
        if value:
            self.progressbar.pack(side=LEFT, padx=1, expand=YES)
            self.label_porcent.pack(side=LEFT, padx=1, expand=YES)
        else:
            self.progressbar.pack_forget()
            self.label_porcent.pack_forget()

    def set_progressbar_determinate(self, value: bool) -> None:
        if value:
            self.progressbar["mode"] = "determinate"
        else:
            self.progressbar["mode"] = "indeterminate"
            self.progressbar.start()

    def change_button_action_state(self, value: bool) -> None:
        if value:
            self.button_action['text'] = 'Enviar ao servidor'
        else:
            self.button_action['text'] = 'Parar transferência'

    def clean_fields(self) -> None:
        self.arquivo.set("")
        self.titulo.set("")
        self.grupo.set("")

    def validate(self) -> bool:
        if self.configuration["servidor"] is None or self.configuration["servidor"] == "":
            messagebox.showwarning(title="Atenção", message="Em configurações todos os campos devem ser "
                                                            "preenchidos.")
            return False
        if self.arquivo.get() is None or self.arquivo.get() == "":
            messagebox.showwarning(title="Atenção", message="O campo arquivo deve ser selecionado.")
            return False
        if self.file_extension(self.arquivo.get()) != ".MXF":
            messagebox.showwarning(title="Atenção", message="O arquivo selecionado deve ser um arquivo com extensão "
                                                            ".mxf.")
            return False
        if self.titulo.get() is None or self.titulo.get() == "":
            messagebox.showwarning(title="Atenção", message="O campo título deve ser preenchido.")
            return False
        if self.grupo.get() is None or self.grupo.get() == "":
            messagebox.showwarning(title="Atenção", message="O campo Grupo dever ser selecionado.")
            return False
        return True

    @staticmethod
    def file_extension(src):
        extension = pathlib.Path(src).suffix
        return extension
