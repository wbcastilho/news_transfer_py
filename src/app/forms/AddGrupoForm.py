import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter import messagebox
from src.business.adapters.MyJSON import MyJSON


class AddGrupoForm(ttk.Frame):
    def __init__(self, master, parent):
        super().__init__(master)
        self.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.master = master
        self.parent = parent

        self.nome_grupo = ttk.StringVar()

        self.button_save = None
        self.button_cancel = None
        self.button_browse2 = None
        self.treeview = None

        self.init_style()
        self.create_config_frame()
        self.create_buttons()

    @staticmethod
    def init_style():
        my_style = ttk.Style()
        my_style.configure('danger.TButton', font=('Helvetica', 10))
        my_style.configure('success.TButton', font=('Helvetica', 10))

    def create_config_frame(self) -> None:
        label_frame = ttk.Labelframe(self, text='Grupo')
        label_frame.pack(fill="x", padx=10, pady=5)

        frame = ttk.Frame(label_frame)
        frame.pack(fill="x", padx=20, pady=10)

        label = ttk.Label(frame, text="Nome", font=('Helvetica', 10))
        label.grid(row=0, column=0, padx=1, sticky=ttk.E, pady=5)

        entry_servidor = ttk.Entry(frame,
                                   textvariable=self.nome_grupo,
                                   width=60,
                                   font=('Helvetica', 10)
                                   )
        entry_servidor.grid(row=0, column=1, padx=2, sticky=ttk.W, pady=5)

    def create_buttons(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        self.button_cancel = ttk.Button(frame, text="Cancelar", bootstyle="secondary", style='danger.TButton',
                                        command=self.on_cancel)
        self.button_cancel.pack(side=RIGHT, padx=5, pady=10)

        self.button_save = ttk.Button(frame, text="Adicionar", bootstyle="success", style='success.TButton',
                                      command=self.on_save)
        self.button_save.pack(side=RIGHT, padx=5, pady=10)

    def on_save(self) -> None:
        if self.nome_grupo.get() == "":
            messagebox.showwarning(title="Atenção", message="O campo Nome deve ser preenchido.")
            return

        tamanho = len(self.parent.treeview.get_children())
        self.parent.treeview.insert('', tamanho + 1, text=self.nome_grupo.get())
        self.master.destroy()

    def on_cancel(self) -> None:
        self.master.destroy()
