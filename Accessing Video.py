
import cv2

vid = cv2.VideoCapture(0) #Will capture the video

if not vid.isOpened():
    print("Cannot open Camera")
    exit()


vid.set(3,200)  #setting frame size to 200*200
vid.set(4,200)


while True:
    ret,frame= vid.read() #“vid.read() “will read the captured frame
    if not ret: 
        print("Frame not captured")
        break

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #to change color to gray

    cv2.imshow('frame',frame) #“cv.imshow()”, we are displaying the captured frame

    if cv2.waitKey(1) & 0xFF == ord('q'): #To exit the loop we are using keyboard “Q” key
        break

vid.release() #we release all the resources.
cv2.destroyAllWindows()



