from PIL import Image
import PIL
import sys
import os
from os.path import isfile

"""
    This script resizes the source image to percents of the original image size.
    Usage: CLI or call scaleImage.main() with arguments
    Run from CLI you must provide the path to the image (prepended with PATH:), the highest percentage resolution to run on (prepended with HIGH:), the smallest percentage resolution to run on (prepended with LOW:), and the percent to incrementally run at (prepended with INC:).
    i.e. 'python3 benchmark_file.py PATH:"C:\Image.png" HIGH:100 LOW:50 INC:5' would run compress_file.py on the source image at 100%, 95%, 90%, 85%... and 50% resolution. Starting at 100% and incrementing to 50% by 5% each time.
    Run from calling main() you must provide (the path to the file, high value, low value, inc value). See above about what those values mean. Returns a list of string filepaths to the output scaled images.
    Notes:
    Technically you could provide a HIGH: value above 100. Why you would do that though...
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
    valid_filetypes = ('png', 'tif', 'tiff', 'jpg', 'jpeg', 'bmp', 'webp')
    if not file_ext[1:] in valid_filetypes:
        print(f'{file_ext} is an invalid file type. {valid_filetypes} are all accepted types.')
        sys.exit(-1)

    #Check that numbers were input
    #I would like to levy my personal annoyance with weak/dynamic typing here, because when calling from main() high/low/inc are int, but calling from CLI they are str even though CLI calls main() anyways. Why calling main() from another script and from within this script are different escapes me. I'm sure there is a perfectly logical explanation for this behavior, but irrational annoyance isn't necessarily fueled by logical convention -- in this case it is due to inconvenience.
    if (isinstance(high, str) and not high.isdigit()) or (isinstance(low, str) and not low.isdigit()) or (isinstance(inc, str) and not inc.isdigit()):
        print(f'Percent must be integer only. One of the inputs is not an integer.')
        sys.exit(-1)
    high = int(high)
    low = int(low)
    inc = int(inc)

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
        print(f'Generating {n}% scale image...')

        #Resize image and time
        image = Image.open(path)
        image.resize((round(image.size[0]*(n/100)), round(image.size[1]*(n/100)))).save(f'{filename}_{n}{file_ext}')
        image.close()
        scaled_image_list.append(f'{filename}_{n}{file_ext}')

    return scaled_image_list

if __name__ == '__main__':
    if len(sys.argv) != 5 or not sys.argv[1].upper().startswith('PATH:') or not sys.argv[2].upper().startswith('HIGH:') or not sys.argv[3].upper().startswith('LOW:') or not sys.argv[4].upper().startswith('INC:'):
        print(f'Usage must be:\npython3 {os.path.basename(__file__)} PATH:[path to file] HIGH:[100-0 percent of file size to start at] LOW:[100-0 percent of file size to end at] INC:[integer increment to resize by]\n')
        sys.exit(-1)

    main(sys.argv[1][5:], sys.argv[2][5:], sys.argv[3][4:], sys.argv[4][4:])