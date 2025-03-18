import cv2
import numpy as np
import time

def capture_webcam_image():
    # MacBook's built-in camera (1), adjustable
    cap = cv2.VideoCapture(1)   
    # If failed to access webcam:
    if not cap.isOpened():
        print("Error: Could not open webcam. Try again.")
        return None

    time.sleep(1)
    # Capture and discard 10 frames
    for _ in range(10):         
        ret, frame = cap.read()
    # Capture final frame
    ret, frame = cap.read()     
    cap.release()
    # Save captured image before template detection
    if ret:                     
        image_path = "webcam_image.jpg"
        cv2.imwrite(image_path, frame)
        return image_path
    else:
        print("Error: Could not capture image. Try again.")
        return None

def find_template_in_image(test_image_path, template_image_path):
    # Load test image (captured) and template ("newtemp.jpg")
    image = cv2.imread(test_image_path)                     
    template = cv2.imread(template_image_path)

    # If failed to load:
    if image is None or template is None:                   
        print("Error: Could not load test image or template. Try again.")
        return None, None
    
    # Make both images greyscale for easier feature detection
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)    
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Initialize ORB (Oriented FAST and Rotated BRIEF) detector with 1000 features
    orb = cv2.ORB_create(nfeatures=1000)                   
    # Collecy keypoints and descriptors for both images 
    kp_image, des_image = orb.detectAndCompute(gray_image, None)
    kp_template, des_template = orb.detectAndCompute(gray_template, None)

    # Initialize Brute-Force Matcher with Hamming distance as the metric, cross-checking enabled
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Match descriptors of the test image and template using the Brute-Force Matcher
    matches = bf.match(des_image, des_template)
    # Sort the matches by distance (lower distance = better match)
    matches = sorted(matches, key=lambda x: x.distance)
   
    # Check if there are at least 2 good matches
    if len(matches) < 2:
        print("No good matches found!")
        return None, None
    
    # Extract the coordinates of the matched keypoints in the test image
    points_image = np.float32([kp_image[m.queryIdx].pt for m in matches[:20]]).reshape(-1, 1, 2)

    # If matches are found, calculate the median center of the matched points
    if len(points_image) > 0:
        center_x = int(np.median([p[0][0] for p in points_image]))
        center_y = int(np.median([p[0][1] for p in points_image]))

        # Offset crosshair
        offset = 180
        center_x += offset

        # Draw a crosshair on the detected template location in the test image with those features (size, color)
        result_image = image.copy()
        crosshair_size = 25
        crosshair_color = (0, 255, 0)

        # Draw horizontal and vertical lines to form the actual crosshair
        cv2.line(result_image, (center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y), crosshair_color, 3)
        cv2.line(result_image, (center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size), crosshair_color, 3)

        # Save the result image with the crosshair to "detected_template_output.jpg"
        output_image_path = 'detected_template_output.jpg'
        cv2.imwrite(output_image_path, result_image)

        # Display the result image with the detected template for 10 seconds (change 10,000 ms if needed)
        cv2.imshow("Detected Template", result_image)
        cv2.waitKey(10000)
        cv2.destroyAllWindows()

        # Return coordinates of the detected template and the output image path
        return (center_x, center_y), output_image_path
    else:
        print("No matches found!")
        return None, None

# Capture image from webcam (call the function)
test_image_path = capture_webcam_image()
# Location of the template photo in the files of GitHub (ece349)
template_image_path = 'newtemp.jpg' 

# If the webcam image was successfully captured, proceed with template matching
if test_image_path:
    coordinates, output_image_path = find_template_in_image(test_image_path, template_image_path)

    # If the template was successfully detected, print the found oordinates and output image path
    if coordinates:
        print("Coordinates of the detected template:", coordinates)
        print("Result image saved as:", output_image_path)