import numpy as np
from PIL import Image
from PIL import ImageOps
import sys
from scipy import signal
import os
import pathlib
import scaleImage

import matplotlib
matplotlib.use('Agg')  # Had to be imported after matplotlib, but before plt
import matplotlib.pyplot as plt

'''
This script is used to run edge detection on an image.

Method overview:
run() - This method calls runED() on every image in /pictures directory
runED() - This method runs the edge detection on the supplied input image and saves it to a supplied output
'''


logging_delay = 15
#run() calls runED() on every image in /pictures directory
# Arguments:
#   None
# Returns:
#   Just returns 1
def run():
    #Find paths
    workingPath = pathlib.Path().absolute()
    picturesPath = os.path.join(workingPath, 'pictures')

    #Check that /pictures directory exists
    if not os.path.isdir(picturesPath):
        print('/pictures doesn\'t exist')
        return 0

    #For every image in /pictures
    file_list = os.listdir(picturesPath)
    for file_name in file_list:
        
        inPicturePath = os.path.join(workingPath, 'pictures', file_name)

        # Create scaled versions of each image and run ED on each of those
        scaled_file_list = scaleImage.main(inPicturePath, 150, 50, 5)  # SET AMOUNTS
        for scaled_file_path in scaled_file_list:
            if scaled_file_path.endswith('.jpg'):
                runED(scaled_file_path)
            os.remove(os.path.join(picturesPath, scaled_file_path))

    return 1

# Does edge detection
# Arguments:
#   input - String path to image input
# Returns:
#   Just returns 1
def runED(input):
    input_name = input
    #output_name = output

    # Open the image and grayscale it
    gray_img = np.array(ImageOps.grayscale(Image.open(input_name))).astype(np.uint8)

    # Get dimensions of image
    h, w = gray_img.shape

    # Define kernels
    horizontal_Kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])  # s2
    vertical_Kernel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])  # s1

    # Fill arrays with zeros
    horizontal_Gradient = np.zeros((h, w))
    vertical_Gradient = np.zeros((h, w))
    new_Gradient = np.zeros((h, w))

    # Calculate horizontal and vertical gradients
    horizontal_Gradient = signal.convolve2d(in1=gray_img, in2=horizontal_Kernel, mode='valid', boundary='fill', fillvalue=0)
    vertical_Gradient = signal.convolve2d(in1=gray_img, in2=vertical_Kernel, mode='valid', boundary='fill', fillvalue=0)

    # Combine horizontal and vertical gradients
    combineHorizVert = lambda x, y: np.sqrt(pow(x, 2.0) + pow(y, 2.0))
    new_Gradient = np.array(list(map(combineHorizVert, horizontal_Gradient, vertical_Gradient)))

    # Save to output
    #plt.title(output_name)
    #plt.imsave(output_name, new_Gradient, cmap='gray', format='png')

    return 1

