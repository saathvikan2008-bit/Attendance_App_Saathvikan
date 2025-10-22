import customtkinter as ctk

root = ctk.CTk()
root.iconbitmap("Bitmaps/logo_new.ico")   # set the app icon
dlg = ctk.CTkInputDialog(text="Enter ID", title="Remove User")
result = dlg.get_input()
print(result)