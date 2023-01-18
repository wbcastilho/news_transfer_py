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
        self.yscroll = None
        self.xscroll = None
        self.datevar = ttk.StringVar()

        self.create_table()
        self.select_date()
        # self.select_test()

    def create_table(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=(0, 20), pady=10)

        self.data_entry = ttk.DateEntry(frame, bootstyle="primary")
        self.data_entry.pack(padx=10, pady=5, side=LEFT)

        button = ttk.Button(frame, text="Pesquisar", bootstyle="primary", command=self.select_date)
        button.pack(side=LEFT)

        self.treeview = ttk.Treeview(self,
                                     bootstyle='primary',
                                     columns=('data', 'type_log', 'log'),
                                     show='headings',
                                     height=20,
                                     selectmode='browse')

        # configuracao cabecalho
        self.treeview.heading('data', text='Data', anchor=W)
        self.treeview.heading('type_log', text='Tipo', anchor=W)
        self.treeview.heading('log', text='Mensagem', anchor=W)

        # configuracao colunas
        self.treeview.column('data', stretch=False, width=130)
        self.treeview.column('type_log', stretch=False, width=80)
        self.treeview.column('log', stretch=False, width=600)

        # configuracao yscroll
        self.yscroll = ttk.Scrollbar(self, orient=VERTICAL, command=self.treeview.yview)
        self.yscroll.pack(side=RIGHT, fill=Y)

        # configuracao xscroll
        self.xscroll = ttk.Scrollbar(self, orient=HORIZONTAL, command=self.treeview.xview)
        self.xscroll.pack(side=BOTTOM, fill=X)

        # configuracao scroll
        self.treeview.configure(yscrollcommand=self.yscroll.set, xscrollcommand=self.xscroll.set)

        # configuracao cor das linhas
        self.treeview.tag_configure('info', foreground='blue')
        self.treeview.tag_configure('warning', foreground='dark goldenrod')
        self.treeview.tag_configure('error', foreground='red')
        self.treeview.tag_configure('odd', background='white smoke')

        self.treeview.pack(expand=YES, fill=BOTH)

    def select_date(self):
        maior = 0
        i = 0
        # show_xscroll = False
        self.treeview.column('log', stretch=False, width=600)
        data_selecionada = self.data_entry.entry.get()

        self.clear_treeview()
        logs = LogRepository.find(data_selecionada)

        if len(logs) < 19:
            self.yscroll.pack_forget()

        for log in logs:
            tamanho = len(log.message)
            if tamanho > maior:
                maior = tamanho
                if tamanho > 100:
                    # show_xscroll = True
                    x = (600 * tamanho // 100)
                    self.treeview.column('log', stretch=False, width=x)

            if i % 2 == 0:
                self.treeview.insert('',
                                     END, log.id,
                                     values=(log.datetime, log.type_log.capitalize(), log.message),
                                     tags=(log.type_log,))
            else:
                self.treeview.insert('',
                                     END, log.id,
                                     values=(log.datetime, log.type_log.capitalize(), log.message),
                                     tags=("odd", log.type_log,))
            i = i + 1

        '''if not show_xscroll:
            self.xscroll.pack_forget()'''

    def select_test(self):
        # self.treeview.configure(yscrollcommand=self.yscroll.set)

        # self.yscroll.pack_forget()
        # self.xscroll.pack_forget()

        self.clear_treeview()

        self.treeview.insert('', END, 0, values=('18/01/2023 19:06:00', 'Error',
                                                 '01234567890123456789012345678901234567890123456789'
                                                 '01234567890123456789012345678901234567890'))
        self.treeview.insert('', END, 1, values=('18/01/2023 19:07:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 2, values=('18/01/2023 19:08:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 3, values=('18/01/2023 19:09:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 4, values=('18/01/2023 19:10:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 5, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 6, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 7, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 8, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        '''self.treeview.insert('', END, 9, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 10, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 11, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 12, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 13, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 14, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 15, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 16, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 17, values=('18/01/2023 19:11:00', 'Error', 'Teste'))
        self.treeview.insert('', END, 18, values=('18/01/2023 19:11:01', 'Error', 'Teste'))
        self.treeview.insert('', END, 19, values=('18/01/2023 19:11:02', 'Error', 'Teste'))'''

    def clear_treeview(self):
        for item in self.treeview.get_children():
            self.treeview.delete(item)





