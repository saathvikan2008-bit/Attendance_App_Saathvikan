import tkinter as tk

root = tk.Tk()
root.geometry("300x100")

entry = tk.Entry(root)
entry.pack()

def show_text():
    print("Input:", entry.get())

btn = tk.Button(root, text="Print Input", command=show_text)
btn.pack()

root.mainloop()

