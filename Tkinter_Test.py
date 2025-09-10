import tkinter as tk

# Create the main window
window = tk.Tk()
window.title("My First Tkinter App")
window.geometry("500x500")

# Add a label widget
label = tk.Label(window, text="Hello, Tkinter!", font=("Arial", 18))
label.pack(pady=20)

# Run the GUI event loop
window.mainloop()
