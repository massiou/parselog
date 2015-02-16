#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Common """

__copyright__ = "Copyright 2015, Parrot"

# Generic imports
import os
from datetime import datetime

#Globals

JENKINS_SERVER = 'https://snake:8080/'

#FC60x0_CONFIGS =  ('fc6000tn', '256_Generic_VR-Asia'),\
#                  ('fc6000tn', '256_Panasonic-Honda-14M-T5AA'),\
#                  ('fc6000tn', '256_Panasonic-Honda-14M-T5AA_VR-NorthAmerica'),\
#                  ('fc6000ts', '256_Generic'),\
#                  ('fc6000ts', '256_Pioneer-KM506'),\
#                  ('fc6000ts', '256_AlpineDalian-Honda-G6'),\
#                  ('fc6050w',  'Demo'),\
#                  ('fc6050b',  'Demo_B')

FC60x0_CONFIGS =  ('fc6000tn', '256_Panasonic-Honda-14M-T5AA_VR-NorthAmerica'),\
                  ('fc6000ts', '256_Generic'),\
                  ('fc6000ts', '256_Pioneer-KM506'),\
                  ('fc6000ts', '256_AlpineDalian-Honda-G6'),\
                  ('fc6050w',  'Demo'),\
                  ('fc6050b',  'Demo_B')

VGTT_JOB = "https://snake:8080/view/Asp/view/ASP2%20Dashboard/job/03_OV_VGTT_Tuner_AT_Cmds/63/CONFIG_HW=FC6100,label=VGTT/artifact/results/"

#Decorators
def logging(func):
    '''
    logging decorator
    '''

    def wrapper(*args, **kwargs):
        '''
        func wrapper
        '''
        res = func(*args, **kwargs)
        print func.__name__, args, kwargs
        return res

    return wrapper

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
        print 'Time execution %s, %s : %s sec' % (func.__name__, args, (stop - start).total_seconds())

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
        else:
            untar_directory = None
    return untar_directory

