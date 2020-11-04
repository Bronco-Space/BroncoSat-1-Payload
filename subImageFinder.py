import cv2
import numpy as np
import matplotlib
#matplotlib.use('Agg')  # Had to be imported after matplotlib, but before plt
import matplotlib.pyplot as plt
import pathlib
import os
import sys

logging_delay = 10
'''
Important information.
Currently this script assumes there is a /pictures directory in the same path as subImageFinder.py
Currently it also assumes within /pictures each image named %imageName%.%fileType% has a paired image named %imageName%_template.%fileType%
The template image is the sub-image that is searched for in the main image. File type must be the same, naming must follow above pattern.
'''

def run():
    #workingPath is the directory this script is in
    workingPath = pathlib.Path(__file__).parent.absolute()
    #picturesPath is the path to the /pictures folder, assumed to be a sub directory within the working directory
    picturesPath = os.path.join(workingPath, 'pictures')

    #If there is not a /pictures path then exit
    if not os.path.isdir(picturesPath):
        print('/pictures doesn\'t exist')
        sys.exit(-1);

    #For every main image in the /pictures folder run the sub image finder.
    file_list = os.listdir(picturesPath)
    for file_name in file_list:
        #Skip _template files so we only execute subImage finding on one of the "main image-template image" pair
        if '_template' in file_name:
            continue
        inPicturePath = os.path.join(workingPath, 'pictures', file_name)
        inPictureTemplatePath = os.path.join(workingPath, 'pictures', file_name.rsplit('.', 1)[0] + '_template.' + file_name.rsplit('.', 1)[1])
        findSubImage(inPicturePath, inPictureTemplatePath)
    return 1

def findSubImage(inImage, inTemplate):
    #Load input images
    img = cv2.imread(inImage,0)
    img2 = img.copy()
    template = cv2.imread(inTemplate,0)
    w, h = template.shape[::-1]

    # All the 6 methods for comparison in a list
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
                'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    coordPairs = []

    #For now we go through each method, later we might settle on only one
    for meth in methods:
        img = img2.copy()
        method = eval(meth)

        # Apply template Matching
        res = cv2.matchTemplate(img,template,method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc

        # <COMMENT OUT IF YOU DON'T WANT THE WINDOW TO OPEN>
        # bottom_right = (top_left[0] + w, top_left[1] + h)
        #
        # cv2.rectangle(img,top_left, bottom_right, 255, 2)
        #
        # plt.subplot(121),plt.imshow(res,cmap = 'gray')
        # plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        # plt.subplot(122),plt.imshow(img,cmap = 'gray')
        # plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        # plt.suptitle(meth)
        #
        # plt.show()
        # </COMMENT OUT IF YOU DON'T WANT THE WINDOW TO OPEN>
        coordPairs += [top_left, min_val, max_val]
    print(coordPairs)
    return

