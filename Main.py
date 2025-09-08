from deepface import DeepFace
import cv2
import os
import csv
import datetime

cwd = os.getcwd() # Gets the current working directory


#Function to check if all required Directories are present and if not present, create them
def initcheck():
    dir_list = os.listdir(cwd)
    print(dir_list)
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
                return "Duplicate"
            else:
                continue
        object_writer.writerow([Time,ID])
        return "Record Added successfully"
    
#Function to delete the temporary Image
def tempimgdel(path):
    if os.path.exists(path):
        os.remove(path)
        print("Temp image successfully deleted, Quitting")
    elif os.path.exists(path) == False:
        print("Temp file does not Exist, Quitting")

initcheck() 

cap = cv2.VideoCapture(0)

#Main Loop
while True:

    success, frame = cap.read() #Read the webcam
    if not success:
        print("Webcam Not responding")
        break
    
    frame_flipped = cv2.flip(frame, 1) #Flips the frame along the vertical axis

    # Save current frame temporarily
    temp_img_path = "temp.jpg"
    cv2.imwrite(temp_img_path, frame_flipped)

    # Perform face recognition
    result = DeepFace.find(img_path=temp_img_path, db_path=cwd+"/RegisteredFaces", enforce_detection=False)
    
    # Print the closest match's name if found
    if len(result)>0:
        df = result[0] #Takes the closest match

        # If a face is matched
        if not df.empty:

            # Face Recognition
            matched_path = df.iloc[0]["identity"]
            folder_path = os.path.dirname(matched_path)
            person_ID = os.path.basename(folder_path)
            print("Recognised Person:", person_ID)
            formatted_time = (datetime.datetime.now()).strftime("%H:%M:%S")
            
            #Updates the CSV file
            updation_Success = update_record(person_ID, formatted_time)
            cv2.putText(frame_flipped, updation_Success, (0, frame_flipped.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            print(updation_Success)

            #Drawing a box and displaying the name of the person
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
            gray = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            for (x,y,w,h) in faces:
                #Draw the rectangle
                cv2.rectangle(frame_flipped, (x,y), (x+w, y+h), (0,0,255), 2)

                #Display the name
                cv2.putText(frame_flipped, person_ID, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
                break

        else:
            print("Standby")
            cv2.putText(frame_flipped, "Waiting for a Face", (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0,0), 2)
    
    # displays q to quit
    cv2.putText(frame_flipped, "'q' to quit", (frame_flipped.shape[1]-125,25), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,0,0), 1)

    # Show webcam frame
    cv2.imshow("Monitor", frame_flipped)
    
    #Quit if "q" key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        tempimgdel(temp_img_path)
        break
    
#Close the Webcam and destroy all windows
cap.release()
cv2.destroyAllWindows()
