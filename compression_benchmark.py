import gzip
import bz2
import lzma
import zlib
from PIL import Image
import os
from os.path import isfile, join
import sys
import scaleImage
import pathlib

#This file is a heavily modified version of demo_compress.py from https://github.com/fhkingma/bitswap
"""
    This script can be used to compress an image. It will take an input image and attempt to compress it using various compression techniques.
    run() is the entry point of execution for this file.
    
    Information about compression approaches:
    Six compression methods are attempted - zlib, gzip, bz2, lzma, png, and webp. 
    The latter two use Pillow to compress to the format. 
    The first four use their corresponding approach to compress the raw binary of the input file. decompress_file.py is needed to uncompress them. 
    
    Method overview:
    run() - This method is intended to be used for running the benchmark. It will call compress() on every file within the /pictures directory and return the best compression ratio along with corresponding approach encoded as a 4 digit integer. The first digit of the returned value indicates compression approach and the last three indicate ratio where '123' would mean a ratio of 12.3%. It doesn't save a file and it only outputs the return value to console.
    compress() - This method is the method that runs all the compression approaches for a given image. To do this it calls runCompressionApproach() once for each approach.
    runCompressionApproach() - This method runs the specified compression approach on the given input file.
    process_input_file() - takes a file path as input and verifies it is valid. Returns information about the file that is used later.
"""

LOGGING_DELAY = 10

# Calls compress() on every image in the /pictures directory
# Arguments:
#   None
# Returns:
#   Encoded 4 digit integer representing best compression ratio and associated compression method. First digit indicates method, last three digits indicate ratio where 123 means 12.3%
def run():
    #Find paths
    workingPath = pathlib.Path().absolute()
    picturesPath = os.path.join(workingPath, 'pictures')

    #Check if /pictures path exists in same directory
    if not os.path.isdir(picturesPath):
        print('ERROR in compression_benchmark: /pictures directory doesn\'t exist')
        return 0

    bestResult = [100.0, 0] #Stores best compression ratio and associated method. bestResult[0] is the ratio, bestResult[1] stores the encoded return value

    #For every picture in /pictures run compress() on them and save the best compression ratio and associated method
    file_list = os.listdir(picturesPath)
    for file_name in file_list:
        inPicturePath = os.path.join(workingPath, 'pictures', file_name)    #Get path to picture

        #Create scaled versions of each image and run compression on each of those
        scaled_file_list = scaleImage.main(inPicturePath, 150, 50, 10)  #SET AMOUNTS
        for scaled_file_path in scaled_file_list:
            val, ratio = compress(scaled_file_path)
            #If this picture had better compression, update bestResult
            if ratio < bestResult[0]:
                bestResult[0] = ratio
                bestResult[1] = val
            os.remove(scaled_file_path)

    return bestResult[1]

# Runs various compression methods on input file.
# Arguments:
#   path - String representing path to image i.e. 'C:/image.png'
# Returns:
#   Encoded value, and associated compression ratio as float for accuracy during comparison.
def compress(path):
    # Get info about image
    valid_filetypes = ('png', 'tif', 'tiff', 'jpg', 'jpeg', 'bmp', 'webp')
    dir, filename, file_ext = process_input_file(path=path)
    if not file_ext in valid_filetypes: #Accept only image files
        print(f'ERROR in compression_benchmark: {file_ext} is an invalid file type. {valid_filetypes} are all accepted types.')
        return 0
    uncompressed_size = os.path.getsize(path)  # Size of original file

    # Open input file and store contents
    infile = open(path, 'rb')
    infile_data = infile.read()

    #Ready running tally of best algorithm
    min_size = [uncompressed_size, 'uncompressed']

    # Run various compression approaches. If one gets better compression size, then update min_size to reflect this change
    compression_approaches = ('zlib', 'gzip', 'bz2', 'lzma', 'png', 'webp')
    for method in compression_approaches:
        temp_size = runCompressionApproach(path, dir, filename, file_ext, infile_data, method)
        if temp_size < min_size[0]:
            min_size[0] = temp_size
            min_size[1] = method

    #Calculate encoded return code
    #If compression results in a size larger than uncompressed or something else wacky goes on it will return 0
    encodedReturnVal = 0000
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
    return encodedReturnVal, bestRatio * 100

#This function runs the specified compression technique on the input file.
# Arguments:
#   path - String path to image i.e. 'C:/image.png'
#   dir - String directory to image i.e. 'C:/'
#   filename - String file name i.e. 'image'
#   file_ext - String file extension i.e. 'png'
#   infile_data - the data of the input image which we will compress
#   compression_method - String the method to use when compressing i.e. 'zlib'
# Returns:
#   compressed_size - Integer size of compressed file
def runCompressionApproach(path, dir, filename, file_ext, infile_data, compression_method):
    #Initialize variables
    compressed_size = 0

    #Ready file_out
    file_out_path = join(dir, f'{filename}_{file_ext}.{compression_method}')
    file_out = open(file_out_path, 'wb')

    #Run different compression algorithms
    if compression_method == 'zlib':
        file_out.write(zlib.compress(infile_data))
    elif compression_method == 'gzip':
        file_out.write(gzip.compress(infile_data))
    elif compression_method == 'bz2':
        file_out.write(bz2.compress(infile_data))
    elif compression_method == 'lzma':
        file_out.write(lzma.compress(infile_data))
    elif compression_method == 'png':
        Image.open(path).save(file_out_path, format='PNG', optimize=True, compress_level=9)
    elif compression_method == 'webp':
        Image.open(path).save(file_out_path, format='WebP', lossless=True, quality=100, method=6)

    #Store size of the compressed file
    file_out.close()
    compressed_size = os.path.getsize(file_out_path)
    os.remove(file_out_path)

    #Return the resultant compressed size
    return compressed_size

# Input file and check that it is a valid file. Return information about the file.
# Arguments:
#   Path is the path to the file i.e. "C:/image.png"
# Return:
#   dir - String directory to image i.e. 'C:/'
#   filename - String file name i.e. 'image'
#   file_ext - String file extension i.e. 'png'
def process_input_file(path):
    if not isinstance(path, str):
        print('ERROR in compression_benchmark: Path must be string.')
        return 0
    if not os.path.exists(path):
        print('ERROR in compression_benchmark: Path does not exist.')
        return 0
    if not isfile(path):
        print('ERROR in compression_benchmark: Path does not point to a file.')
        return 0

    dir, file = os.path.split(os.path.abspath(path))
    filename, file_ext = os.path.splitext(file)
    file_ext = f'{file_ext[1:]}'
    return dir, filename, file_ext


