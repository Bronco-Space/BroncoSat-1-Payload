import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()
import cv2
#import matplotlib
#matplotlib.use('Agg')  # Had to be imported after matplotlib, but before plt
#import matplotlib.pyplot as plt
import pathlib
import sys

logging_delay = 10
'''
Important information.
Currently this script assumes there is a /pictures directory in the same path as subImageFinder.py
Currently it also assumes within /pictures each image named %imageName%.%fileType% has a paired image named %imageName%_template.%fileType%
The template image is the sub-image that is searched for in the main image. File type must be the same, naming must follow above pattern.
'''

actual_position = ((218, 1400),(3411,2041),(3400,260),(1820,325),(2140,940))

def run():
    #workingPath is the directory this script is in
    workingPath = pathlib.Path(__file__).parent.absolute()
    #picturesPath is the path to the /pictures folder, assumed to be a sub directory within the working directory
    picturesPath = os.path.join(workingPath, 'pictures')

    #If there is not a /pictures path then exit
    if not os.path.isdir(picturesPath):
        print('/pictures doesn\'t exist')
        return -1

    #For every main image in the /pictures folder run the sub image finder.
    file_list = os.listdir(picturesPath)
    results = []
    for file_name in file_list:
        #Only run on files meant for subimage
        if 'US' in file_name and '_template' in file_name :
            inPicturePath = os.path.join(workingPath, 'pictures', 'US_Map.png')
            inPictureTemplatePath = os.path.join(workingPath, 'pictures', file_name)
            results += [findSubImage(inPicturePath, inPictureTemplatePath)]
    return max(results)

#Returns the percent distance the search was off by. Calculated by dividing the distance between estimated and actual location by the length of the diagonal of the picture.
def findSubImage(inImage, inTemplate):

    # This is used to find the actual coordinates from the 'actual_position' global tuple above
    picture_index = -1
    if 'US1' in inTemplate:
        picture_index = 0
    elif 'US2' in inTemplate:
        picture_index = 1
    elif 'US3' in inTemplate:
        picture_index = 2
    elif 'US4' in inTemplate:
        picture_index = 3
    elif 'US5' in inTemplate:
        picture_index = 4

    # Load input images
    img = cv2.imread(inImage,0)
    img2 = img.copy()
    template = cv2.imread(inTemplate,0)
    w, h = template.shape[::-1]

    # All the 6 methods for comparison in a list
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
                'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    coordPairs = []
    normalized = []

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

        coordPairs += [top_left]
        #This code displays the estimated position graphically
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


    allNodes = []             # Combine x and y as one value for easier calculation
    for pair in coordPairs:
        allNodes += [Node(pair[0], pair[1])]

    #Find which nodes are immediately reachable from each individual node
    range = 50  # The radius within which two nodes are considered to be grouped together
    immediateGroupings = [] #These groups are just what nodes are within the radius of the first node.
    for node in allNodes:
        group = Group()
        group.addNode(node)
        for node2 in allNodes: #If node2 is within range of node1, then add it to the list of nodes reachable from node1
            if node != node2:
                if (node.getValue() == node2.getValue()) or (node.getValue() > node2.getValue() and node.getValue()-range < node2.getValue()) or (node.getValue() < node2.getValue() and node.getValue()+range > node2.getValue()):
                    group.addNode(node2)
        immediateGroupings += [group]

    #Group nodes together if they are reachable
    nodeGroups = [] #This list contains the groupings of nodes, allowing for jumps from one node to the next as long as it is within radius
    unassignedGroups = immediateGroupings
    while len(unassignedGroups) != 0:  #While there are nodes not assigned to a nodeGroup
        group = unassignedGroups.pop()
        groupPoolUpdated = True
        while groupPoolUpdated:                      #This is just here so that if a new node is added to this group, we make sure to re-check all unassigned groups
            groupPoolUpdated = False
            for g in unassignedGroups:              #For every free group, if that free group has a node in this current group then
                if any(item in g.getNodes() for item in group.getNodes()):
                    group.addGroup(g)
                    unassignedGroups.remove(g)
                    groupPoolUpdated = True
        nodeGroups += [group]

    #Find the group of nodes that is the largest. This is the group that is most consistent in placement
    biggestGroup = max(nodeGroups, key=lambda group : len(group.getNodes()))

    #Find average position of nodes in biggest group
    xAvg = 0
    yAvg = 0
    for node in biggestGroup.getNodes():
        xAvg += node.getCoords()[0]
        yAvg += node.getCoords()[1]
    xAvg = round(xAvg / len(biggestGroup.getNodes()))
    yAvg = round(yAvg / len(biggestGroup.getNodes()))

    #Find distance from average estimated position to actual position
    distanceDifference = round((((xAvg-actual_position[picture_index][0])**2)+((yAvg-actual_position[picture_index][1])**2))**0.5)  #Distance formula
    percentDifference = ( distanceDifference / (((img.shape[0])**2)+((img.shape[1])**2))**0.5 ) * 100
    return percentDifference

# A x, y point combined into one item
class Node:
    def __init__(self, xCoord, yCoord):
        self.x = xCoord
        self.y = yCoord
        self.value = round( ( (xCoord**2) + (yCoord**2) )**0.5 )

    def getValue(self):
        return self.value

    def getCoords(self):
        return self.x, self.y

#A group of nodes
class Group:
    def __init__(self): 
        self.reachableNodes = []

    def addNode(self, n):
        if n not in self.reachableNodes:
            self.reachableNodes += [n]

    def addGroup(self, g):
        for node in g.getNodes():
            if node not in self.reachableNodes:
                self.reachableNodes += [node]

    def getNodes(self):
        return self.reachableNodes