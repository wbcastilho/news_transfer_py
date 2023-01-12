from src.forms.MainForm import MainForm
import ttkbootstrap as ttk


if __name__ == '__main__':
    app = ttk.Window(
        title="News Transfer - 1.0",
        resizable=(False, False)
    )
    app.iconbitmap('src/assets/favicon.ico')
    MainForm(app)

    app.mainloop()
