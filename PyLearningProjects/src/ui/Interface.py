""" =========================================================
        Прослойка над Tkinter.
        Не знает про задачи и saves.txt.
        Только создаёт окно и виджеты.
    =========================================================
"""
import tkinter as tk
from tkinter import messagebox, simpledialog

from ui.Button import AppButton


class Interface:
    def __init__(self, title="Task Manager", width=400, height=400):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.iconbitmap("../assets/icon.ico")
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg="#000000")

    # ---------- жизненный цикл ----------
    def run(self):
        self.root.mainloop()

    def quit(self):
        self.root.quit()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------- виджеты ----------
    def add_label(self, text, font=("Arial", 12), fg="#ffffff"):
        label = tk.Label(self.root, text=text, bg="#000000", fg=fg, font=font)
        label.pack(pady=3)
        return label

    def add_button(self, text, command, bg=None, width=16):
        kwargs = {"width": width}
        if bg is not None:
            kwargs["bg"] = bg
        button = AppButton(self.root, text, command, **kwargs)
        button.pack(pady=3)
        return button

    def add_entry(self):
        entry = tk.Entry(self.root, width=40)
        entry.pack(pady=3)
        return entry

    def add_text(self, height=5):
        text = tk.Text(self.root, width=40, height=height)
        text.pack(pady=3)
        return text

    def add_listbox(self, height=15):
        listbox = tk.Listbox(self.root, height=height)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)
        return listbox

    # ---------- диалоги ----------
    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def show_warning(self, title, message):
        messagebox.showwarning(title, message)

    def show_yesno(self, title, message):
        return messagebox.askyesno(title, message)

    def show_details(self, title, lines):
        """Модальное окно с многострочным содержимым.

        lines — список строк, будут отображены сверху вниз.
        """
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("350x300")
        win.configure(bg="#000000")
        win.transient(self.root)
        win.grab_set()

        for line in lines:
            tk.Label(win, text=line, bg="#000000", fg="#ffffff",
                     font=("Arial", 12), anchor="w", justify="left",
                     wraplength=320).pack(anchor="w", padx=15, pady=3)

        AppButton(win, "Закрыть", command=win.destroy).pack(pady=15)

    def ask_choice(self, title, prompt, options, default=None):
        """Простой диалог выбора из списка. Возвращает строку или None."""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("300x150")
        win.configure(bg="#000000")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text=prompt, bg="#000000", fg="#ffffff",
                 font=("Arial", 12)).pack(pady=10)

        var = tk.StringVar(value=default or options[0])
        menu = tk.OptionMenu(win, var, *options)
        menu.pack(pady=5)

        result = {"value": None}

        def ok():
            result["value"] = var.get()
            win.destroy()

        def cancel():
            win.destroy()

        frame = tk.Frame(win, bg="#000000")
        frame.pack(pady=10)
        AppButton(frame, "OK", command=ok, width=8).pack(side="left", padx=5)
        AppButton(frame, "Отмена", command=cancel, width=8, bg="#aa3333").pack(side="left", padx=5)

        win.wait_window()
        return result["value"]

    def ask_string(self, title, prompt, default=""):
        """Спросить строку. Возвращает строку или None (если отмена)."""
        return simpledialog.askstring(title, prompt,
                                      initialvalue=default,
                                      parent=self.root)
