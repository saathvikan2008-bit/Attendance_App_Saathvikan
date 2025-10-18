from deepface import DeepFace
import cv2
import os
import csv
import datetime
import threading
import time

current_dir = os.path.dirname(os.path.realpath(__file__))

#Global Variables
frame_flipped = None
frame_lock = threading.Lock()
stop = False
data_lock = threading.Lock()
recognised_faces = list()
pause_recognition = False
capture_image = False
addNew_running = False
addNew_circle_radius = 175
addNew_circle_center = None

#Function to check if all required Directories are present and if not present, create them
def initcheck():
    dir_list = os.listdir(current_dir)
    #print(dir_list)
    if "Records" not in dir_list:
        print("Records folder not Present, creating records folder")
        os.mkdir(os.path.join(current_dir, 'Records'))
    if "RegisteredFaces" not in dir_list:
        print("RegisteredFaces folder not present, creating RegisteredFaces folder")
        os.mkdir(os.path.join(current_dir, 'RegisteredFaces'))

# Function to Store the attendance information in a csv file 'For Testing Purposes only'
def update_record(ID, Time):
    now_date = datetime.date.today()
    now_date_string = now_date.strftime("%Y-%m-%d")
    CSVfile_location = os.path.join(current_dir, 'Records')
    with open(os.path.join(CSVfile_location, now_date_string) + '.csv', "a+", newline="") as current_record:
        object_writer = csv.writer(current_record)

        current_record.seek(0)
        object_reader = csv.reader(current_record)
        for rows in object_reader:
            if rows[1] == ID:                
                cv2.putText(frame_final, "Duplicate", (0,frame_final.shape[0]-10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0), 1)
                return "Duplicate"
            else:
                continue
        object_writer.writerow([Time,ID])
        cv2.putText(frame_final, "Attendance Recorded", (0,frame_final.shape[0]-10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0), 1)
        return "Record Added successfully"
    
#Function to delete the temporary Image
def tempimgdel(path):
    if os.path.exists(path):
        os.remove(path)
        print("Temp image successfully deleted, Quitting")
    elif os.path.exists(path) == False:
        print("Temp file does not Exist, Quitting")

#A function to check if the input directory is valid
def createDir(loc):
    try:
        os.mkdir(loc)
    except FileExistsError:
        print("User already exists, updating the user")

#Function to Check if the database is empty or not
def IsDatabaseEmpty():
    if len(os.listdir(db_path)) <= 1:
        return True
    else:
        return False

# A function to add new users
def addNew():

    global frame_flipped, pause_recognition, capture_image, addNew_running, addNew_circle_radius,  addNew_circle_center

    addNew_running = True
    pause_recognition = True
    capture_image = False
    addNew_circle_center = (int(frame_final.shape[1]/2),int(frame_final.shape[0]/2)+30)
    ID = input("Enter ID: ")
    place = os.path.join(current_dir, 'RegisteredFaces', ID)
    
    # Gets Coords for the image cropping
    frame_lock.acquire()
    frame_local = frame_flipped
    centre = addNew_circle_center
    frame_lock.release()
    while True:
        frame_lock.acquire()
        if frame_flipped is None:
            frame_lock.release()
            time.sleep(0.05)
            continue
        
        frame_local = frame_flipped
        frame_lock.release()
        if capture_image == True:

            #Crops the image
            imgtosave = frame_local[centre[1]-addNew_circle_radius:centre[1]+addNew_circle_radius, centre[0]-addNew_circle_radius:centre[0]+addNew_circle_radius]
            
            #Saves the cropped image
            createDir(place)
            cv2.imwrite(os.path.join(place, f"{ID}.jpg"), imgtosave)
            print("Image saved successfully")
            capture_image = False
            break

    pause_recognition = False
    addNew_running = False

#A function that uses haarcascades to crop the image and deepface performs face recognition on that cropped image
def Face_recognition_thread():

    global frame_flipped, stop, pause_recognition
    while not stop:
        if pause_recognition:
            time.sleep(0.1)
            recognised_faces.clear()
            continue
        frame_lock.acquire()
        if frame_flipped is None:
            frame_lock.release()
            time.sleep(0.05)
            continue

        # Have the current frame as a copy, so the main thread can use it
        frame_copy = frame_flipped
        frame_lock.release()

        gray = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        data_lock.acquire()
        recognised_faces.clear()

        for (x,y,w,h) in faces:
            face_cropped = frame_copy[y:y+h, x:x+w]

            temp_img_path = os.path.join(current_dir, 'temp.jpg')
            cv2.imwrite(temp_img_path, face_cropped)
            try:
                result = DeepFace.find(img_path=temp_img_path, db_path=db_path, enforce_detection=False)
            except Exception as e:
                print("Detection failed: ", e)
                continue

            if len(result)>0 and not result[0].empty:
                df = result[0]

                #Face Recognition
                matched_path = df.iloc[0]["identity"]
                folder_path = os.path.dirname(matched_path)
                person_ID = os.path.basename(folder_path)
                print("Recognised person: ",  person_ID)
                formatted_time = (datetime.datetime.now()).strftime("%H:%M:%S")
                recognised_faces.append((x,y,w,h,person_ID, formatted_time))
            else:
                recognised_faces.append((x,y,w,h,None,None))

        data_lock.release()

        time.sleep(0.01)

#Loads the Haarcascademodel
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml") #Loads the Haarcascademodel

db_path = os.path.join(current_dir, 'RegisteredFaces')#Photo Database path
initcheck() 

#Initialize Webcam
cap = cv2.VideoCapture(0)

#Start the threading
facerec_thread = threading.Thread(target=Face_recognition_thread)
facerec_thread.daemon = True #So thread exits when main program quits
facerec_thread.start()

#Main Thread
while True:

    success, frame = cap.read() #Read the webcam
    if not success: #If webcam doesn't work print appropriate messages
        print("Webcam Not responding")
        break
    
    frame_final = cv2.flip(frame, 1) #Flips the frame along the vertical axis

    # Save current frame temporarily
    temp_img_path = os.path.join(current_dir, "temp.jpg")
    cv2.imwrite(temp_img_path, frame_final)

    #To share the frame with the facerec_thread safely without any obstructions
    frame_lock.acquire()
    frame_flipped = frame_final.copy()
    frame_lock.release()

    if not addNew_running:
        #Gets data about the recognised person from the facerec_thread
        data_lock.acquire()
        for (x,y,w,h, personID, formatted_time) in recognised_faces:
            cv2.rectangle(frame_final, (x,y), (x+w, y+h), (0,0,255), 2)
            if personID is not None:
                text = personID
                cv2.putText(frame_final, text, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
            else:
                text = "Unknown"
                cv2.putText(frame_final, text, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

            #Updates CSV file
            if text != 'Unknown':
                updation_Success = update_record(text, formatted_time)
                cv2.putText(frame_flipped, updation_Success, (0, frame_flipped.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
                if updation_Success == 'Record Added successfully':
                    print(updation_Success)
        data_lock.release()
    elif addNew_running:
        cv2.circle(frame_final, addNew_circle_center ,addNew_circle_radius, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(frame_final, "Enter your name and Press 'Space' to save", (0, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 1)

    # displays q to quit and n to add new person
    cv2.putText(frame_final, "'q' to quit", (frame_final.shape[1]-125,50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,0,0), 1)
    topText = "'n' to add new user" if not addNew_running else None
    cv2.putText(frame_final, topText, (frame_final.shape[1]-240,25), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,0,0), 1)
    
    if IsDatabaseEmpty():
        cv2.putText(frame_final, '**Database is Empty**', (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    # Show webcam frame
    cv2.imshow("Display", frame_final)
    
    #Quit if "q" key is pressed
    choice = cv2.waitKey(1)
    if choice & 0xFF == ord('q'):
        break
    elif choice & 0xFF == ord("n"):
        addNew_thread = threading.Thread(target=addNew)
        addNew_thread.daemon = True
        addNew_thread.start()
    elif (choice & 0xFF == 32):
        if 'addNew_thread' in globals() and addNew_thread.is_alive():
            capture_image = True

#Close the Webcam and destroy all windows
stop = True
tempimgdel(temp_img_path)
facerec_thread.join()
cap.release()
cv2.destroyAllWindows()