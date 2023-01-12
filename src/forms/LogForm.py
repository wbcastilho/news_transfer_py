import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from src.data.repository.LogRepository import LogRepository


class LogsForm(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(padx=10, pady=10)
        self.master = master

        self.treeview = None

        self.create_table()
        self.load_data()

    def create_table(self):
        self.treeview = ttk.Treeview(self,
                                     bootstyle='primary',
                                     columns=('data', 'log'),
                                     show='headings',
                                     height=20,
                                     selectmode='browse')

        self.treeview.heading('data', text='Data', anchor=W)
        self.treeview.heading('log', text='Mensagem', anchor=W)

        self.treeview.column('data', stretch=False, width=150)
        self.treeview.column('log', stretch=False, width=650)

        yscroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.treeview.yview)
        yscroll.pack(side=RIGHT, fill=Y)

        xscroll = ttk.Scrollbar(self, orient=HORIZONTAL, command=self.treeview.xview)
        xscroll.pack(side=BOTTOM, fill=X)

        self.treeview.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.treeview.pack()

    def load_data(self):
        for log in LogRepository.all():
            self.treeview.insert('', END, log.id, values=(log.datetime, log.message))





