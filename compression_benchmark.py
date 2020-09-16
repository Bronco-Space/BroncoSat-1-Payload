from PIL import Image
import PIL
import compress_file
import sys
import os
from os.path import isfile
from terminaltables import AsciiTable
import time
import csv
import scaleImage

"""
    This script can be used to input an image and run compression on it at various resolutions and then output statistics on compression ratio relative to the source image and time taken per algorithm.
    This script resizes the source image to percents of the original image size.
    Usage: CLI or .main()
    Run from CLI you must provide the path to the image (prepended with PATH:), the highest percentage resolution to run on (prepended with HIGH:), the smallest percentage resolution to run on (prepended with LOW:), and the percent to incrementally run at (prepended with INC:).
    i.e. 'python3 benchmark_file.py PATH:"C:\Image.png" HIGH:100 LOW:50 INC:5' would run compress_file.py on the source image at 100%, 95%, 90%, 85%... and 50% resolution. Starting at 100% and incrementing to 50% by 5% each time.
    Run from main() use compression_benchmark.main(string path, int high, int low, int inc)
    Notes:
    Technically you could provide a HIGH: value above 100. Why you would do that though...
    To run once at X resolution size set HIGH:X LOW:X INC:1. inc cannot be 0.
    The incrementing starts from high so the exact low value might not be run if the increment value doesn't coincide with the difference between the two. (high-low)%inc != 0 (i.e. HIGH:100 LOW:90 INC:6 would run on 100% and 94%)
"""

def main(path, high, low, inc):
    if not isinstance(path, str):
        print(f'Path ({path}) must be string.')
        sys.exit(-1)
    if not os.path.exists(path):
        print(f'Path ({path}) does not exist.')
        sys.exit(-1)
    if not isfile(path):
        print(f'Path ({path}) does not point to a file.')
        sys.exit(-1)
    filename, file_ext = os.path.splitext(path)
    uncompressed_size = os.path.getsize(path)
    valid_filetypes = ('png', 'tif', 'tiff', 'jpg', 'jpeg', 'bmp', 'webp')
    if not file_ext[1:] in valid_filetypes:
        print(f'{file_ext} is an invalid file type. {valid_filetypes} are all accepted types.')
        sys.exit(-1)

    # Check that numbers were input
    if type(high) == str and not high.isdigit() or type(low) == str and not low.isdigit() or type(inc) == str and not inc.isdigit():
        print(f'Percent must be integer only. One of the inputs is not an integer.')
        sys.exit(-1)
    high = int(high)
    low = int(low)
    inc = int(inc)

    # create scaled versions of image and store in list
    image_list = scaleImage.main(path, high, low, inc)

    # Stores the data about the resultant sizes and time taken to run compression of each algorithm
    compression_size_data = [
        ['Resolution Percent', 'Resolution', 'Uncompressed Ratio', 'zlib Ratio', 'gzip Ratio', 'bz2 Ratio',
         'lzma Ratio', 'png Ratio', 'webp Ratio', 'Best Compression']]
    compression_time_data = [
        ['Resolution Percent', 'Resolution', 'zlib Time', 'gzip Time', 'bz2 Time', 'lzma Time',
         'png Time', 'webp Time', 'Best Time']]

    # Run compression on each percent size
    for image_path in image_list:
        percent = int(image_path.split('_')[-1].split('.')[0])
        print(f'Running compression on {percent}% scale image...')

        # Run compression and output log to output_log
        image = Image.open(image_path)
        output_log = compress_file.main(path=f'{image_path}', verboseFlag=False, deleteFlag=True)
        image.close()

        # Parse and store output_log information to compression_size/time_data
        compression_sizes = output_log.splitlines()[1].split(',')[1:]
        compression_size_data.append([f'{percent}', f'{round(image.size[0] * (percent / 100))}x{round(image.size[1] * (percent / 100))}',
                                      f'{(int(compression_sizes[0]) / uncompressed_size) * 100:.2f}',
                                      f'{(int(compression_sizes[1]) / uncompressed_size) * 100:.2f}',
                                      f'{(int(compression_sizes[2]) / uncompressed_size) * 100:.2f}',
                                      f'{(int(compression_sizes[3]) / uncompressed_size) * 100:.2f}',
                                      f'{(int(compression_sizes[4]) / uncompressed_size) * 100:.2f}',
                                      f'{(int(compression_sizes[5]) / uncompressed_size) * 100:.2f}',
                                      f'{(int(compression_sizes[6]) / uncompressed_size) * 100:.2f}',
                                      f'{compression_sizes[7]}'])
        compression_times = output_log.splitlines()[2].split(',')[1:]
        compression_time_data.append(
            [f'{percent}', f'{round(image.size[0] * (percent / 100))}x{round(image.size[1] * (percent / 100))}',
             f'{float(compression_times[1]):.3f}', f'{float(compression_times[2]):.3f}',
             f'{float(compression_times[3]):.3f}', f'{float(compression_times[4]):.3f}',
             f'{float(compression_times[5]):.3f}', f'{float(compression_times[6]):.3f}', f'{compression_times[7]}'])

        # Remove the rescaled image
        os.remove(f'{image_path}')

    print()
    # Print compression ratio table
    compression_size_table = AsciiTable(compression_size_data)
    compression_size_table.title = 'Compression Size'
    print(compression_size_table.table)

    # Print compression time table
    compression_time_table = AsciiTable(compression_time_data)
    compression_time_table.title = 'Compression Time'
    print(compression_time_table.table)

    # output csv files
    with open('benchmark_ratio_log.csv', mode='w', newline='') as ratio_log:
        ratio_log = csv.writer(ratio_log, delimiter=',')
        ratio_log.writerows(compression_size_data)

    with open('benchmark_time_log.csv', mode='w', newline='') as time_log:
        time_log = csv.writer(time_log, delimiter=',')
        time_log.writerows(compression_time_data)

if __name__ == '__main__':
    if len(sys.argv) != 5 or not sys.argv[1].upper().startswith('PATH:') or not sys.argv[2].upper().startswith('HIGH:') or not sys.argv[3].upper().startswith('LOW:') or not sys.argv[4].upper().startswith('INC:'):
        print(f'Usage must be:\npython3 {os.path.basename(__file__)} PATH:[path to file] HIGH:[100-0 percent of file size to start at] LOW:[100-0 percent of file size to end at] INC:[integer increment to resize by]\n')
        sys.exit(-1)

    # Check that input path is valid
    path = sys.argv[1][5:]
    high = sys.argv[2][5:]
    low = sys.argv[3][4:]
    inc = sys.argv[4][4:]
    main(path, high, low, inc)