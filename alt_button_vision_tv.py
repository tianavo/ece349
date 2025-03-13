import cv2
import numpy as np

def find_template(image_path, template_path):
    # Load the images
    image = cv2.imread(image_path)
    template = cv2.imread(template_path, 0)  # Convert template to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Get template dimensions
    w, h = template.shape[::-1]
    
    # Apply template matching
    res = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8  # Adjust as needed
    loc = np.where(res >= threshold)
    
    # Draw rectangles around matches
    for pt in zip(*loc[::-1]):
        cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
        cv2.putText(image, f'({pt[0]}, {pt[1]})', (pt[0], pt[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    
    # Show result
    cv2.imshow('Detected Template', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
find_template('testpic.jpg', 'templatefive.jpg')