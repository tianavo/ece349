import cv2
import numpy as np

def find_template_in_image(test_image_path, template_image_path):
    # Load the images
    image = cv2.imread(test_image_path)  # Test image
    template = cv2.imread(template_image_path)  # Template image

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Initialize ORB detector
    #orb = cv2.ORB_create()
    orb = cv2.ORB_create(nfeatures=1000)  # Increase keypoints

    # Detect keypoints and descriptors
    kp_image, des_image = orb.detectAndCompute(gray_image, None)
    kp_template, des_template = orb.detectAndCompute(gray_template, None)

    # Create a brute-force matcher and match descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des_image, des_template)

    # Sort matches based on distance (best matches first)
    matches = sorted(matches, key=lambda x: x.distance)

    # Check if there are enough good matches
    if len(matches) < 3:
        print("No good matches found! Try adjusting the threshold or template size.")
        return None, None

    # Extract the location of good matches
    points_image = np.float32([kp_image[m.queryIdx].pt for m in matches[:10]]).reshape(-1, 1, 2)
    
    if len(points_image) > 0:
        # Compute the center of the matched points
        center_x = np.mean([p[0][0] for p in points_image])
        center_y = np.mean([p[0][1] for p in points_image])

        # Calculate width and height of bounding box
        width = np.std([p[0][0] for p in points_image]) * 4  # Extend width
        height = np.std([p[0][1] for p in points_image]) * 1.5  # Reduce height

        # Apply scaling factor to keep it **horizontally long**
        scale_factor_width = 1.5  # Increase width
        scale_factor_height = 0.4  # Decrease height

        width *= scale_factor_width
        height *= scale_factor_height

        # Define bounding box coordinates
        min_x = int(center_x - width / 2)
        max_x = int(center_x + width / 2)
        min_y = int(center_y - height / 2)
        max_y = int(center_y + height / 2)

        # Draw the adjusted bounding box
        result_image = image.copy()
        cv2.rectangle(result_image, (min_x, min_y), (max_x, max_y), (0, 255, 0), 3)

        # Save the result
        output_image_path = 'detected_template_output.jpg'
        cv2.imwrite(output_image_path, result_image)

        # Show the image
        cv2.imshow("Detected Template with Horizontally Long Bounding Box", result_image)
        cv2.waitKey(10000)
        cv2.destroyAllWindows()

        # Return coordinates
        return [(min_x, min_y), (max_x, max_y)], output_image_path
    else:
        print("No matches found!")
        return None, None

# Example usage
test_image_path = 'testpic6.jpg'  # Full elevator panel
template_image_path = 'templatefive.jpg'   # Template (button 5)
coordinates, output_image_path = find_template_in_image(test_image_path, template_image_path)

if coordinates is not None:
    print("Coordinates of the detected template:", coordinates)
    print("Result image saved as:", output_image_path)