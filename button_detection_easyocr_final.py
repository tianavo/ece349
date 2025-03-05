import cv2
#import ssl
import easyocr

#ssl._create_default_https_context = ssl._create_unverified_context

# initialize easyocr reader
reader = easyocr.Reader(['en'])

# start on webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# target button to recognize
target_button = "5"

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    # use easyocr to detect text
    results = reader.readtext(frame)

    # loop over each detected text element
    for (bbox, text, confidence) in results:
        # check if detected text matches target
        if target_button in text:
            # draw rectangle around text
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

            # print detected text and confidence
            print(f"Button {target_button} found with confidence {confidence}")

            # crosshair position STATIC: (60 pixels to the right and 10 pixels down)
            crosshair_x = bottom_right[0] + 55  # 60 pixels to the right of the right edge
            crosshair_y = (top_left[1] + bottom_right[1]) // 2 + 10  # middle of the rectangle vertically + 10 pixels down

            # makes sure the crosshair is within the frame boundaries
            if 0 <= crosshair_x < frame.shape[1] and 0 <= crosshair_y < frame.shape[0]:
                # draw crosshair
                crosshair_size = 20  # size of crosshair
                cv2.drawMarker(frame, (crosshair_x, crosshair_y), (0, 255, 0), cv2.MARKER_CROSS, crosshair_size, 2)

                # print crosshair coords
                print(f"Crosshair placed at: ({crosshair_x}, {crosshair_y})")

    # display frame
    cv2.imshow("EasyOCR Button Detection", frame)

    # exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()