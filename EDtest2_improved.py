import numpy as np
from PIL import Image
from PIL import ImageOps
import sys
from scipy import signal

import matplotlib
matplotlib.use('Agg')  # Had to be imported after matplotlib, but before plt
import matplotlib.pyplot as plt

input_name = sys.argv[1]
output_name = sys.argv[2]

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
plt.title(output_name)
plt.imsave(output_name, new_Gradient, cmap='gray', format='png')

