from deepface import DeepFace
import cv2
import os
import csv
import datetime
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
import shutil

current_dir = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_dir,"RegisteredFaces")
records_dir = os.path.join(current_dir,"Records")

os.makedirs(db_path, exist_ok=True)
os.makedirs(records_dir, exist_ok=True)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

logo = 'Bitmaps/logo_new.ico'
class MainApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Attendance App")
        self.root.geometry("800x600")
        self.root.resizable(False,False)
        try:
            self.root.iconbitmap(logo)
        except Exception:
            print("Logo Not found")

        header_frame = ctk.CTkFrame(root, fg_color="transparent")
        header_frame.grid(row = 0, column = 1, pady=(40,40), sticky = 's')
        header_frame.grid_columnconfigure(0, weight = 0)
        header_frame.grid_columnconfigure(1, weight = 0)

        try:
            logo_image = ctk.CTkImage(Image.open('Bitmaps/logobg_removed.png'), size=(52,52))
            self.logo_label = ctk.CTkLabel(header_frame, text='', image=logo_image)
            self.logo_label.grid(row = 0, column = 0, padx=(0,10))
        except Exception:
            self.logo_label = ctk.CTkLabel(root, text='')
        
        self.Title = ctk.CTkLabel(header_frame, text="Face Recognition System", font=("Calibri", 60, 'bold'))
        self.Title.grid(row = 0, column = 1)

        self.start_btn = ctk.CTkButton(root, text = "Start Recognition", font=("Arial", 18), height=50, width=250, command=self.open_recognition_window)
        self.addnew_btn = ctk.CTkButton(root, text = "Add new User", font = ("Arial", 18), height=50, width=250, command = self.open_addnew_window)
        self.viewrecords_btn = ctk.CTkButton(root, text='View Records', font=("Arial", 18), height=50, width=250, command=self.open_viewrecords_window)
        self.remove_user_btn = ctk.CTkButton(root, text = 'Remove User', font = ("Arial", 18), height=50, width=250, command=self.remove_user)
        self.exit_btn = ctk.CTkButton(root, text='Exit', font = ("Arial", 18), height=50, width=250, command=root.destroy)
        
        self.root.grid_columnconfigure(0,weight = 1)
        self.root.grid_columnconfigure(2,weight = 1)
        self.root.grid_rowconfigure(1, weight = 1)
        self.root.grid_rowconfigure(7, weight = 1)

        self.start_btn.grid(row = 2, column = 1, pady = 10)
        self.addnew_btn.grid(row = 3, column = 1, pady = 10)
        self.viewrecords_btn.grid(row = 4, column = 1, pady = 10)
        self.remove_user_btn.grid(row = 5, column = 1, pady = 10)
        self.exit_btn.grid(row = 6, column = 1, pady = (40,10))

    def open_recognition_window(self):
        if not os.listdir(db_path):
            messagebox.showwarning("Empty Database", "No registered faces found in the database!")
            return
        RecognitionWindow(self.root)

    def open_addnew_window(self):
        AddNew(self.root)

    def open_viewrecords_window(self):
        ViewRecords(self.root)
    
    def remove_user(self):
        self.dialog = ctk.CTkInputDialog(text = 'Enter the User to be removed', title='Remove User')
        self.user_id_to_remove = self.dialog.get_input()
        if self.user_id_to_remove:
            self.user_path = os.path.join(db_path, self.user_id_to_remove)

            if os.path.isdir(self.user_path):
                self.confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently remove user '{self.user_id_to_remove}'?")
                if self.confirm:
                    try:
                        shutil.rmtree(self.user_path)
                        messagebox.showinfo("Success", f"User '{self.user_id_to_remove}' has been removed.")
                    except Exception:
                        messagebox.showerror("Error", "Something went wrong, try again")
            else:
                messagebox.showerror("User Not Found", f"'User {self.user_id_to_remove}' doesn't exist.")

    def enable_addnew_button(self):
        self.addnew_btn.configure(state = 'normal')   

    def disable_addnew_button(self):
        self.addnew_btn.configure(state = 'disabled')

    def enable_facerec_button(self):
        self.start_btn.configure(state = 'normal')

    def disable_facerec_button(self):
        self.start_btn.configure(state = 'disabled')

class RecognitionWindow:
    def __init__(self, parent):
        self.top = ctk.CTkToplevel(parent)
        self.top.after(250, lambda:self.top.iconbitmap(logo))
        self.top.title("Face Recognition")
        self.top.geometry('800x600')
        self.video_label = ctk.CTkLabel(self.top, text='')
        self.video_label.pack(padx = 10, pady = 10)
        self.status_label = ctk.CTkLabel(self.top, text='Status:Online', font = ("Arial", 16))
        self.status_label.pack()
        self.close_button = ctk.CTkButton(self.top, text='Close', command=self.close)
        self.close_button.pack(pady = 10)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.top.protocol('WM_DELETE_WINDOW', self.close)
        root.iconify()
        app.disable_addnew_button()
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
                
                img = cv2.cvtColor(cv2.resize(self.frame, (1000,750)), cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image = imgtk)
            self.top.after(5, self.update_frame)
        else:
            if self.cap:
                self.cap.release()
            app.enable_addnew_button()
            root.deiconify()
            self.top.destroy()
    
    def close(self):
        root.deiconify()
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

class AddNew:
    def __init__(self, parent):
        self.running = True
        self.circleradius = 175
        self.window = ctk.CTkToplevel(parent)
        self.window.after(250, lambda:self.window.iconbitmap(logo))
        self.window.title("Add New User")
        self.window.geometry("900x600")
        self.window.resizable(True, True)
        self.cap = cv2.VideoCapture(0)
        self.name_var = ctk.StringVar()
        self.video_label = ctk.CTkLabel(self.window, text='', pady = 50, padx = 50)
        self.name_label = ctk.CTkLabel(self.window, text='ID:', font=("Arial", 14))
        self.name_entry = ctk.CTkEntry(self.window, textvariable=self.name_var, font=("Arial", 10))
        self.save_btn = ctk.CTkButton(self.window, text = 'Confirm', command = self.imagesave)
        self.name_entry.bind("<Return>", self.enterkeypressed)
        
        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_rowconfigure(3, weight=0)
        self.window.grid_rowconfigure(4, weight=0)
        self.window.grid_rowconfigure(5, weight=1)
        self.window.grid_rowconfigure(6, weight=1)
        self.window.grid_rowconfigure(7, weight=1)    
        self.video_label.grid(row = 0, column = 0, padx = 10, pady = 10, rowspan = 7)
        self.name_label.grid(row = 3, column = 1, sticky = 'w', padx = (10,5), pady = (10,5))
        self.name_entry.grid(row = 3, column = 2, sticky = 'w', padx = (5,10), pady = (10,5))
        self.save_btn.grid(row = 4, column = 1, sticky='ew', padx = 10, pady= (5,10), columnspan = 2)
        root.iconify()
        app.disable_facerec_button()
        self.update_frame_addnew()
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def enterkeypressed(self, event):
        self.imagesave()
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
                img = cv2.cvtColor(cv2.resize(frame_addnew, (1000,750)), cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            self.window.after(10, self.update_frame_addnew)
        else:
            if self.window:
                self.cap.release()
            app.enable_facerec_button()
            root.deiconify()
            self.window.destroy()        

class ViewRecords:
    def __init__(self, parent):
        self.window = ctk.CTkToplevel(parent)
        try:
            self.window.after(250, lambda:self.window.iconbitmap(logo))
        except Exception as e:
            print(f"Couldn't show logo: {e}")
        self.window.title("Records")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.geometry('800x600')
        root.iconify()
        self.user_list = [i for i in os.listdir(db_path) if not i.endswith('.pkl')]
        control_frame = ctk.CTkFrame(self.window)
        control_frame.pack(padx = 10, pady = 10)

        self.records_list = self.get_records()
        self.selected_file = ctk.StringVar()

        self.file_menu = ctk.CTkOptionMenu(control_frame, variable=self.selected_file, values=self.records_list if self.records_list else "No Records found", command=self.on_file_select)
        self.file_menu.pack(side = 'left', padx = (0,10))

        self.record_display = ctk.CTkTextbox(self.window, font=("Courier", 14), wrap = 'none', state = 'disabled')
        self.record_display.pack(padx = 10, pady = (0,10), fill = 'both', expand = True)
        self.record_display.tag_config("Present", foreground = "#40D51A")
        self.record_display.tag_config("Absent", foreground = "#CD3232")

        today_file_name = f"{datetime.date.today().strftime('%Y-%m-%d')}.csv"
        if today_file_name in self.records_list:
            self.selected_file.set(today_file_name)
            self.load_csv_data(os.path.join(records_dir, today_file_name))
        else:
            self.record_display.insert("end", "No records found for today")


    def get_records(self):
        try:
            return sorted([f for f in os.listdir(records_dir) if f.endswith('.csv')], reverse=True)       
        except Exception:
            return []

    def on_file_select(self, choice):
        file_path = os.path.join(records_dir, choice)
        self.load_csv_data(file_path)
        
    def load_csv_data(self, file_path):
        self.record_display.configure(state = 'normal')
        self.record_display.delete("1.0", 'end')
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                header = f'Present:\n{"Time":<25}{"Name"}\n'
                seperator = '='*45 + '\n'
                self.record_display.insert('end', header)
                self.record_display.insert('end', seperator)

                present = []

                for row in reader:
                    if len(row)>=2:
                        formatted_row = f'{row[0]:<25}{row[1]}\n'
                        start_index = self.record_display.index('end-1c')
                        self.record_display.insert("end", formatted_row)
                        end_index = self.record_display.index('end-1c')
                        self.record_display.tag_add("Present", start_index, end_index)
                        present.append(row[1])

                self.record_display.insert('end', '\n'+'*'*50+'\n'*2)
                self.record_display.insert('end', "Absentees:\n")
                absentees = [f for f in self.user_list if f not in present]
                for absentee in absentees:
                    start_index = self.record_display.index('end-1c')
                    self.record_display.insert("end", absentee+'\n')
                    end_index = self.record_display.index('end-1c')
                    self.record_display.tag_add("Absent", start_index, end_index)
        except Exception as e:
            messagebox.showerror("Error!", e)
        self.record_display.configure(state = 'disabled')

    def close(self):
        root.deiconify()
        self.window.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = MainApp(root)
    root.mainloop()