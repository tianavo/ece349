import cv2
import numpy as np
import time

def capture_webcam_image():
    cap = cv2.VideoCapture(1)  # Use MacBook's built-in camera (0), adjust if needed

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None

    # Warm up the camera to adjust exposure
    time.sleep(1)
    for _ in range(10):  # Capture and discard 10 frames
        ret, frame = cap.read()

    ret, frame = cap.read()  # Capture final frame
    cap.release()

    if ret:
        image_path = "webcam_image.jpg"
        cv2.imwrite(image_path, frame)
        return image_path
    else:
        print("Error: Could not capture image.")
        return None

def find_template_in_image(test_image_path, template_image_path):
    image = cv2.imread(test_image_path)
    template = cv2.imread(template_image_path)

    if image is None or template is None:
        print("Error: Could not load image or template.")
        return None, None

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(nfeatures=1000)
    kp_image, des_image = orb.detectAndCompute(gray_image, None)
    kp_template, des_template = orb.detectAndCompute(gray_template, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des_image, des_template)
    matches = sorted(matches, key=lambda x: x.distance)

    if len(matches) < 2:
        print("No good matches found!")
        return None, None

    points_image = np.float32([kp_image[m.queryIdx].pt for m in matches[:20]]).reshape(-1, 1, 2)

    if len(points_image) > 0:
        center_x = int(np.median([p[0][0] for p in points_image]))
        center_y = int(np.median([p[0][1] for p in points_image]))

        result_image = image.copy()
        crosshair_size = 25
        crosshair_color = (0, 255, 0)

        cv2.line(result_image, (center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y), crosshair_color, 3)
        cv2.line(result_image, (center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size), crosshair_color, 3)

        output_image_path = 'detected_template_output.jpg'
        cv2.imwrite(output_image_path, result_image)

        cv2.imshow("Detected Template", result_image)
        cv2.waitKey(10000)
        cv2.destroyAllWindows()

        return (center_x, center_y), output_image_path
    else:
        print("No matches found!")
        return None, None

test_image_path = capture_webcam_image()
template_image_path = 'newtemp.jpg' 

if test_image_path:
    coordinates, output_image_path = find_template_in_image(test_image_path, template_image_path)

    if coordinates:
        print("Coordinates of the detected template:", coordinates)
        print("Result image saved as:", output_image_path)