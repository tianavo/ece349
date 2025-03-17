import cv2
import numpy as np

def find_template_in_image(test_image_path, template_image_path):
    #load images
    image = cv2.imread(test_image_path)  
    template = cv2.imread(template_image_path) 

    #convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    #initialize ORB detector
    orb = cv2.ORB_create(nfeatures=1000)    #increase # of features for more "stability"

    #detect keypoints and descriptors
    kp_image, des_image = orb.detectAndCompute(gray_image, None)
    kp_template, des_template = orb.detectAndCompute(gray_template, None)

    #create a brute-force matcher and match descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des_image, des_template)

    #sort matches based on distance (best matches first)
    matches = sorted(matches, key=lambda x: x.distance)

    #check if there are enough good matches
    if len(matches) < 2:
        print("No good matches found! Try adjusting the threshold or template size.")
        return None, None

    #extract locations of good matches
    points_image = np.float32([kp_image[m.queryIdx].pt for m in matches[:20]]).reshape(-1, 1, 2)
    
    if len(points_image) > 0:
        #center_x = int(np.mean([p[0][0] for p in points_image]))
        #center_y = int(np.mean([p[0][1] for p in points_image]))
        center_x = int(np.median([p[0][0] for p in points_image]))  #compute center of the matches points (median)
        center_y = int(np.median([p[0][1] for p in points_image]))

        result_image = image.copy()         #draw crosshair
        crosshair_size = 100                #size
        crosshair_color = (0, 255, 0)       #color (green)
        
        #horizontal then vertical lines
        cv2.line(result_image, (center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y), crosshair_color, 3)
        cv2.line(result_image, (center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size), crosshair_color, 3)

        output_image_path = 'detected_template_output.jpg'  #save result photo as a .jpg
        cv2.imwrite(output_image_path, result_image)

        cv2.imshow("Detected Template", result_image)       #display result photo
        cv2.waitKey(5000)                                   #show result for 5sec
        cv2.destroyAllWindows()

        return (center_x, center_y), output_image_path
    else:
        print("No matches found!")
        return None, None

test_image_path = 'testpic8.jpg'        #problem photos (2/17 = 12%): testpic4, testpic9 
template_image_path = 'newtemp.jpg'  
coordinates, output_image_path = find_template_in_image(test_image_path, template_image_path)

if coordinates is not None:
    print("Coordinates of the detected template:", coordinates)
    print("Result image saved as:", output_image_path)