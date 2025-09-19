import datetime
import csv
#print(datetime.date.today())

det = (datetime.datetime.now())
time = (det.strftime("%H:%M:%S"))

def update_record(ID, Time):
    global time
    now_date = datetime.date.today()
    now_date_string = now_date.strftime("%Y-%m-%d")
    location = 'C:/Users/MOHAN/Documents/Saathvikan/Attendance_App_Saathvikan/Records'
    with open(location + "/" + now_date_string + ".csv", "a") as current_record:
        a = csv.writer(current_record)
        a.writerow([time, "Saathvikan"])

update_record(1,2)