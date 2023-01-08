import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter import messagebox
from src.adapters.MyJSON import MyJSON


class SettingsForm(ttk.Frame):
    def __init__(self, master, configuration):
        super().__init__(master)
        self.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.master = master
        self.configuration = configuration
        self.local_configuration = {
            'servidor': ttk.StringVar()
        }
        self.button_save = None
        self.button_cancel = None
        self.button_browse = None

        self.init_configuration()
        self.create_config_frame()
        self.create_buttons()

    def create_config_frame(self) -> None:
        label_frame = ttk.Labelframe(self, text='Configuração Destino')
        label_frame.pack(fill="x", padx=10, pady=5)

        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=10)

        label = ttk.Label(frame, text="Caminho")
        label.grid(row=0, column=0, padx=1, sticky=ttk.E, pady=5)

        entry_servidor = ttk.Entry(frame,
                                   textvariable=self.local_configuration['servidor'],
                                   width=100,
                                   state="disabled"
                                   )
        entry_servidor.grid(row=0, column=1, padx=2, sticky=ttk.W, pady=5)

        self.button_browse = ttk.Button(frame, text="Selecionar Pasta", bootstyle=(INFO, OUTLINE),
                                        command=self.on_browse)
        self.button_browse.grid(row=0, column=2, padx=2)

    def create_buttons(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        self.button_cancel = ttk.Button(frame, text="Cancelar", bootstyle="secondary", command=self.on_cancel)
        self.button_cancel.pack(side=RIGHT, padx=5, pady=10)

        self.button_save = ttk.Button(frame, text="Salvar", bootstyle="success", command=self.on_save)
        self.button_save.pack(side=RIGHT, padx=5, pady=10)

    def on_save(self) -> None:
        try:
            if self.validate():
                self.change_configuration()
                my_json = MyJSON('config.json', self.configuration)
                my_json.write()
                # SimpleLog.save("Configurações salvas com sucesso!")
                self.master.destroy()
        except Exception as err:
            # SimpleLog.save(err)
            messagebox.showerror(title="Erro", message=err)

    def on_browse(self):
        path = filedialog.askdirectory(initialdir=r'c:\\', title="Selecionar Pasta")
        if path:
            self.local_configuration['servidor'].set(path)

    def on_cancel(self) -> None:
        self.master.destroy()

    def init_configuration(self) -> None:
        self.local_configuration["servidor"].set(self.configuration["servidor"])

    def change_configuration(self) -> None:
        self.configuration["servidor"] = self.local_configuration["servidor"].get()

    def validate(self) -> bool:
        if self.local_configuration["servidor"] == "":
            messagebox.showwarning(title="Atenção", message="O campo Servidor deve ser preenchido.")
            return False
        return True

