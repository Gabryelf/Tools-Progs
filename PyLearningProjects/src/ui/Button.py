import tkinter as tk


class AppButton(tk.Button):
    def __init__(self, master, text, command, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            width=16,
            height=1,
            bg="#333333",
            fg="#ffffff",
            activebackground="#555555",
            activeforeground="#ffffff",
            font=("Arial", 11),
            **kwargs
        )
