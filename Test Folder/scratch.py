import customtkinter
class MyFrame(customtkinter.CTkScrollableFrame):
   def __init__(self, master, **kwargs):
       super().__init__(master, **kwargs)
       self.label = customtkinter.CTkLabel(self, text="Scrollable Frame")
       self.label.grid(row=0, column=0, padx=20)
class App(customtkinter.CTk):
   def __init__(self):
       super().__init__()
       self.my_frame = MyFrame(master=self, width=300, height=200)
       self.my_frame.grid(row=0, column=0, padx=20, pady=20)
app = App()
app.mainloop()