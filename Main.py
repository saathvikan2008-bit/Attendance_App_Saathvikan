from deepface import DeepFace
import cv2
import os
import datetime
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
import mysql.connector
from mysql.connector import errorcode
import numpy as np
import json

#Database Configuration
DB_CONFIG = {'user' : 'root', 'password' : '123456', 'host' : 'localhost', 'database' : "face_recognition_db"}
def get_db_connection():
    """Establishes and returns the connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Wrong Username or password")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database Doesn't exist")
        else:
            print(e)
        return None
    
def initialize_database():
    """Creates the Databse and Tables if they don't exist"""
    try:
        conn = mysql.connector.connect(user=DB_CONFIG['user'],password=DB_CONFIG['password'],host=DB_CONFIG['host'])
        cur = conn.cursor()

        #Create the databse
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cur.execute(f"USE {DB_CONFIG['database']}")

        #Create the tables
        cur.execute('CREATE TABLE IF NOT EXISTS users(id int auto_increment PRIMARY KEY, user_id VARCHAR(255) NOT NULL UNIQUE, image_blob LONGBLOB, embedding TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        cur.execute('CREATE TABLE IF NOT EXISTS attendance(id INT auto_increment not null PRIMARY KEY, user_id VARCHAR(255) NOT NULL, timestamp DATETIME NOT NULL, UNIQUE KEY daily_attendance(user_id, (DATE(timestamp))))')
        conn.commit()
        cur.close()
        conn.close()
        print("Database loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading database: {e}")
        return False

#Global Variables
current_dir = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_dir,"RegisteredFaces")
records_dir = os.path.join(current_dir,"Records")
logo = 'Bitmaps/logo_new.ico'
face_detection_threshold = 1.2
debug = False

# Remove after adding MYSQL
os.makedirs(db_path, exist_ok=True)
os.makedirs(records_dir, exist_ok=True)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

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

        if debug == True:
            Slider(self.root)
    
    def open_recognition_window(self):
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Database Error", "Could not connect to Database")
            return
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM USERS")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()

        if count == 0:
            messagebox.showwarning("Empty Database", "No registered faces found in the database!")
            return
        RecognitionWindow(self.root)

    def open_addnew_window(self):
        AddNew(self.root)

    def open_viewrecords_window(self):
        ViewRecords(self.root)
    
    def remove_user(self):
        dialog = ctk.CTkInputDialog(text = 'Enter the User to be removed', title='Remove User')
        user_id_to_remove = dialog.get_input()
        if user_id_to_remove:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure, you want permanently delete user {user_id_to_remove}")
            if confirm:
                conn = get_db_connection()
                if not conn:
                    messagebox.showerror("Database Error", "Could not connect to Database")
                    return
                cur = conn.cursor()

                try:
                    cur.execute("SELECT id FROM users WHERE user_id = %s", (user_id_to_remove,))
                    if cur.fetchone():
                        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id_to_remove,))
                        conn.commit()
                        messagebox.showinfo("Success", f" '{user_id_to_remove}' has been permanently removed")
                    else:
                        messagebox.showerror("User not found", f"'{user_id_to_remove}' does not exist")
                except Exception as e:
                    messagebox.showerror("Error", f"Something Went wrong {e}")
                finally:
                    cur.close()
                    conn.close()


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
        self.running = True
        app.disable_addnew_button()
        app.disable_facerec_button()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)
        self.known_face_embeddings = self.load_known_faces()
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
        self.top.protocol('WM_DELETE_WINDOW', self.close)
        self.update_frame()
        self.top.geometry(f'{self.frame.shape[1]+10}x600')
        root.iconify()

    def load_known_faces(self):
        """Loads All existing user_id and embeddings from the database"""
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Could not connect with database")

        known_faces = {}
        cur = conn.cursor()
        cur.execute("SELECT user_id, embedding FROM users")
        records = cur.fetchall()

        for row in records:
            user_id = row[0]
            embedding = np.array(json.loads(row[1]))
            known_faces[user_id] = embedding
        
        cur.close()
        conn.close()

        if not known_faces:
            messagebox.showwarning("Empty Database", "Database has no Users")
        
        return known_faces

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
                        detected_embedding_obj = DeepFace.represent(img_path=face_crop, enforce_detection=False, model_name="VGG-Face")
                        detected_embedding = np.array(detected_embedding_obj[0]['embedding'])

                        name = "Unknown"
                        color = (0,0,255)
                        min_distance = float('inf')

                        #Compare with known embeddings
                        for user_id, known_embedding in self.known_face_embeddings.items():
                            distance = np.linalg.norm(detected_embedding - known_embedding)

                            if distance < min_distance and distance<face_detection_threshold:
                                min_distance = distance
                                name = user_id
                                color = (0,255,0)
                        if name != "Unknown":
                            self.log_attendance(name=name)

                    except Exception as e:
                        name = "Unknown"
                        color = (0,0,255)
                        print(f"Recognition failed : {e}")
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
            app.enable_facerec_button()
            root.deiconify()
            self.top.destroy()
    
    def close(self):
        root.deiconify()
        self.running = False

    def log_attendance(self, name):
        conn = get_db_connection()
        if not conn:
            return

        now = datetime.datetime.now()

        cur = conn.cursor()
        data = (name, now)
        sql = "INSERT INTO attendance (user_id, timestamp) VALUES (%s, %s)"

        try:
            cur.execute(sql, data)
            conn.commit()
        except mysql.connector.IntegrityError:
            #Dupicate Entry
            pass
        except Exception as e:
            print(f"Error logging attendance: {e}")
        finally:
            cur.close()
            conn.close()

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
        app.disable_addnew_button()
        self.update_frame_addnew()
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def enterkeypressed(self, event):
        self.imagesave()
    def close(self):
        self.running = False
    
    def imagesave(self):
        user_id = self.name_var.get()
        if not user_id:
            messagebox.showerror("Error", "User ID cannot be empty")
            return
        imgtosave = self.img[int(self.img.shape[0]/2)-self.circleradius:int(self.img.shape[0]/2)+self.circleradius, int(self.img.shape[1]/2)-self.circleradius:int(self.img.shape[1]/2)+self.circleradius]
        
        try:
            embedding_obj = DeepFace.represent(img_path=imgtosave, model_name="VGG-Face", enforce_detection=False)
            embedding = embedding_obj[0]['embedding']
        except Exception as e:
            messagebox.showerror('Error', f"Could not generate embedding: {e}")
            return
        
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Database Error", "Could not connect to Databse")
            return
        
        cur = conn.cursor()

        _,Buffer = cv2.imencode('.jpg', imgtosave)
        image_blob = Buffer.tobytes()
        embedding_str = json.dumps(embedding)

        sql = "INSERT INTO users (user_id, image_blob, embedding) VALUES (%s,%s,%s)"
        data = (user_id, image_blob, embedding_str)

        try:
            cur.execute(sql, data)
            conn.commit()
            messagebox.showinfo("Success", f"User '{user_id}' Successfully added")
            self.running = False
        except mysql.connector.IntegrityError:
            messagebox.showerror("Duplicate Entry", f"User '{user_id}' already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Database Insertion Failed: {e}")
        finally:
            cur.close()
            conn.close()
        
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
            app.enable_addnew_button()
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
        self.user_list = self.get_all_users()
        control_frame = ctk.CTkFrame(self.window)
        control_frame.pack(padx = 10, pady = 10)

        self.date_label = ctk.CTkLabel(control_frame, text='Select Date:', font=("Arial", 14))
        self.date_label.pack(side = 'left')
        self.date_entry = ctk.CTkEntry(control_frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.insert(0,datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack(side = 'left', padx = 5)
        self.load_btn = ctk.CTkButton(control_frame, text = 'Load Records', command=self.load_records_for_date)
        self.load_btn.pack(side = 'left', padx = 5)

        self.window.bind("<Return>", self.enterpressed)        

        self.record_display = ctk.CTkTextbox(self.window, font=("Courier", 14), wrap = 'none', state = 'disabled')
        self.record_display.pack(padx = 10, pady = (0,10), fill = 'both', expand = True)
        self.record_display.tag_config("Present", foreground = "#40D51A")
        self.record_display.tag_config("Absent", foreground = "#CD3232")

        self.load_records_for_date() #Load today's records

    def enterpressed(self, event):
        self.load_records_for_date()
    def get_all_users(self):
        conn = get_db_connection()
        if not conn : return []
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users ORDER BY user_id asc")
        users = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return users
    
    def load_records_for_date(self):
        selected_date_str = self.date_entry.get()
        try:
            selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except:
            messagebox.showerror("Invalid Date", "Please Enter the date in YYYY-MM-DD format")
            return
        self.record_display.configure(state = 'normal')
        self.record_display.delete('1.0', 'end')

        conn = get_db_connection()
        if not conn:
            self.record_display.insert('end', 'Could not connect to database')
            self.record_display.configure(state = 'disabled')
            return
        
        cur = conn.cursor()

        sql = 'SELECT user_id, TIME(timestamp) FROM attendance WHERE DATE(timestamp) = %s ORDER BY timestamp ASC'
        cur.execute(sql, (selected_date,))
        present_records = cur.fetchall()
        
        present_users = [rec[0] for rec in present_records]

        # Display the present users
        header = f'Present on {selected_date_str}:\n{"Time":<25}{"Name"}\n'
        seperator = '='*45 + '\n'
        self.record_display.insert('end', header)
        self.record_display.insert('end', seperator)
        
        for time, name in present_records:
            formatted_row = f'{str(time):<25}{name}\n'
            self.record_display.insert('end', formatted_row, tags='Present')

        #Display Absent users
        absentees = [user for user in self.user_list if user not in present_users]
        self.record_display.insert('end', '\n'+'*'*50+'\n\n')
        self.record_display.insert('end', "Absentees:\n")
        for absentee in absentees:
            self.record_display.insert('end', absentee+'\n', tags='Absent')

        cur.close()
        conn.close()
        self.record_display.configure(state = 'disabled')

    def close(self):
        root.deiconify()
        self.window.destroy()

class Slider:
    def __init__(self, parent):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Thrshold Dbug")
        self.window.geometry("500x400")
        self.slider = ctk.CTkSlider(self.window, from_ = 0, to = 5,width=300, number_of_steps=200, command=self.update_threshold)
        self.slider.set(face_detection_threshold)
        self.slider.pack(pady = 20, padx = 20)
        self.thr_label = ctk.CTkLabel(self.window, text = str(face_detection_threshold))
        self.thr_label.pack(pady = 20)
    def update_threshold(self, value):
        global face_detection_threshold
        face_detection_threshold = value
        self.thr_label.configure(text = str(face_detection_threshold))

if __name__ == "__main__":
    if not initialize_database():
        print("Failed to initialise database, Exitong...")
        exit(1)
    root = ctk.CTk()
    app = MainApp(root)
    root.mainloop()