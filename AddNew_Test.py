import cv2
import os

cap = cv2.VideoCapture(0)
current_dir = os.path.dirname(os.path.realpath(__file__))

def Addnew():
    ID = input("Enter name: ")
    place = (f"{current_dir}/RegisteredFaces/{ID}")
    os.mkdir(place)
    while True:
        success, frame = cap.read()
        if not success:
            print("Webcam failure")
        frame_flipped = cv2.flip(frame, 1)
        cv2.imshow("Window", frame_flipped)

        if cv2.waitKey(1) & 0xFF == ord('e'):
            cv2.imwrite(f"{place}/test.jpg", frame_flipped)
            break

Addnew()

#os.remove("test.jpg")
cap.release()
cv2.destroyAllWindows()
