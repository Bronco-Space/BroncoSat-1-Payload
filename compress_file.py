import gzip
import bz2
import lzma
import zlib
import os
from os.path import isfile, join
import sys
import time
#import png
#These can be removed later, only used for console output
from terminaltables import AsciiTable
import matplotlib.pyplot as plt
import io
from PIL import Image
import PIL

#This file is a modified version of demo_compress.py from https://github.com/fhkingma/bitswap
"""
    This script can be used to compress an image. It will take an input image and attempt to compress it using various compression techniques, and then save the resultant file.
    The main function of this script RETURNS statistics about the compression for use in benchmark_file.py and (without the verbose flag) outputs to CONSOLE the absolute location of the compressed file.
    Run from CLI you must include as arguments a path to the image first, and then optionally a 'v' and/or 'd' for verbose output and to delete the resultant compressed file respectively. i.e. 'python3 compress_file.py "C:\Image.tiff" vd'
    Run from compress_file.main it requires a path to the image, and then boolean values for verbose and delete respectively.
"""
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
def runCompression(path, dir, filename, file_ext, infile_data, compression, verboseFlag, deleteFlag):
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
def main(path, verboseFlag, deleteFlag):
    total_time = time.time()
    # Get info about image
    valid_filetypes = ('png', 'tif', 'tiff', 'jpg', 'jpeg', 'bmp', 'webp')
    dir, filename, file_ext = input_file(path=path)
    if not file_ext in valid_filetypes: #Accept only image files
        print(f'{file_ext} is an invalid file type. {valid_filetypes} are all accepted types.')
        sys.exit(-1)
    uncompressed_size = os.path.getsize(join(dir, filename + '.' + file_ext))  # Size of original file

    # Output info about image
    """file_data = [
        ['Property', 'Value'],
        ['Filename', filename],
        ['Directory', dir],
        ['Raw size', f'{uncompressed_size} bits']
    ]
    table = AsciiTable(file_data)
    table.title = 'File data'
    if verboseFlag:
        print('')
        print(table.table)"""

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
    zlib_size, zlib_time = runCompression(path, dir, filename, file_ext, infile_data, 'zlib', verboseFlag, deleteFlag)
    gzip_size, gzip_time = runCompression(path, dir, filename, file_ext, infile_data, 'gzip', verboseFlag, deleteFlag)
    bz2_size, bz2_time = runCompression(path, dir, filename, file_ext, infile_data, 'bz2', verboseFlag, deleteFlag)
    lzma_size, lzma_time = runCompression(path, dir, filename, file_ext, infile_data, 'lzma', verboseFlag, deleteFlag)
    png_size, png_time = runCompression(path, dir, filename, file_ext, infile_data, 'png', verboseFlag, deleteFlag)
    webp_size, webp_time = runCompression(path, dir, filename, file_ext, infile_data, 'webp', verboseFlag, deleteFlag)

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
    #print(out_log)
    return out_log

if __name__ == '__main__':
    # Check for valid syntax during call
    if len(sys.argv) < 2:
        print(f'Requires at least 1 argument, a path to the file. {len(sys.argv)} argument provided.')
        sys.exit(-1)
    elif len(sys.argv) > 3:
        print(f'Requires at most 2 arguments, a path and "-v" for verboseFlag output. {len(sys.argv)} arguments provided.')

    #Set flags for options. verbose, delete
    vFlag = True if len(sys.argv) > 2 and 'v' in sys.argv[2] else False
    dFlag = True if len(sys.argv) > 2 and 'd' in sys.argv[2] else False
    main(path=sys.argv[1], verboseFlag=vFlag, deleteFlag=dFlag)
