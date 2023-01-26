import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter import messagebox
from src.app.forms.AddGrupoForm import AddGrupoForm
from src.business.adapters.MyJSON import MyJSON


class SettingsForm(ttk.Frame):
    def __init__(self, master, parent):
        super().__init__(master)
        self.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.master = master
        self.parent = parent
        self.local_configuration = {
            'servidor': ttk.StringVar(),
            'habilitar_servidor2': ttk.IntVar(),
            'servidor2': ttk.StringVar(),
            'timeout_ack': ttk.IntVar(),
            'usuario': ttk.StringVar()
        }
        self.button_save = None
        self.button_cancel = None
        self.button_browse2 = None
        self.treeview = None

        self.create_config_frame()
        self.create_buttons()
        self.select_checkbutton()
        self.init_configuration()

    def create_config_frame(self) -> None:
        label_frame = ttk.Labelframe(self, text='Configuração Servidor 1')
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

        label_frame = ttk.Labelframe(self, text='Configuração Servidor 2')
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

        label = ttk.Label(frame, text="Usuário")
        label.grid(row=0, column=0, padx=1, sticky=ttk.E, pady=5)

        entry_usuario = ttk.Entry(frame,
                                  textvariable=self.local_configuration['usuario'],
                                  width=60
                                  )
        entry_usuario.grid(row=0, column=1, padx=2, sticky=ttk.W, pady=5)

        label = ttk.Label(frame, text="Grupos")
        label.grid(row=1, column=0, padx=1, sticky=ttk.E, pady=5)

        self.treeview = ttk.Treeview(frame,
                                     columns=('grupo',),
                                     height=5,
                                     selectmode='browse',
                                     show="tree"
                                     )

        self.treeview.column('grupo', stretch=False)
        self.treeview.grid(row=1, column=1, padx=2, sticky=ttk.W, pady=5)

        frame_button = ttk.Frame(frame)
        frame_button.grid(row=1, column=2, padx=2, sticky=ttk.W, pady=5)

        button_adicionar = ttk.Button(frame_button, text="Adicionar", bootstyle="primary", command=self.add)
        button_adicionar.grid(row=0, column=0, padx=2, sticky=ttk.W, pady=5)

        button_remover = ttk.Button(frame_button, text="Remover", bootstyle="danger", command=self.remove)
        button_remover.grid(row=1, column=0, padx=2, sticky=ttk.W, pady=5)

        label = ttk.Label(frame, text="Timeout ACK (minutos)")
        label.grid(row=2, column=0, padx=1, pady=(20, 0), sticky=ttk.E)

        spinbox_timeout = ttk.Spinbox(frame, width=5, justify="center", from_=1, to=20,
                                      textvariable=self.local_configuration["timeout_ack"], wrap=False)
        spinbox_timeout.grid(row=2, column=1, padx=2, pady=(20, 0), sticky=ttk.W)

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
                my_json = MyJSON('config.json', self.parent.configuration)
                my_json.write()

                grupos = []
                for item in self.parent.configuration["grupos"]:
                    grupos.append(item)
                    self.parent.combobox_grupo.configure(values=grupos)

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

    def add(self):
        add_grupo_form = ttk.Toplevel()
        add_grupo_form.title("Adicionar Grupo")
        add_grupo_form.iconbitmap('src/app/assets/favicon.ico')
        add_grupo_form.grab_set()
        add_grupo_form.resizable(False, False)
        AddGrupoForm(add_grupo_form, self)

    def remove(self):
        if len(self.treeview.get_children()) > 0:
            selected_item = self.treeview.selection()[0]
            self.treeview.delete(selected_item)

    def on_cancel(self) -> None:
        self.master.destroy()

    def init_configuration(self) -> None:
        self.local_configuration["servidor"].set(self.parent.configuration["servidor"])
        self.local_configuration["servidor2"].set(self.parent.configuration["servidor2"])
        self.local_configuration["habilitar_servidor2"].set(self.parent.configuration["habilitar_servidor2"])
        self.local_configuration["timeout_ack"].set(self.parent.configuration["timeout_ack"])
        self.local_configuration["usuario"].set(self.parent.configuration["usuario"])

        i = 0
        for item in self.parent.configuration["grupos"]:
            self.treeview.insert('', i, text=item)
            i = i + 1

    def change_configuration(self) -> None:
        self.parent.configuration["servidor"] = self.local_configuration["servidor"].get()
        self.parent.configuration["servidor2"] = self.local_configuration["servidor2"].get()
        self.parent.configuration["habilitar_servidor2"] = self.local_configuration["habilitar_servidor2"].get()
        self.parent.configuration["timeout_ack"] = self.local_configuration["timeout_ack"].get()
        self.parent.configuration["usuario"] = self.local_configuration["usuario"].get()

        self.parent.configuration["grupos"].clear()

        for item in self.treeview.get_children():
            self.parent.configuration["grupos"].append(self.treeview.item(item)["text"])

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
        if self.local_configuration["usuario"].get() == "":
            messagebox.showwarning(title="Atenção", message="O campo Usuário deve ser preenchido.")
            return False
        return True

