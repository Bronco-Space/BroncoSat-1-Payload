import os
from os.path import isfile, join
import sys
from PIL import Image
import gzip
import bz2
import lzma
import zlib

#This file is a modified version of demo_decompress.py from https://github.com/fhkingma/bitswap

'''
This script is used to decompress files compressed by compression_benchmark, specifically zlib, gzip, bz2, and lzma.
Currently only runs from CLI with syntax 'python decompress_file.py {path to compressed file}'.
'''

def input_compressed_file():    #Input compressed file, check that it exists, and that it has a valid extension. Return file information
    path = sys.argv[1]

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

    valid_filetypes = ('zlib', 'gzip', 'bz2', 'lzma')
    if not file_ext[1:] in valid_filetypes:
        print(f'{file_ext} is an invalid file type. {valid_filetypes} are all accepted types.')
        sys.exit(-1)

    return dir, filename, file_ext



if __name__ == '__main__':
    # Check that another argument, namely a path, is supplied
    if len(sys.argv) != 2:
        print(f'Requires 1 argument, namely a path to the file. {len(sys.argv)} argument/s provided.')
        sys.exit(-1)

    # Retrieve information about input file
    dir, filename, file_ext = input_compressed_file()

    # Create input and output files
    infile = open(sys.argv[1], 'rb')
    outfile = open(join(dir, f'{filename[0:filename.rindex("_")]}_reconstructed.{filename[filename.rindex("_")+1:]}'), 'wb')

    #Depending on what the extension on the input is, decompress using different algorithm
    if file_ext == '.zlib':
        outfile.write(zlib.decompress(infile.read()))
    elif file_ext == '.gzip':
        outfile.write(gzip.decompress(infile.read()))
    elif file_ext == '.bz2':
        outfile.write(bz2.decompress(infile.read()))
    elif file_ext == '.lzma':
        outfile.write(lzma.decompress(infile.read()))

    infile.close()
    outfile.close()

    # Console output
    print('')
    print(f'{filename[0:filename.rindex("_")]}_reconstructed.{filename[filename.rindex("_")+1:]}')
