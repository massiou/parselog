#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Common """

__copyright__ = "Copyright 2015, Matthieu Velay"

# Generic imports
import sys
from datetime import datetime

# logging imports
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler

# fabric imports
from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import blue
from fabric.colors import white

# Globals
JENKINS_SERVER = '' # Fill jenkins server url #TODO

FC60x0_CONFIGS =  (,) # Fill jobs configs to parse #TODO

# logger object creation
logger = logging.getLogger('index')
logger.setLevel(logging.DEBUG)
# Build formatter for each handler
formatter_file = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
formatter_console = logging.Formatter(yellow('[%(asctime)s]') + \
                                      blue('[%(levelname)s]') + \
                                      white(' %(message)s'))

# Set handlers filesize is < 1Mo
file_handler = RotatingFileHandler('index.log', 'a', 1000000, 1)
stream_handler = logging.StreamHandler(stream=sys.stdout)

# Set formatters
file_handler.setFormatter(formatter_file)
stream_handler.setFormatter(formatter_console)

# Set level
file_handler.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.INFO)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

#Decorators
def timing(func):
    '''
    timing decorator
    '''
    def wrapper(*args, **kwargs):
        '''
        func wrapper
        '''
        start = datetime.now()
        func(*args, **kwargs)
        stop = datetime.now()
        logger.debug('Time execution %s, %s : %s sec', \
               func.__name__, args, (stop - start).total_seconds())

    return wrapper

def decompressed_tgz(tgz_file, output_directory):
    """
    @goal: decompressed tar.gz file in a given output directory
    @param tgz_file: tar.gz file to decompress
    @param output_directory: output directory where to decompress
    @return untar_directory: name of the archive parent directory
    """
    import tarfile
    untar_directory = None
    with tarfile.open(tgz_file) as tgz_file:
        tgz_info = tgz_file.getnames()

        if tgz_info:
            tar_directory = tgz_info[0].split('/')[0]
            tgz_file.extractall(output_directory)
            untar_directory = '/'.join([output_directory, tar_directory])
            logger.info("%s untarred", tgz_file.name)
        else:
            logger.warning("%s untar failed", tgz_file)
            untar_directory = None
    return untar_directory


