from deepface import DeepFace
import cv2
import os
import csv
import datetime
import threading
import time


cwd = os.getcwd() # Gets the current working directory

#Global Variables
frame_flipped = None
frame_lock = threading.Lock()
stop = False
data_lock = threading.Lock()
recognised_faces = list()

#Function to check if all required Directories are present and if not present, create them
def initcheck():
    dir_list = os.listdir(cwd)
    #print(dir_list)
    if "Records" not in dir_list:
        print("Records folder not Present, creating records folder")
        os.mkdir(cwd+"/Records")
    if "RegisteredFaces" not in dir_list:
        print("RegisteredFaces folder not present, creating directory")
        os.mkdir(cwd+'/RegisteredFaces')

# Function to Store the attendance information in a csv file 'For Testing Purposes only'
def update_record(ID, Time):
    now_date = datetime.date.today()
    now_date_string = now_date.strftime("%Y-%m-%d")
    CSVfile_location = cwd + '/Records'
    with open(CSVfile_location + "/" + now_date_string + ".csv", "a+", newline="") as current_record:
        object_writer = csv.writer(current_record)

        current_record.seek(0)
        object_reader = csv.reader(current_record)
        for rows in object_reader:
            if rows[1] == ID:
                print("Duplicate record")
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

#A function that uses haarcascades to crop the image and deepface performs face recognition on that cropped image
def Face_recognition_thread():

    global frame_flipped, stop
    while not stop:
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

        for (x,y,w,h) in faces:
            face_cropped = frame_copy[y:y+h, x:x+w]

            temp_img_path = cwd+"/temp.jpg"
            cv2.imwrite(temp_img_path, face_cropped)
            try:
                result = DeepFace.find(img_path=temp_img_path, db_path=db_path, enforce_detection=False)
            except Exception as e:
                print("Detection failed: ", e)
                continue

            if len(result)>0:
                df = result[0]
                
            if not df.empty:

                #Face Recognition
                matched_path = df.iloc[0]["identity"]
                folder_path = os.path.dirname(matched_path)
                person_ID = os.path.basename(folder_path)
                print("Recognised person: ",  person_ID)
                formatted_time = (datetime.datetime.now()).strftime("%H:%M:%S")

                #Shares Data about the recognised person to main thread
                data_lock.acquire()
                recognised_faces.clear()
                for (x,y,w,h) in faces:
                    recognised_faces.append((x,y,w,h,person_ID, formatted_time))
                data_lock.release()
            else:
                data_lock.acquire()
                recognised_faces.clear()
                data_lock.release()
        time.sleep(0.01)


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml") #Loads the Haarcascademodel
db_path = cwd+"/RegisteredFaces"
initcheck() 

#Initialize Webcam
cap = cv2.VideoCapture(0)

#Start the threading
facerec_thread = threading.Thread(target=Face_recognition_thread)
facerec_thread.daemon = True #So thread exits when main program quits
facerec_thread.start()

#Main Loop
while True:

    success, frame = cap.read() #Read the webcam
    if not success: #If webcam doesn't work print appropriate messages
        print("Webcam Not responding")
        break
    
    frame_final = cv2.flip(frame, 1) #Flips the frame along the vertical axis

    # Save current frame temporarily
    temp_img_path = "temp.jpg"
    cv2.imwrite(temp_img_path, frame_final)

    #To share the frame with the facerec_thread safely without any obstructions
    frame_lock.acquire()
    frame_flipped = frame_final.copy()
    frame_lock.release()

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
        updation_Success = update_record(text, formatted_time)
        cv2.putText(frame_flipped, updation_Success, (0, frame_flipped.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        print(updation_Success)
    data_lock.release()
    
    # displays q to quit
    cv2.putText(frame_final, "'q' to quit", (frame_final.shape[1]-125,25), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,0,0), 1)

    # Show webcam frame
    cv2.imshow("Display", frame_final)
    
    #Quit if "q" key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#Close the Webcam and destroy all windows
stop = True
tempimgdel(temp_img_path)
facerec_thread.join()
cap.release()
cv2.destroyAllWindows()
