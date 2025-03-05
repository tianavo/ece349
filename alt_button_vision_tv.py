import cv2
import rawpy
import numpy as np

# Function to load the DNG image
def load_dng_image(image_path):
    with rawpy.imread(image_path) as raw:
        rgb_image = raw.postprocess()  # This converts the raw image to a color image
        return rgb_image

# Load the template image (number 5 you want to find)
template = cv2.imread("templatefive.jpg", cv2.IMREAD_GRAYSCALE)
if template is None:
    print("Error: Could not load template image. Check the file path.")
    exit()

# Load the DNG image in which you want to search for the template
dng_image_path = "IMG_7206.DNG"  # Replace with your DNG file
image_to_search = load_dng_image(dng_image_path)
if image_to_search is None:
    print("Error: Could not load DNG image. Check the file path.")
    exit()

# Convert the loaded DNG image to grayscale
image_gray = cv2.cvtColor(image_to_search, cv2.COLOR_RGB2GRAY)

# Step 1: Use ORB to detect features
orb = cv2.ORB_create()

# Find keypoints and descriptors in the template image
kp_template, des_template = orb.detectAndCompute(template, None)

# Find keypoints and descriptors in the DNG image
kp_image, des_image = orb.detectAndCompute(image_gray, None)

# Step 2: Use BFMatcher to find best matches
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Match descriptors
matches = bf.match(des_template, des_image)

# Step 3: Sort matches based on distance and focus on the closest (most accurate) matches
matches = sorted(matches, key=lambda x: x.distance)

# Focus on the best few matches to make the box more specific (can adjust number if needed)
top_matches = matches[:5]

# Extract coordinates for the best matches (keypoints corresponding to the number 5)
coordinates = []
for match in top_matches:
    dng_kp = kp_image[match.trainIdx]  # Keypoint in the DNG image
    coordinates.append((dng_kp.pt[0], dng_kp.pt[1]))

# Convert the coordinates list to a numpy array
coordinates = np.array(coordinates)

# Calculate a smaller bounding box around the keypoints (this time only top few keypoints)
x_min = int(np.min(coordinates[:, 0]))
x_max = int(np.max(coordinates[:, 0]))
y_min = int(np.min(coordinates[:, 1]))
y_max = int(np.max(coordinates[:, 1]))

# Step 4: Draw a smaller bounding box around the best matches
cv2.rectangle(image_to_search, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

# Display the coordinates and the bounding box
print("Coordinates of best matches (x, y):")
for coord in coordinates:
    print(coord)

# Display the image with the bounding box around the detected number 5
cv2.imshow("Image with Bounding Box", image_to_search)
cv2.waitKey(5000)
cv2.destroyAllWindows()
exit()