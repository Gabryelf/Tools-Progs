import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

root = tk.Tk()
root.title("Traine App")
root.geometry("500x500")
root.configure(background="black")


def ask_yes_no(title, message):
    return messagebox.askyesno(f"{title}", message=f"{message}")


def on_exit():
    if ask_yes_no("Выход", "Вы действительно хотите выйти"):
        root.quit()


but_quit = tk.Button(root, text="EXIT", command=on_exit, bg="red", fg="white")
but_quit.pack()

dark_var = tk.BooleanVar(value=False)

label = tk.Label(root, text="Привет")
label.pack(pady=20)

def toggle_theme():
    if dark_var.get():
        root.configure(bg="black")
        label.config(bg="black", fg="white")
    else:
        root.configure(bg="SystemButtonFace")
        label.config(bg="SystemButtonFace", fg="black")

check = tk.Checkbutton(root, text="Тёмная тема",
                       variable=dark_var, command=toggle_theme)
check.pack()

menubar = tk.Menu(root)

file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Новый", command=lambda: print("Новый"))
file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.quit)
menubar.add_cascade(label="Файл", menu=file_menu)

help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="О программе",
                      command=lambda: messagebox.showinfo("О программе", "Traine App v1.0"))
menubar.add_cascade(label="Справка", menu=help_menu)

root.config(menu=menubar)

colors = {"Красный": "red", "Зелёный": "green", "Синий": "blue"}

label = tk.Label(root, text="Выбери цвет", width=20, height=3)
label.pack(pady=10)

combo = ttk.Combobox(root, values=list(colors.keys()), state="readonly")
combo.pack()

def on_select(event):
    name = combo.get()
    label.config(bg=colors[name], text=name)

combo.bind("<<ComboboxSelected>>", on_select)

progress = ttk.Progressbar(root, maximum=100, length=250)
progress.pack(pady=20)

button = tk.Button(root, text="Запустить")
button.pack()

def step(value=0):
    progress["value"] = value
    if value < 100:
        root.after(50, step, value + 5)   # через 50 мс — следующий шаг
    else:
        button.config(state="normal")

def start():
    button.config(state="disabled")
    step(0)

button.config(command=start)

root.mainloop()

