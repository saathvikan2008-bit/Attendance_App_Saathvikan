import mysql.connector
import datetime
import csv
import os

conn = mysql.connector.connect(user = 'root', password = '123456', host = 'localhost', database = 'face_recognition_db')
records_path = 'C:/Users/MOHAN/Documents/Saathvikan/Attendance_App_Saathvikan/Records'
cur = conn.cursor()

records = os.listdir(records_path)
print(records)

for filename in records:
    if filename.endswith('.csv'):
        with open(os.path.join(records_path, filename), 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                time_str, user_name = row
                date_str = filename.replace('.csv', '')
                timestamp = f"{date_str} {time_str}"
                sql = 'INSERT INTO attendance (user_id,timestamp) VALUES (%s, %s)'
                cur.execute(sql, (user_name, timestamp))
        conn.commit()

cur.close()
conn.close()