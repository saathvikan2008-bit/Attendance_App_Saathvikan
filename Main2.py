from deepface import DeepFace
import cv2
import os
import csv
import datetime
import tkinter as tk
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk

current_dir = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_dir,"RegisteredFaces")
records_dir = os.path.join(current_dir,"Records")

os.makedirs(db_path, exist_ok=True)
os.makedirs(records_dir, exist_ok=True)

class RecognitionWindow:
    def __init__(self, parent):
        self.top = Toplevel(parent)
        self.top.title("Face Recognition")
        self.top.geometry('800x600')
        self.video_label = tk.Label(self.top)
        self.video_label.pack(padx = 10, pady = 10)
        self.status_label = tk.Label(self.top, text='Status:Online', font = ("Arial", 12))
        self.status_label.pack()
        self.close_button = tk.Button(self.top, text='Close', command=self.close)
        self.close_button.pack(pady = 10)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.top.protocol('WM_DELETE_WINDOW', self.close)
        self.update_frame()
        self.top.geometry(f'{self.frame.shape[1]+10}x600')

    def update_frame(self):
        if self.running:
            result, self.frame = self.cap.read()
            if result:
                self.frame = cv2.flip(self.frame, 1)
                gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 6)
                for (x,y,w,h) in faces:
                    face_crop = self.frame[y:y+h, x:x+w]
                    try:
                        results = DeepFace.find(img_path=face_crop, db_path=db_path, enforce_detection=False, silent=True)
                        if results and not results[0].empty:
                            df = results[0]
                            matched_path = df.iloc[0]['identity']
                            name = os.path.basename(os.path.dirname(matched_path))
                            color = (0,255,0)
                            self.log_attendance(name)
                        else:
                            name = "Unknown"
                            color = (0,0,255)

                    except Exception:
                        name = "Unknown"
                        color = (0,0,255)
                    cv2.rectangle(self.frame, (x,y), (x+w, y+h), color, 2)
                    cv2.putText(self.frame, name, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image = imgtk)
            self.top.after(10, self.update_frame)
        else:
            if self.cap:
                self.cap.release()
            self.top.destroy()
    
    def close(self):
        self.running = False

    def log_attendance(self, name):
        today = datetime.date.today().strftime("%Y-%m-%d")
        csv_path = os.path.join(records_dir, f"{today}.csv")
        try:
            with open(csv_path, 'r') as f:
                for row in csv.reader(f):
                    if len(row)>1 and row[1] == name:
                        return
        except FileNotFoundError:
            pass
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.datetime.now().strftime("%H:%M:%S"), name])

class MainApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Attendance App")
        self.root.geometry("500x300")
        self.root.resizable(0,0)

        tk.Label(root, text="Face Recognition System", font=("Arial", 24)).pack(pady=20)
        self.start_btn = tk.Button(root, text = "Start Recognition", font=("Arial", 12), command=self.open_recognition_window)
        self.start_btn.pack(pady = 10)
        self.addnew_btn = tk.Button(root, text = "Add new User", font = ("Arial", 12), command = self.open_addnew_window)
        self.addnew_btn.pack(pady = 10)

    def open_recognition_window(self):
        if not os.listdir(db_path):
            messagebox.showwarning("Empty Database", "No registered faces found in the database!")
            return
        RecognitionWindow(self.root)

    def open_addnew_window(self):
        AddNew(self.root)

class AddNew:
    def __init__(self, parent):
        self.running = True
        self.circleradius = 175
        self.window = Toplevel(parent)
        self.window.title("Add New User")
        self.window.geometry("700x600")
        self.window.resizable(False, False)
        self.cap = cv2.VideoCapture(0)
        self.name_var = tk.StringVar()
        self.video_label = tk.Label(self.window)
        self.name_label = tk.Label(self.window, text='ID:', font=("Arial", 10))
        self.name_entry = tk.Entry(self.window, textvariable=self.name_var,font=("Arial", 10))
        self.save_btn = tk.Button(self.window, text = 'Confirm', command = self.imagesave)
        self.video_label.grid(row = 0, column=0)
        self.name_label.grid(row = 1, column=0)
        self.name_entry.grid(row = 2, column=0)
        self.save_btn.grid(row = 3, column=0)
        self.update_frame_addnew()
        self.window.geometry(f"{self.img.shape[1]+10}x600")
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        self.running = False
    
    def imagesave(self):
        imgtosave = self.img[int(self.img.shape[0]/2)-self.circleradius:int(self.img.shape[0]/2)+self.circleradius, int(self.img.shape[1]/2)-self.circleradius:int(self.img.shape[1]/2)+self.circleradius]
        place = os.path.join(current_dir, 'RegisteredFaces', self.name_var.get())
        try:
            os.makedirs(place, exist_ok=False)

            try:
                cv2.imwrite(os.path.join(place, f"{self.name_var.get()}.jpg"), imgtosave)
                self.running = False
                messagebox.showinfo("Success", "User Added Successfully")
            except:
                messagebox.showerror("Error", "Something Went Wrong Try Again")
        except FileExistsError:
            messagebox.showinfo('Duplicate Entry', 'User already Exists')
        
    def update_frame_addnew(self):
        if self.running:
            ret, frame_addnew = self.cap.read()
            if ret:
                frame_addnew = cv2.flip(frame_addnew, 1)
                self.img = frame_addnew.copy()
                cv2.circle(frame_addnew, (int(frame_addnew.shape[1]/2), int(frame_addnew.shape[0]/2)), self.circleradius, (0,255,0), 1, cv2.LINE_AA)
                img = cv2.cvtColor(frame_addnew, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            self.window.after(10, self.update_frame_addnew)
        else:
            if self.window:
                self.cap.release()
            self.window.destroy()        


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()


