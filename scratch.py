import csv

f = open('students.csv', 'r+')
f.seek(0,2)
o = csv.writer(f)
o.writerow(['hi', 'hello', 'hiw'])
f.close()