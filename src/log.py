#!/usr/bin/env python
# -*- coding: UTF-8 -*-
''' Generic log class '''

__copyright__ = "Copyright 2015, Parrot"

# Generic imports
import re

class GenericLog(object):
    """
    Generic Log class (parent)
    """
    def __init__(self, data):
        """
        Initialize class
        """
        self._log_type = "default"
        self._data = data

    def __str__(self):
        s = 'Log :\n'
        for items in self.__dict__.items():
            s  += '- {0}: {1}\n'.format(*items)
        return s

    def get_version(self):
        raise NotImplementedError


    def get_library(self):
        raise NotImplementedError

class CkcmLog(GenericLog):
    """
    CKCM log class (specific)
    """
    def __init__(self):
        self.log_type = "ckcm"
        self._data    = None
        self.library  = None
        self.severity = None
        self.command  = None
        self.event    = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.severity = self.set_severity()
        self.library = self.set_library()
        self.event = self.set_event()
        self.command = self.set_command()

    def set_library(self):
        '''
        Get library from ckcm frame
        '''
        library = 'unknown'
        cmd_event = None

        blues_str_list  = [']BT', 'rt_postBlues', 'Blues']
        hiphop_str_list = [']HSTI', 'SoftAT_', 'HIPHOP']
        rap_str_list    = [']RAP', ']SIVR']

        if any(cur_str in self.data for cur_str in blues_str_list):
            library = 'blues'
        elif ']HSTI' in self.data:
            library = 'hsti'
        if any(cur_str in self.data for cur_str in rap_str_list):
            library = 'rap'
        if any(cur_str in self.data for cur_str in hiphop_str_list):
            library = 'hiphop'
        elif ']TALA' in self.data:
            library = 'tala'
        elif ']TANGO' in self.data:
            library = 'tango'
        elif ']SOP' in self.data:
            library = 'soprano'
        elif ']CCTOS' in self.data:
            library = 'concertos'
        elif ']DISCO' in self.data:
            library = 'disco'
        elif ']SOUL' in self.data:
            library = 'soul'
        elif 'wxCKCM' in self.data:
            library = 'wxCKCM'

        return library
       
    def set_severity(self):
        '''
        Get library from ckcm frame
        '''
        try:
            severity = self.data.split("[")[4][0].lower().encode('utf8')
        except IndexError:
            severity = 'unknown'
        if severity == 'i':
            severity = 'info'
        elif severity == 'e':
            severity = 'error'
        elif severity == 'w':
            severity = 'warning'
        elif severity == 'd':
            severity = 'debug'
        elif severity == 'v':
            severity = 'verbose'
        elif severity == 'c':
            severity = 'critical'
        else:
            severity = None

        return severity  

    def set_command(self):
        '''
        Get HSTI command
        '''
        command = None
        if self.library == 'hsti':
            if 'WaitCmdAT' in self.data:
                try:
                    command = re.search('(.*)WaitCmdAT(.*)<LF>', self.data).group(2)
                except AttributeError:
                    print '>>> AttributeError: (HSTI Command) Bad ckcm line format:\n>>>%s' % self.data
        return command

    def set_event(self):
        '''
        Get HSTI event
        '''
        event = None
        if self.library == 'hsti':
            if re.search('WaitCmd(.*):(.*)<LF>', self.data):
                try:
                    self._event = re.search('(.*)WaitCmd*(.*)<LF>', self.data).group(2)
                except AttributeError:
                    print '>>> AttributeError: (HSTI Event) Bad ckcm line format:\n>>>%s' % self.data
            elif 'HSTIRapEvent' in self.data:
                try:
                    self.event = re.search('(.*)HSTIRapEvent*(.*)<LF>', self.data).group(2)
                except AttributeError:
                    print '>>> AttributeError: (HSTI Rap Event) Bad ckcm line format:\n>>>%s' % self.data
        return event

class OctopylogLog(GenericLog):
    """
    octopylog class (specific)
    """
    def __init__(self, pytestemb_version):
        self.log_type = "octopylog"
        self._data    = None
        self.message_type  = None
        self.timestamp = None
        self.message = None
        self.pytestemb_version = pytestemb_version
        self.pytestemb_version_major = int(pytestemb_version.split('.')[0])
        self.pytestemb_version_minor = int(pytestemb_version.split('.')[1])
        self.first_field_position = 0
        if self.pytestemb_version_major >= 2 \
        and self.pytestemb_version_minor >= 2:
            self.first_field_position = 2

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.message_type = self.set_message_type()
        self.timestamp = self.set_timestamp()
        self.message = self.set_message()

    def set_message_type(self):
        '''
        Set message type field from octopylog frame
        '''
        if self.data[0].isdigit():
            try:
                message_type = self.data.split()[self.first_field_position + 1]
            except IndexError:
                message_type = None
        else:
            message_type = None
        return message_type

    def set_timestamp(self):
        '''
        Set timestamp field from octopylog frame
        '''
        if self.data[0].isdigit():
            timestamp = self.data.split()[self.first_field_position]
        else:
            timestamp = None
        return timestamp

    def set_message(self):
        '''
        Set message field from octopylog frame
        '''
        if self.data[0].isdigit():
            try:
                message = ' '.join(self.data.split()[self.first_field_position + 2:])
            except IndexError:
                message = None
        else:
            message = None
        return message






