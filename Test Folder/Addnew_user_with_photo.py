import mysql.connector
import json
import os
from deepface import DeepFace
import cv2

conn = mysql.connector.connect(user = 'root', password = '123456', host = 'localhost', database = 'face_recognition_db')
db_path = 'C:/Users/MOHAN/Documents/Saathvikan/Attendance_App_Saathvikan/RegisteredFaces'

users = os.listdir(db_path)
cur = conn.cursor()

user = input("Enter user id")



user_img = input("Enter the image path")
user_img = cv2.imread(user_img)

embedding_obj = DeepFace.represent(img_path=user_img, enforce_detection=False)
embedding = embedding_obj[0]['embedding']

_,buffer = cv2.imencode('.jpg', user_img)
image_blob = buffer.tobytes()

embedding_str = json.dumps(embedding)

cur.execute("INSERT INTO users (user_id, image_blob, embedding) VALUES (%s, %s, %s)", (user, image_blob, embedding_str))
conn.commit()

cur.close()
conn.close()
