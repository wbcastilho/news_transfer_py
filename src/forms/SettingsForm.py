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
            'servidor': ttk.StringVar(),
            'habilitar_servidor2': ttk.IntVar(),
            'servidor2': ttk.StringVar(),
            'timeout_ack': ttk.IntVar()
        }
        self.button_save = None
        self.button_cancel = None
        self.button_browse2 = None

        self.init_configuration()
        self.create_config_frame()
        self.create_buttons()
        self.select_checkbutton()

    def create_config_frame(self) -> None:
        label_frame = ttk.Labelframe(self, text='Configuração Destino 1')
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

        button_browse = ttk.Button(frame, text="Selecionar Pasta", bootstyle=(INFO, OUTLINE),
                                   command=lambda: self.on_browse(1))
        button_browse.grid(row=0, column=2, padx=2)

        label_frame = ttk.Labelframe(self, text='Configuração Destino 2')
        label_frame.pack(fill="x", padx=10, pady=5)

        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=10)

        label = ttk.Label(frame, text="Habilitar")
        label.grid(row=0, column=0, padx=1, sticky=ttk.E, pady=5)

        chk_habilitar = ttk.Checkbutton(frame, variable=self.local_configuration['habilitar_servidor2'],
                                        onvalue=1, offvalue=0, command=self.select_checkbutton)
        chk_habilitar.grid(row=0, column=1, padx=1, sticky=ttk.W, pady=5)

        label = ttk.Label(frame, text="Caminho")
        label.grid(row=1, column=0, padx=1, sticky=ttk.E, pady=5)

        entry_servidor = ttk.Entry(frame,
                                   textvariable=self.local_configuration['servidor2'],
                                   width=100,
                                   state="disabled"
                                   )
        entry_servidor.grid(row=1, column=1, padx=2, sticky=ttk.W, pady=5)

        self.button_browse2 = ttk.Button(frame, text="Selecionar Pasta", bootstyle=(INFO, OUTLINE),
                                         state="disabled", command=lambda: self.on_browse(2))
        self.button_browse2.grid(row=1, column=2, padx=2)

        label_frame = ttk.Labelframe(self, text='Configuração Geral')
        label_frame.pack(fill="x", padx=10, pady=5)

        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=10)

        label = ttk.Label(frame, text="Timeout Arquivo de Checagem")
        label.grid(row=0, column=0, padx=1, pady=(20, 0), sticky=ttk.E)

        spinbox_timeout = ttk.Spinbox(frame, width=5, justify="center", from_=1, to=20,
                                      textvariable=self.local_configuration["timeout_ack"], wrap=False)
        spinbox_timeout.grid(row=0, column=1, padx=2, pady=(20, 0), sticky=ttk.W)

    def create_buttons(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        self.button_cancel = ttk.Button(frame, text="Cancelar", bootstyle="secondary", command=self.on_cancel)
        self.button_cancel.pack(side=RIGHT, padx=5, pady=10)

        self.button_save = ttk.Button(frame, text="Salvar", bootstyle="success", command=self.on_save)
        self.button_save.pack(side=RIGHT, padx=5, pady=10)

    def select_checkbutton(self):
        if self.local_configuration['habilitar_servidor2'].get() == 1:
            self.button_browse2["state"] = "enabled"
        else:
            self.button_browse2["state"] = "disabled"

    def on_save(self) -> None:
        try:
            if self.validate():
                self.change_configuration()
                my_json = MyJSON('config.json', self.configuration)
                my_json.write()
                self.master.destroy()
        except Exception as err:
            messagebox.showerror(title="Erro", message=err)

    def on_browse(self, servidor):
        path = filedialog.askdirectory(initialdir=r'c:\\', title="Selecionar Pasta")
        if path:
            if servidor == 1:
                self.local_configuration['servidor'].set(path)
            else:
                self.local_configuration['servidor2'].set(path)

    def on_cancel(self) -> None:
        self.master.destroy()

    def init_configuration(self) -> None:
        self.local_configuration["servidor"].set(self.configuration["servidor"])
        self.local_configuration["servidor2"].set(self.configuration["servidor2"])
        self.local_configuration["habilitar_servidor2"].set(self.configuration["habilitar_servidor2"])
        self.local_configuration["timeout_ack"].set(self.configuration["timeout_ack"])

    def change_configuration(self) -> None:
        self.configuration["servidor"] = self.local_configuration["servidor"].get()
        self.configuration["servidor2"] = self.local_configuration["servidor2"].get()
        self.configuration["habilitar_servidor2"] = self.local_configuration["habilitar_servidor2"].get()
        self.configuration["timeout_ack"] = self.local_configuration["timeout_ack"].get()

    def validate(self) -> bool:
        if self.local_configuration["servidor"].get() == "":
            messagebox.showwarning(title="Atenção", message="O campo Caminho Destino 1 deve ser preenchido.")
            return False
        if self.local_configuration["servidor2"].get() == "":
            messagebox.showwarning(title="Atenção", message="O campo Caminho Destino 2 deve ser preenchido.")
            return False
        if self.local_configuration["servidor"].get() == self.local_configuration["servidor2"].get():
            messagebox.showwarning(title="Atenção", message="O campo Caminho Destino 1 deve ser diferente do campo "
                                                            "Caminho Destino 2 deve ser preenchido.")
            return False
        return True

