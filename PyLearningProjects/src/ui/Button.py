import tkinter as tk


class AppButton(tk.Button):
    def __init__(self, master, text, command, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg="#020202",
            activebackground="#555555",
            activeforeground="#ffffff",
            font=("Arial", 11, 'bold'),
            **kwargs
        )
