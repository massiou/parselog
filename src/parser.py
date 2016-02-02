#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Log parser classes """

__copyright__ = "Copyright 2015, Parrot"

#imports
import os
import log
import mysql.connector as mysql
from datetime import datetime

from src.com import logger

class LogParser(object):
    '''
    Log class generic
    '''
    def __init__(self):
        self.type = 'generic'

    def parse(self, data):
        raise NotImplementedError('No parse method')

class CkcmParser(LogParser):
    """
    Inherit from LogParser
    """
    def __init__(self):
        self.type = 'ckcm'

    def parse(self, ckcm_file_path, version=None, module=None):
        '''
        wxCKCM parser
        @param ckcm_file_path: wxCKCM file path
        @return test_name: file script name
        @return parsed_trace: ckcm formatted traces
        '''
        #Read ckcm file
        test_title = "_".join(os.path.basename(ckcm_file_path).split("_")[:-2])

        # Loop on ckcm file
        with open(ckcm_file_path) as ckcm_file:
            ckcm_content = ckcm_file.read()

        for line in ckcm_content.split('\n'):
            # Ensure first character is a '[' (timestamp)
            if line.startswith("["):
                ckcm_line = log.CkcmLog()
                try:
                    ckcm_line.data = line.decode('utf8')
                    # one line log = one data dictionary 
                    data = {
                        'author': u'jenkins',
                        'test': u"%s" % test_title,
                        'severity': u"%s" % ckcm_line.severity,
                        'text': u"%s" % ckcm_line.data,
                        'library': u'%s' % ckcm_line.library,
                        'ATCommand': u'%s' % ckcm_line.command, 
                        'ATEvent': u'%s' % ckcm_line.event,
                        'index_time': u'%s' % datetime.now().isoformat(),
                        'module': u"%s" % module,
                        'version': u'%s' % version
                          }
                    yield data
                except UnicodeDecodeError:
                    logger.error(UnicodeDecodeError)

class OctopylogParser(LogParser):
    """
    Inherit from LogParser
    """
    def __init__(self, pytestemb_version):
        self.type = 'octopylog'
        self.pytestemb_version = pytestemb_version

    def parse(self, ctp_file_path, version=None, module=None):
        """
        CTP parser
        @param ctp_file_path: wxCKCM file path
        @return test_name: file script name
        @return parsed_trace: octopylog formatted traces
        """
        #Read octopylog file
        test_title = "_".join(os.path.basename(ctp_file_path).split("_")[:-1])
        
        with open(ctp_file_path) as ctp_file:
            ctp_content = ctp_file.read()

        # Loop on octopylog file
        for line in ctp_content.split('\n'):
            # Ensure first character is a digit (timestamp)
            if line and line[0].isdigit():

                ctp_line = log.OctopylogLog(self.pytestemb_version)

                try:
                    ctp_line.data = line.decode('utf8')
                    # one line log = one data dictionary 
                    data = {
                        'author': u'jenkins',
                        'test': u"%s" % test_title,
                        'text': u"%s" % ctp_line.message,
                        'timestamp': u"%s" % ctp_line.timestamp,
                        'library': u"%s" % ctp_line.message_type,
                        'index_time': 'u%s' % datetime.now().isoformat(),
                        'version': u'%s' % version,
                        'module': u'%s' % module
                          }
                    yield data
                except UnicodeDecodeError:
                    logger.error(UnicodeDecodeError)


class MySQLParser(LogParser):
    """
    Inherit from LogParser
    """
    def __init__(self, server, user, password, database, table):
        self.type = 't_table'
        self.pytestemb_version = table
        self.user = user
        self.password = password
        self.server = server
        self.table = table
        self.cur_db = mysql.connect(user=user,
                                    password=password,
                                    host=server,
                                    database=database)

    def parse(self):
        columns = """SHOW COLUMNS FROM {0}""".format(self.table)
        cursor = self.cur_db.cursor(buffered=True)
        cursor.execute(columns)
        columns = cursor.fetchall()
        columns = [column[0] for column in columns]
        query = """SELECT * from {0}""".format(self.table)

        cursor = self.cur_db.cursor(buffered=True)
        cursor.execute(query)
        results = cursor.fetchall()
        print len(results)
        for index, result in enumerate(results):
            data = {col: res for col, res in zip(columns, result)}
            if index % 1000 == 0:
                print index
                print data
            yield data