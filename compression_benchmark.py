import gzip
import bz2
import lzma
import zlib
from PIL import Image
import os
from os.path import isfile, join
import sys
import time
import csv
import scaleImage
import pathlib

#This can be removed later, only used to make console output look nice
from terminaltables import AsciiTable

#This file is a modified version of demo_compress.py from https://github.com/fhkingma/bitswap
"""
    If you want to run compression on a file use compress()
    If you want to benchmark use compBenchmark()
    If you want to get the run code use run()
    You probably shouldn't call runCompressApproach since that function itself doesn't check path validity
    
    This script can be used to compress an image. It will take an input image and attempt to compress it using various compression techniques, and then save the resultant file.
    The main function of this script RETURNS statistics about the compression for use in benchmark_file.py and (without the verbose flag) outputs to CONSOLE the absolute location of the compressed file.
    Run from CLI you must include as arguments a path to the image first, and then optionally a 'v' and/or 'd' for verbose output and to delete the resultant compressed file respectively. i.e. 'python3 compress_file.py "C:\Image.tiff" vd'
    Run from compress_file.main it requires a path to the image, and then boolean values for verbose and delete respectively.
"""

logging_delay = 10

def input_file(path):  # Input file and check that it is a valid file. Return information about the file.
    if not isinstance(path, str):
        print('Path must be string.')
        sys.exit(-1)
    if not os.path.exists(path):
        print('Path does not exist.')
        sys.exit(-1)
    if not isfile(path):
        print('Path does not point to a file.')
        sys.exit(-1)

    dir, file = os.path.split(os.path.abspath(path))
    filename, file_ext = os.path.splitext(file)
    file_ext = f'{file_ext[1:]}'
    return dir, filename, file_ext

#This function runs the various compression algorithms. Passing path along with dir/filename/file_ext is a bit redundant might change later
def runCompressionApproach(path, dir, filename, file_ext, infile_data, compression, verboseFlag, deleteFlag):
    #Initialize variables
    total_time = 0
    compressed_size = 0
    if verboseFlag: print(f'{compression} compression starting... ', end='', flush=True)

    #Ready file_out
    file_out_path = join(dir, f'{filename}_{file_ext}.{compression}')
    file_out = open(file_out_path, 'wb')

    #Run different compression algorithms
    temp_time = time.time()
    if compression == 'zlib':
        file_out.write(zlib.compress(infile_data))
    elif compression == 'gzip':
        file_out.write(gzip.compress(infile_data))
    elif compression == 'bz2':
        file_out.write(bz2.compress(infile_data))
    elif compression == 'lzma':
        file_out.write(lzma.compress(infile_data))
    elif compression == 'png':
        Image.open(path).save(file_out_path, format='PNG', optimize=True, compress_level=9)
    elif compression == 'webp':
        Image.open(path).save(file_out_path, format='WebP', lossless=True, quality=100, method=6)

    #Set statistics and close file
    time_taken = time.time() - temp_time
    file_out.close()
    compressed_size = os.path.getsize(file_out_path)

    #Determine if this run had better compression than the previous best and take actions accordingly
    global min_size
    if compressed_size < min_size[0]:   #If this approach had the best compression so far
        if verboseFlag: print('Better compression achieved')
        if not deleteFlag and min_size[1] != 'uncompressed':    #If not a benchmark and the previous best wasn't the source image, then delete previous best
            os.remove(join(dir, f'{filename}_{file_ext}.{min_size[1]}'))
        elif deleteFlag:                #Benchmarking so delete any produced files
            os.remove(file_out_path)
        min_size = [compressed_size, compression]
    else:                               #This approach didn't have the best compression, delete file
        if verboseFlag: print('Worse compression achieved')
        os.remove(file_out_path)

    #Determine and update whether this approach had faster compression time
    global min_time
    if time_taken < min_time[0]:
        min_time = [time_taken, compression]

    #Return the resultant compressed size and how long the algorithm ran
    return compressed_size, time_taken

#Global variables that store the fastest and best compression algorithms. Use the format [size/time, 'name of algorithm']
min_size = []
min_time = []
#Main function, called for compression, benchmarking, or that code thing
def compress(path, verboseFlag, deleteFlag):
    total_time = time.time()
    # Get info about image
    valid_filetypes = ('png', 'tif', 'tiff', 'jpg', 'jpeg', 'bmp', 'webp')
    dir, filename, file_ext = input_file(path=path)
    if not file_ext in valid_filetypes: #Accept only image files
        print(f'{file_ext} is an invalid file type. {valid_filetypes} are all accepted types.')
        sys.exit(-1)
    uncompressed_size = os.path.getsize(join(dir, filename + '.' + file_ext))  # Size of original file

    # Open input file and store contents. Create list to store best approach
    infile = open(path, 'rb')
    infile_data = infile.read()

    #Ready running tally of best algorithms
    global min_size
    min_size = [uncompressed_size, 'uncompressed']
    global min_time
    min_time = [float('inf'), 'uncompressed']

    # Run compression
    if verboseFlag:
        print('')
        print('Beginning compression...')

    # Run various compression approaches
    zlib_size, zlib_time = runCompressionApproach(path, dir, filename, file_ext, infile_data, 'zlib', verboseFlag, deleteFlag)
    gzip_size, gzip_time = runCompressionApproach(path, dir, filename, file_ext, infile_data, 'gzip', verboseFlag, deleteFlag)
    bz2_size, bz2_time = runCompressionApproach(path, dir, filename, file_ext, infile_data, 'bz2', verboseFlag, deleteFlag)
    lzma_size, lzma_time = runCompressionApproach(path, dir, filename, file_ext, infile_data, 'lzma', verboseFlag, deleteFlag)
    png_size, png_time = runCompressionApproach(path, dir, filename, file_ext, infile_data, 'png', verboseFlag, deleteFlag)
    webp_size, webp_time = runCompressionApproach(path, dir, filename, file_ext, infile_data, 'webp', verboseFlag, deleteFlag)

    # Output table detailing compression numbers of the different algorithms
    compression_data = [
        ['Compression Scheme', 'Filename', 'Size (bits)', 'Ratio (%)', 'Savings (%)', 'Time (s)'],
        ['Uncompressed', f'{filename}_uncompressed.npy', uncompressed_size, '100.00', '0.00', 'N/A'],
        ['Zlib', f'{filename}_{file_ext}.zlib', zlib_size, f'{(zlib_size / uncompressed_size) * 100:.2f}',
         f'{100. - (zlib_size / uncompressed_size) * 100:.2f}', f'{zlib_time:.3f}'],
        ['GNU Gzip', f'{filename}_{file_ext}.gzip', gzip_size, f'{(gzip_size / uncompressed_size) * 100:.2f}',
         f'{100. - (gzip_size / uncompressed_size) * 100:.2f}', f'{gzip_time:.3f}'],
        ['bzip2', f'{filename}_{file_ext}.bz2', bz2_size, f'{(bz2_size / uncompressed_size) * 100:.2f}',
         f'{100. - (bz2_size / uncompressed_size) * 100:.2f}', f'{bz2_time:.3f}'],
        ['LZMA', f'{filename}_{file_ext}.lzma', lzma_size, f'{(lzma_size / uncompressed_size) * 100:.2f}',
         f'{100. - (lzma_size / uncompressed_size) * 100:.2f}', f'{lzma_time:.3f}'],
        ['PNG', f'{filename}_{file_ext}.png', png_size, f'{(png_size / uncompressed_size) * 100:.2f}',
         f'{100. - (png_size / uncompressed_size) * 100:.2f}', f'{png_time:.3f}'],
        ['WEBP', f'{filename}_{file_ext}.webp', webp_size, f'{(webp_size / uncompressed_size) * 100:.2f}',
         f'{100. - (webp_size / uncompressed_size) * 100:.2f}', f'{webp_time:.3f}'],
    ]
    table = AsciiTable(compression_data)
    table.title = 'Results'
    if verboseFlag:
        print('')
        print(table.table)
        print('')

    #Display information about the best compression algorithm, time taken, and location of file if not deleted
    min_size_format = min_size[1]
    min_time_format = min_time[1]
    if verboseFlag: print(f'{min_size_format} compression resulted in smallest file size', flush=True)
    total_time = time.time() - total_time
    if verboseFlag: print(f'Total time taken: {total_time:.3f} seconds.')
    if not deleteFlag: print(join(dir, f'{filename}_{file_ext}.{min_size[1]}'))

    #Output log data for benchmark_file.py
    out_log = f',uncomp,zlib,gzip,bz2,lzma,png,webp,best\nsize,{uncompressed_size},{zlib_size},{gzip_size},{bz2_size},{lzma_size},{png_size},{webp_size},{min_size_format}\ntime,0,{zlib_time:.3f},{gzip_time:.3f},{bz2_time:.3f},{lzma_time:.3f},{png_time:.3f},{webp_time:.3f},{min_time_format}'

    #Calculate encoded return code
    #If compression results in a size larger than uncompressed or something else wacky goes on it will return 0
    encodedReturnVal = 0000;
    bestRatio = min_size[0] / uncompressed_size #* 1000

    #Use raw float for comparison so if the compressed file is one bit smaller it is still included
    if bestRatio < 1 and bestRatio >= 0:
        if min_size[1] == 'zlib':
            encodedReturnVal = 1000
        elif min_size[1] == 'gzip':
            encodedReturnVal = 2000
        elif min_size[1] == 'bz2':
            encodedReturnVal = 3000
        elif min_size[1] == 'lzma':
            encodedReturnVal = 4000
        elif min_size[1] == 'png':
            encodedReturnVal = 5000
        elif min_size[1] == 'webp':
            encodedReturnVal = 6000

        encodedReturnVal += int(bestRatio * 1000)
    return out_log, encodedReturnVal, bestRatio * 100

#Benchmark
def compBenchmark(path, high, low, inc):
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
        output_log, _, _ = compress(path=f'{image_path}', verboseFlag=False, deleteFlag=True)
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
    return

def run():
    workingPath = pathlib.Path(__file__).parent.absolute()
    picturesPath = os.path.join(workingPath, 'pictures')

    if not os.path.isdir(picturesPath):
        print('/pictures doesn\'t exist')
        sys.exit(-1);

    file_list = os.listdir(picturesPath)
    bestResult = [100.0, 0]
    for file_name in file_list:
        inPicturePath = os.path.join(workingPath, 'pictures', file_name)
        _, val, ratio = compress(inPicturePath, False, True)
        if ratio < bestResult[0]:
            bestResult[0] = ratio
            bestResult[1] = val
    return bestResult[1]
