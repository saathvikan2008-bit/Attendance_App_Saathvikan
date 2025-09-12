import cv2 as c


face_cascade = c.CascadeClassifier(c.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = c.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        print("Capture Source Failure")
        break

    frame_flipped = c.flip(frame, flipCode=1)
    gray = c.cvtColor(frame_flipped, c.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    for (x,y,w,h) in faces:
        c.rectangle(frame_flipped, (x,y), (x+w, y+h), (0,0,255), 2)
        c.putText(frame_flipped, "Person", (x,y-10), c.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 1)

    c.putText(frame_flipped, "'q' to quit", (frame_flipped.shape[1]-125,25), c.FONT_HERSHEY_COMPLEX, 0.7, (0,0,0), 1)

    c.imshow("Faces Boxes", frame_flipped)
    if c.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
c.destroyAllWindows()
