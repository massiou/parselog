#!/usr/bin/env python
# -*- coding: UTF-8 -*-
''' Index logs in Elasticsearch '''

__copyright__ = "Copyright 2015, Parrot"

# Generic imports
import os
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.exceptions import RequestError
from elasticsearch.helpers import bulk
from contextlib import contextmanager


# Module imports
import src.jenkins as jenkins
import src.parser as parser
from src.com import logging
from src.com import timing
from src.com import FC60x0_CONFIGS
from src.com import VGTT_JOB
from src.com import decompressed_tgz as decompressed_tgz

@timing
@logging
def delete_data(index_del):
    '''
    @goal: delete index from into elasticsearch database
    @return delete_error_code: error code deletion
    '''
    delete_error_code = None
    es_c = Elasticsearch()

    try:
        delete_error_code = es_c.indices.delete(index = index_del)
        print '>>> delete index: "%s" in database' % index_del
    except NotFoundError:
        print '>>> No such index: "%s" in database' % index_del

    return delete_error_code

@timing
def index_data(log_file_path, es_index, log_type, version=None, pytestemb_version=None):
    '''
    @goal: index log file into elastic search database
    @param log_file_path: path to file traces directory
    @param es_index: ElasticSearch index
    @param version: field version in elastic search  (optional)
    @return error_code: boolean, False if one line is not indexed
    @not_indexed_data: list of all data not indexed
    '''
    #Elasticsearch instance
    es_c = Elasticsearch()
    error_code = True
    not_indexed_data = []

    if log_type == 'ckcm':
        parser_c = parser.CkcmParser()
    elif log_type == 'octopylog':
        parser_c = parser.OctopylogParser(pytestemb_version)

    #Parse log file and format data to export
    parsed_trace = parser_c.parse(log_file_path, version)

    bulk_data = [data for data in parsed_trace]

    try:
        bulk(es_c, bulk_data, index=es_index, doc_type=log_type)
    except RequestError as ex:
        error_code = False
        not_indexed_data.append(data)
        print '%s bad index format' % es_index
        
    #Index data into elastic search
    #for data in parsed_trace:
    #    try:
    #        data['version'] = version
    #        es_c.index(index=es_index, doc_type=log_type, body=data)
    #    except RequestError as ex:
    #        error_code = False
    #        not_indexed_data.append(data)
    #        print '%s bad index format' % es_index

    return error_code, not_indexed_data

@logging
@timing
def index_module(module_type, config, job_number='lastSuccessfulBuild', \
                 log_type='ckcm', url=None):
    '''
    @goal: index module ckcm traces
    @param module_type : fc60x0 module
    @param config: fc60x0 config
    @param job_number: jenkins job number
    @param log_type: ckcm or octopylog
    '''
    err_list = []
    #Create jenkins job object
    jenkins_job = jenkins.JenkinsJob(config_hw = module_type, \
                                     config_sw = config,\
                                     job_number = job_number, \
                                     log_type = log_type, \
                                     url_results = url)

    #Decompressed ckcm.tgz into /tmp/
    if log_type == 'ckcm':
        tgz_file = jenkins_job.ckcm_tgz_file_name
    elif log_type == 'octopylog':
        tgz_file = jenkins_job.octopylog_tgz_file_name

    directory_c = decompressed_tgz(tgz_file, '/tmp')
    print directory_c

    # Get pytestemb version
    pytestemb_version = None
    if log_type == 'octopylog':
        pytestemb_version = get_pytestemb_version(directory_c)

    package_version = get_package_version(directory_c)
    #Build elastic search index
    es_index_current = package_version.lower() + '_' + module_type.lower() + \
                       '_' + config.lower() + '_' + log_type

    #Build field version in ES, common to all file_c
    es_field_version = package_version + '_' + module_type.lower()

    #Delete potential data with same index
    delete_data(es_index_current)

    #Index each line from log file traces
    print "Version : %s, Package: %s, Config: %s" % (package_version, module_type, config)
    for file_c in os.listdir(directory_c):
        print "Parsing... %s" % file_c
        err = index_data(os.path.join(directory_c, file_c), es_index_current, log_type, version = es_field_version, pytestemb_version = pytestemb_version)
        err_list.append(err)

    return all(err_list)

def get_pytestemb_version(directory):
    '''
    @goal: get pytestemb version used for test
    @param directory: directory to parse
    @return pytestemb_version: pytestemb version
    '''
    found = False
    pytestemb_version = None
    for file_c_name in os.listdir(directory):
        if found:
            break
        with open(os.path.join(directory, file_c_name), 'r') as file_c:
            file_c_content = file_c.read()

        for line_c in file_c_content.split('\n'):
            if found:
                break
            if 'Library version : pytestemb' in line_c:
                pytestemb_version = line_c.split()[-1]
                found = True

    return pytestemb_version

def get_package_version(directory):
    '''
    @goal: get version from traces directory
    @param directory: directory to parse
    @return version: package version
    '''
    #Find cmd_CGMREX test file and parse CGMREX command
    check_module_files = [file_c for file_c in os.listdir(directory) \
                          if file_c.startswith('cmd_CGMREX') \
                          or file_c.startswith('check_module_') \
                          or file_c.startswith('setenv_')]

    if not check_module_files:
        #Find cmd_CGMR test file and parse CGMR command
        check_module_files = [file_c for file_c in os.listdir(directory) \
                              if file_c.startswith('cmd_CGMR')]
        [version, file_path] = get_cgmr([os.path.join(directory, file_path) \
                                         for file_path in check_module_files])
    else:
        [version, file_path] = get_cgmrex([os.path.join(directory, file_path) \
                                           for file_path in check_module_files])
    return version

def get_cgmrex(log_file_path_list):
    '''
    @goal: Parse CGMREX command
    @param ckcm_file_path_list: ckcm files paths list
    @return version: FC60x0 version
    @return package: FC60x0 config
    @return ckcm_file_path: ckcm file in which CGMREX has been encountered first
    '''
    version = 'unknown'
    log_file_path = None
    found = False

    #Loop an all ckcm files
    for log_file_path in log_file_path_list:
        if found:
            break
        with open(log_file_path) as log_file:
            file_content = log_file.read()
        for line in file_content.split('\n'):
            #Found '+CGMREX in file'
            if '+CGMREX:' in line:
                version = line.split("'")[1].lower()
                version = version.split()[0] #Ensure no space in version
                print "CGMREX in %s" % log_file_path
                print line
                found = True
                break

    return [version, log_file_path]

def get_cgmr(log_file_path_list):
    '''
    @goal: Parse CGMR command
    @param ckcm_file_path_list: ckcm files paths list
    @return version: FC60x0 version
    @return package: FC60x0 config
    @return ckcm_file_path: ckcm file in which CGMR has been encountered first
    '''
    version = 'unknown'
    log_file_path = None
    found = False

    #Loop an all ckcm files
    for log_file_path in log_file_path_list:
        if found:
            break
        with open(log_file_path) as ckcm_file:
            file_content = ckcm_file.read()
        for line in file_content.split('\n'):
            #Found '+CGMR in file'
            if '+CGMR:HW' in line: #and line.startswith("["):
                version = line.split("-SW")[1].replace("<LF>", '').replace("<0x0D><0x0A>", "")
                print "CGMR in %s" % log_file_path
                print "Version found >>> %s"% line
                print "Version : %s" % version
                found = True
                break

    return [version, log_file_path]

if __name__ == "__main__":
    index_module(module_type='FC6100', config='VGTT', log_type='ckcm', url=VGTT_JOB)
    index_module(module_type='FC6100', config='VGTT', log_type='octopylog', url=VGTT_JOB)
    for config_fc in FC60x0_CONFIGS:
        index_module(config_fc[0], config_fc[1], log_type='ckcm')
        index_module(config_fc[0], config_fc[1], log_type='octopylog')

