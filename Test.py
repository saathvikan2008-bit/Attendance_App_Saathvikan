import tkinter as tk
from tkinter import Toplevel, messagebox
from PIL import Image, ImageTk
import cv2
import os, csv, datetime
from deepface import DeepFace

current_dir = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_dir, "RegisteredFaces")
records_dir = os.path.join(current_dir, "Records")

os.makedirs(db_path, exist_ok=True)
os.makedirs(records_dir, exist_ok=True)

class RecognitionWindow:
    def __init__(self, parent):
        self.top = Toplevel(parent)
        self.top.title("Face Recognition")
        self.top.geometry("800x600")
        self.video_label = tk.Label(self.top)
        self.video_label.pack(padx=10, pady=10)
        self.status_label = tk.Label(self.top, text="Running...", font=("Arial", 12))
        self.status_label.pack()
        self.close_btn = tk.Button(self.top, text="Close", command=self.close)
        self.close_btn.pack(pady=10)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.top.protocol("WM_DELETE_WINDOW", self.close)
        self.update_frame()

    def update_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 6)
                for (x, y, w, h) in faces:
                    face_crop = frame[y:y+h, x:x+w]
                    try:
                        results = DeepFace.find(img_path=face_crop, db_path=db_path, enforce_detection=False, silent=True)
                        if results and not results[0].empty:
                            df = results[0]
                            matched_path = df.iloc[0]["identity"]
                            name = os.path.basename(os.path.dirname(matched_path))
                            color = (0, 255, 0)
                            self.log_attendance(name)
                        else:
                            name = "Unknown"
                            color = (0, 0, 255)
                    except Exception:
                        name = "Unknown"
                        color = (0, 0, 255)

                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
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
            with open(csv_path, "r") as f:
                for row in csv.reader(f):
                    if len(row) > 1 and row[1] == name:
                        return
        except FileNotFoundError:
            pass
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.datetime.now().strftime("%H:%M:%S"), name])

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Control Panel")
        self.root.geometry("300x200")

        tk.Label(root, text="Face Recognition System", font=("Arial", 14)).pack(pady=20)
        self.start_btn = tk.Button(root, text="Start Recognition", font=("Arial", 12), command=self.open_recognition_window)
        self.start_btn.pack(pady=10)
        self.status_label = tk.Label(root, text="", font=("Arial", 10))
        self.status_label.pack(pady=10)

    def open_recognition_window(self):
        if not os.listdir(db_path):
            messagebox.showwarning("Empty Database", "No registered faces found in the database!")
            return
        RecognitionWindow(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
