from PIL import Image
import PIL
import sys
import os
from os.path import isfile

"""
    This script resizes the source image to percents of the original image size. Rescaled images are dumped in the same directory as the source image and a list of the paths to the new images is returned for easier iteration later.
    To run call main(path, high, low, inc) where:
        path is the path to the input image
        high is the highest percentage version of the image to create
        low is the lowest percentage version of the image to create
        inc is the value to increment between high and low
        
    Notes:
    Technically you could provide a HIGH: value above 100
    To run once at X resolution size set HIGH:X LOW:X INC:1. inc cannot be 0.
    The incrementing starts from high so the exact low value might not be run if the increment value doesn't coincide with the difference between the two. (high-low)%inc != 0 (i.e. HIGH:100 LOW:90 INC:6 would run on 100% and 94%)
"""

def main(path, high, low, inc):
    #Check that input path is valid
    if not isinstance(path, str):
        print('Path must be string.')
        sys.exit(-1)
    if not os.path.exists(path):
        print('Path does not exist.')
        sys.exit(-1)
    if not isfile(path):
        print('Path does not point to a file.')
        sys.exit(-1)
    filename, file_ext = os.path.splitext(path)

    #Make sure the file is an image
    valid_filetypes = ('png', 'tif', 'tiff', 'jpg', 'jpeg', 'bmp', 'webp')
    if not file_ext[1:] in valid_filetypes:
        print(f'{file_ext} is an invalid file type. {valid_filetypes} are all accepted types.')
        sys.exit(-1)

    #Stores the percent sizes to rescale to
    i = high
    percent_list = []
    # Populate percent_list. Essentially just range() but backwards
    while i >= low:
        percent_list.append(i)
        i = i - inc

    #Scale image
    scaled_image_list = []
    for n in percent_list:
        #Resize image and time
        image = Image.open(path)
        image.resize((round(image.size[0]*(n/100)), round(image.size[1]*(n/100)))).save(f'{filename}_{n}{file_ext}')
        image.close()
        scaled_image_list.append(f'{filename}_{n}{file_ext}')

    return scaled_image_list
