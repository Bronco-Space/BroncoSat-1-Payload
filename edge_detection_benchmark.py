import numpy as np
from PIL import Image
from PIL import ImageOps
import sys
from scipy import signal
import os
import pathlib

import matplotlib
matplotlib.use('Agg')  # Had to be imported after matplotlib, but before plt
import matplotlib.pyplot as plt

logging_delay = 10
def run():
    workingPath = pathlib.Path().absolute()
    picturesPath = os.path.join(workingPath, 'pictures')

    if not os.path.isdir(picturesPath):
        print('/pictures doesn\'t exist')
        sys.exit(-1);

    file_list = os.listdir(picturesPath)
    for file_name in file_list:
        inPicturePath = os.path.join(workingPath, 'pictures', file_name)
        runED(inPicturePath, None, True)
    return 1

def runED(input, output, deleteFlag):
    input_name = input
    output_name = output

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
    if not deleteFlag:
        plt.title(output_name)
        plt.imsave(output_name, new_Gradient, cmap='gray', format='png')

    return 1

