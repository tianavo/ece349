import cv2
import numpy as np

# load the template image (button i want to press)
template = cv2.imread("templatefive.jpg", cv2.IMREAD_GRAYSCALE)
if template is None:
    print("Error: Could not load template image. Check the file path.")
    exit()

# resize template image
template = cv2.resize(template, (100, 100))  # Adjust the size as needed

# use ORB detector
orb = cv2.ORB_create()

# check for keypoints
kp_template, desc_template = orb.detectAndCompute(template, None)

# start camera
cap = cv2.VideoCapture(0)  # 0 for the default webcam
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# bfmatcher object
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

while True:
    # capture camera frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    # resize webcam feed
    frame = cv2.resize(frame, (640, 480))  # change size if necessary

    # convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect keypoints and descriptors in frame
    kp_frame, desc_frame = orb.detectAndCompute(gray_frame, None)

    # match descriptors between template and frame
    matches = bf.match(desc_template, desc_frame)

    # sort matches by distance (best matches first)
    matches = sorted(matches, key=lambda x: x.distance)

    # draw the top 10 matches (can change this maybe?)
    matched_frame = cv2.drawMatches(template, kp_template, gray_frame, kp_frame, matches[:10], None, flags=2)

    # resize the matched frame to make it smaller
    matched_frame = cv2.resize(matched_frame, (400, 300))  # adjust size if necessary

    # display the frame with matches
    cv2.imshow("Feature Matching", matched_frame)

    # find the location of the best match
    if len(matches) > 0:
        best_match = matches[0]
        frame_idx = best_match.trainIdx
        template_idx = best_match.queryIdx

        # get the coordinates of the matched keypoint in frame
        (x, y) = kp_frame[frame_idx].pt

        # offset the marker and rectangle to the right by (80) pixels
        offset = 80
        button_center = (int(x) + offset, int(y))

        # define the rectangle coordinates with the same offset
        rect_top_left = (int(x) - 25 + offset, int(y) - 25)
        rect_bottom_right = (int(x) + 25 + offset, int(y) + 25)

        # draw rectangle around the matched region
        cv2.rectangle(frame, rect_top_left, rect_bottom_right, (0, 255, 0), 2)

        # draw crosshair at the offset center
        cv2.drawMarker(frame, button_center, (0, 255, 0), cv2.MARKER_CROSS, 20, 2)

        # print the offset center coordinates
        print(f"Button found at (offset): {button_center}")

    # display the webcam feed with the detected button
    cv2.imshow("Webcam Feed", frame)

    # exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release the camera and close windows
cap.release()
cv2.destroyAllWindows()