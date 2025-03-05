import cv2
import rawpy
import numpy as np

# Function to load a DNG image
def load_dng_image(image_path):
    with rawpy.imread(image_path) as raw:
        rgb_image = raw.postprocess()
        return rgb_image

# Load the template image (button you want to find)
template = cv2.imread("templatefive.jpg", cv2.IMREAD_GRAYSCALE)
if template is None:
    print("Error: Could not load template image. Check the file path.")
    exit()

# Normalize the template image
template = cv2.normalize(template, None, 0, 255, cv2.NORM_MINMAX)

# Load the image in which you want to search for the template (DNG image)
image_to_search = load_dng_image("IMG_7200.DNG")
if image_to_search is None:
    print("Error: Could not load image to search. Check the file path.")
    exit()

# Convert the image to grayscale
image_gray = cv2.cvtColor(image_to_search, cv2.COLOR_RGB2GRAY)

# Normalize the image being searched
image_gray = cv2.normalize(image_gray, None, 0, 255, cv2.NORM_MINMAX)

# Initialize variables for matching
best_match = None
best_match_value = -1e10  # Arbitrarily low to start
best_top_left = (0, 0)

# Multi-scale template matching (with smaller increments)
for scale in np.arange(0.5, 1.0, 0.05):  # Start from 50% to 100% size
    # Resize the template to match the current scale
    new_width = int(image_to_search.shape[1] * scale)
    new_height = int((template.shape[0] / template.shape[1]) * new_width)  # Maintain aspect ratio
    template_resized = cv2.resize(template, (new_width, new_height))

    # Match the template at the current scale
    result = cv2.matchTemplate(image_gray, template_resized, cv2.TM_CCOEFF)
    
    # Get the max value and location of the best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Update the best match if we found a better match at this scale
    if max_val > best_match_value:
        best_match_value = max_val
        best_top_left = max_loc
        best_match = template_resized

# Calculate the bottom-right corner of the match
top_left = best_top_left
bottom_right = (top_left[0] + best_match.shape[1], top_left[1] + best_match.shape[0])

# Draw a rectangle around the matched region (optional, to visualize the match)
cv2.rectangle(image_to_search, top_left, bottom_right, (0, 255, 0), 2)

# Display the result (optional, to see the image with the matched region)
cv2.imshow("Matched Result", image_to_search)

# Print the coordinates of the best match
print(f"Best match found at coordinates: {top_left}")

# Wait for a key press and close the window
cv2.waitKey(10000)
cv2.destroyAllWindows()
exit()