import threading
import time

def task1(name):
    time.sleep(4)
    print(f"Finished {name}")

def task2():
    time.sleep(2)
    print("task2 completed")
def task3():
    time.sleep(1)
    print("task3 completed")

thread1 = threading.Thread(target=task1, args=("Saathvikan",))
thread2 = threading.Thread(target=task2)
thread3 = threading.Thread(target=task3)

thread1.start()
thread2.start()
thread3.start()

thread1.join()
thread2.join()
thread3.join()
print("All tasks completed")