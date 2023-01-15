import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from src.data.repository.LogRepository import LogRepository


class LogsForm(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(padx=10, pady=10)
        self.master = master

        self.treeview = None
        self.data_entry = None
        self.datevar = ttk.StringVar()

        self.create_table()
        self.select_date()

    def create_table(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=(0, 20), pady=10)

        self.data_entry = ttk.DateEntry(frame, bootstyle="primary")
        self.data_entry.pack(padx=10, pady=5, side=LEFT)

        button = ttk.Button(frame, text="Pesquisar", bootstyle="primary", command=self.select_date)
        button.pack(side=LEFT)

        self.treeview = ttk.Treeview(self,
                                     bootstyle='primary',
                                     columns=('data', 'log'),
                                     show='headings',
                                     height=20,
                                     selectmode='browse')

        self.treeview.heading('data', text='Data', anchor=W)
        self.treeview.heading('log', text='Mensagem', anchor=W)

        self.treeview.column('data', stretch=False, width=150)
        self.treeview.column('log', stretch=False, width=1050)

        yscroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.treeview.yview)
        yscroll.pack(side=RIGHT, fill=Y)

        xscroll = ttk.Scrollbar(self, orient=HORIZONTAL, command=self.treeview.xview)
        xscroll.pack(side=BOTTOM, fill=X)

        self.treeview.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.treeview.pack()

    def select_date(self):
        data_selecionada = self.data_entry.entry.get()

        self.clear_treeview()
        for log in LogRepository.find(data_selecionada):
            self.treeview.insert('', END, log.id, values=(log.datetime, log.message))

    def clear_treeview(self):
        for item in self.treeview.get_children():
            self.treeview.delete(item)





