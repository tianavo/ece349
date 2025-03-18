import cv2
import easyocr

# easyocr reader
reader = easyocr.Reader(['en'], gpu=True)  # Set gpu=True if you have a GPU

# initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# detect button 5
target_button = "5"

# capture single image from frame
ret, frame = cap.read()
if not ret:
    print("Failed to capture image")
    exit()

# release cam
cap.release()

# use easyocr
results = reader.readtext(frame)

# loop over each text element
for (bbox, text, confidence) in results:
    # check if text matches button
    if target_button in text:
        # draw rectangle around detected text
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

        # print the detected text and confidence
        print(f"Button {target_button} found with confidence {confidence}")

        # crosshair position STATIC: (60 pixels to the right and 10 pixels down)
        crosshair_x = bottom_right[0] + 55  # 60 pixels to the right of the right edge
        crosshair_y = (top_left[1] + bottom_right[1]) // 2 + 10  # middle of the rectangle vertically + 10 pixels down

        # make sure the crosshair is within the frame boundaries
        if 0 <= crosshair_x < frame.shape[1] and 0 <= crosshair_y < frame.shape[0]:
            # draw crosshair
            crosshair_size = 20  # Size of the crosshair
            cv2.drawMarker(frame, (crosshair_x, crosshair_y), (0, 255, 0), cv2.MARKER_CROSS, crosshair_size, 2)

            # print crosshair coordinates
            print(f"Crosshair placed at: ({crosshair_x}, {crosshair_y})")

# display the processed image
cv2.imshow("Processed Image", frame)

# save the processed image (optional)
cv2.imwrite("processed_image.jpg", frame)

# wait for a key press and close the window
cv2.waitKey(0)
cv2.destroyAllWindows()