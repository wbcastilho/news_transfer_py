import ttkbootstrap as ttk
from tkinter import filedialog
from tkinter import messagebox
from ttkbootstrap.constants import *
from src.business.utils.Helper import Helper
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
            'usuario': ttk.StringVar(),
            'remover': ttk.IntVar()
        }
        self.button_save = None
        self.button_cancel = None
        self.button_browse2 = None
        self.entry_servidor1 = None
        self.entry_servidor2 = None
        self.entry_usuario = None
        self.spinbox_timeout = None
        self.treeview = None

        self.create_config_frame()
        self.create_buttons()
        self.init_configuration()
        self.select_checkbutton()

    def create_config_frame(self) -> None:
        label_frame = ttk.Labelframe(self, text='Configuração Servidor 1')
        label_frame.pack(fill="x", padx=10, pady=5)

        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=10)

        label = ttk.Label(frame, text="Caminho", font=('Helvetica', 10))
        label.grid(row=0, column=0, padx=1, sticky=ttk.E, pady=5)

        self.entry_servidor1 = ttk.Entry(frame,
                                         textvariable=self.local_configuration['servidor'],
                                         width=100,
                                         state="disabled",
                                         font=('Helvetica', 10)
                                         )
        self.entry_servidor1.grid(row=0, column=1, padx=2, sticky=ttk.W, pady=5)

        button_browse = ttk.Button(frame, text="Selecionar Pasta", bootstyle=(INFO, OUTLINE),
                                   style='info.Outline.TButton', command=lambda: self.on_browse(1))
        button_browse.grid(row=0, column=2, padx=2)

        label_frame = ttk.Labelframe(self, text='Configuração Servidor 2')
        label_frame.pack(fill="x", padx=10, pady=5)

        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=10)

        label = ttk.Label(frame, text="Habilitar", font=('Helvetica', 10))
        label.grid(row=0, column=0, padx=1, sticky=ttk.E, pady=5)

        chk_habilitar = ttk.Checkbutton(frame, variable=self.local_configuration['habilitar_servidor2'],
                                        onvalue=1, offvalue=0, command=self.select_checkbutton)
        chk_habilitar.grid(row=0, column=1, padx=1, sticky=ttk.W, pady=5)

        label = ttk.Label(frame, text="Caminho", font=('Helvetica', 10))
        label.grid(row=1, column=0, padx=1, sticky=ttk.E, pady=5)

        self.entry_servidor2 = ttk.Entry(frame,
                                         textvariable=self.local_configuration['servidor2'],
                                         width=100,
                                         state="disabled",
                                         font=('Helvetica', 10)
                                         )
        self.entry_servidor2.grid(row=1, column=1, padx=2, sticky=ttk.W, pady=5)

        self.button_browse2 = ttk.Button(frame, text="Selecionar Pasta", bootstyle=(INFO, OUTLINE),
                                         state="disabled", style='info.Outline.TButton',
                                         command=lambda: self.on_browse(2))
        self.button_browse2.grid(row=1, column=2, padx=2)

        label_frame = ttk.Labelframe(self, text='Configuração Geral')
        label_frame.pack(fill="x", padx=10, pady=5)

        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=10)

        label = ttk.Label(frame, text="Usuário", font=('Helvetica', 10))
        label.grid(row=0, column=0, padx=1, sticky=ttk.E, pady=5)

        self.entry_usuario = ttk.Entry(frame,
                                       textvariable=self.local_configuration['usuario'],
                                       width=40,
                                       font=('Helvetica', 10)
                                       )
        self.entry_usuario.grid(row=0, column=1, padx=2, sticky=ttk.W, pady=5)
        self.entry_usuario.bind('<Key>', lambda event: self.entry_usuario.configure(bootstyle="default"))

        label = ttk.Label(frame, text="Grupos", font=('Helvetica', 10))
        label.grid(row=1, column=0, padx=1, sticky=ttk.NE, pady=5)

        self.treeview = ttk.Treeview(frame,
                                     columns=('grupo',),
                                     height=5,
                                     selectmode='browse',
                                     show="tree"
                                     )

        self.treeview.column('grupo', stretch=False, width=170)
        self.treeview.grid(row=1, column=1, padx=2, sticky=ttk.W, pady=5)

        frame_button = ttk.Frame(frame)
        frame_button.grid(row=1, column=2, padx=2, sticky=ttk.W, pady=5)

        button_adicionar = ttk.Button(frame_button, text="Adicionar", bootstyle="primary", style='primary.TButton',
                                      command=self.add)
        button_adicionar.grid(row=0, column=0, padx=2, sticky=ttk.W, pady=5)

        button_remover = ttk.Button(frame_button, text="Remover", bootstyle="danger", style='danger.TButton',
                                    command=self.remove)
        button_remover.grid(row=1, column=0, padx=2, sticky=ttk.W, pady=5)

        label = ttk.Label(frame, text="Timeout ACK (minutos)", font=('Helvetica', 10))
        label.grid(row=2, column=0, padx=1, pady=5, sticky=ttk.E)

        self.spinbox_timeout = ttk.Spinbox(frame, width=5, justify="center", from_=1, to=20,
                                           textvariable=self.local_configuration["timeout_ack"], wrap=False,
                                           font=('Helvetica', 10))
        self.spinbox_timeout.grid(row=2, column=1, padx=2, pady=5, sticky=ttk.W)
        self.spinbox_timeout.bind('<Key>', lambda event: self.spinbox_timeout.configure(bootstyle="default"))
        self.spinbox_timeout.bind('<FocusIn>', lambda event: self.spinbox_timeout.configure(bootstyle="default"))

        label = ttk.Label(frame, text="Remover Arquivos", font=('Helvetica', 10))
        label.grid(row=3, column=0, padx=1, sticky=ttk.E, pady=5)

        chk_remover = ttk.Checkbutton(frame, onvalue=1, offvalue=0, variable=self.local_configuration['remover'])
        chk_remover.grid(row=3, column=1, padx=1, sticky=ttk.W, pady=5)

    def create_buttons(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        self.button_cancel = ttk.Button(frame, text="Cancelar", bootstyle="secondary", style='secondary.TButton',
                                        command=self.on_cancel)
        self.button_cancel.pack(side=RIGHT, padx=5, pady=10)

        self.button_save = ttk.Button(frame, text="Salvar", bootstyle="success", style='success.TButton',
                                      command=self.on_save)
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
                self.entry_servidor1.configure(bootstyle="default")
                self.local_configuration['servidor'].set(path)
            else:
                self.entry_servidor2.configure(bootstyle="default")
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
        self.local_configuration["remover"].set(self.parent.configuration["remover"])

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
        self.parent.configuration["remover"] = self.local_configuration["remover"].get()

        self.parent.configuration["grupos"].clear()

        for item in self.treeview.get_children():
            self.parent.configuration["grupos"].append(self.treeview.item(item)["text"])

    def validate(self) -> bool:
        if self.local_configuration["servidor"].get() == "":
            self.entry_servidor1.configure(bootstyle="danger")
            self.entry_servidor1.focus()
            messagebox.showwarning(title="Atenção", message="O campo Caminho Servidor 1 deve ser preenchido.")
            return False
        if self.local_configuration['habilitar_servidor2'].get() and \
                self.local_configuration["servidor2"].get() == "":
            self.entry_servidor2.configure(bootstyle="danger")
            self.entry_servidor2.focus()
            messagebox.showwarning(title="Atenção", message="O campo Caminho Servidor 2 deve ser preenchido.")
            return False
        if self.local_configuration['habilitar_servidor2'] and \
                self.local_configuration["servidor"].get() == self.local_configuration["servidor2"].get():
            self.entry_servidor2.configure(bootstyle="danger")
            self.entry_servidor2.focus()
            messagebox.showwarning(title="Atenção", message="O campo Caminho Servidor 1 deve ser diferente do campo "
                                                            "Caminho Servidor 2 deve ser preenchido.")
            return False
        if self.local_configuration["usuario"].get() == "":
            self.entry_usuario.configure(bootstyle="danger")
            self.entry_usuario.focus()
            messagebox.showwarning(title="Atenção", message="O campo Usuário deve ser preenchido.")
            return False
        if Helper.possui_caractere_especial(self.local_configuration["usuario"].get()):
            self.entry_usuario.configure(bootstyle="danger")
            self.entry_usuario.focus()
            messagebox.showwarning(title="Atenção", message="Não são permitidos acentos e caracteres especiais no "
                                                            "campo Usuário. Só são permitidos letras, números, "
                                                            "underline e hífen.")
            return False
        if len(self.treeview.get_children()) == 0:
            self.treeview.configure(bootstyle="danger")
            self.treeview.focus()
            messagebox.showwarning(title="Atenção", message="O campo Grupos deve ter pelo menos um item adicionado.")
            return False
        if self.local_configuration["timeout_ack"].get() <= 0 or self.local_configuration["timeout_ack"].get() > 20:
            self.spinbox_timeout.configure(bootstyle="danger")
            messagebox.showwarning(title="Atenção", message="O campo Timeout ACK deve ser preenchido.")
            return False
        return True

