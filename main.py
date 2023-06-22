from src.app.forms.MainForm import MainForm
import ttkbootstrap as ttk


if __name__ == '__main__':
    app = ttk.Window(
        title="News Transfer - 2.2",
        resizable=(False, False)
    )

    # Define alterações nos estilos dos botões
    app.style.configure('danger.TButton', font=('Helvetica', 10))
    app.style.configure('primary.TButton', font=('Helvetica', 10))
    app.style.configure('secondary.TButton', font=('Helvetica', 10))
    app.style.configure('success.TButton', font=('Helvetica', 10))
    app.style.configure('info.Outline.TButton', font=('Helvetica', 10))
    app.style.configure('primary.Outline.TButton', font=('Helvetica', 10))

    app.iconbitmap('src/app/assets/favicon.ico')
    MainForm(app)

    app.mainloop()
