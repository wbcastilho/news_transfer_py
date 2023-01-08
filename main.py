from src.forms.MainForm import MainForm
import ttkbootstrap as ttk


if __name__ == '__main__':
    app = ttk.Window(
        title="News Transfer",
        resizable=(False, False)
    )
    app.iconbitmap('src/assets/favicon.ico')
    MainForm(app)

    app.mainloop()
