import cv2
import tkinter as tk
from PIL import Image, ImageTk

def update_frame():
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        label.imgtk = img_tk
        label.configure(image=img_tk)
    window.after(30, update_frame)

def on_closing():
    cap.release()
    cv2.destroyAllWindows()
    window.destroy()

window = tk.Tk()
window.title("Video in Tkinter")
window.geometry('1000x498')
window.resizable(0,0)

label = tk.Label(window)
label.pack(side="left")

cap = cv2.VideoCapture(0)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.after(0, update_frame)
window.mainloop()
