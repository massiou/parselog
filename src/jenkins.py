#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Get jenkins logs """

__copyright__ = "Copyright 2015, Parrot"


# Module imports
from src.com import JENKINS_SERVER
from src.com import download_tgz_file
import requests

class JenkinsJob(object):
    """
    Build a jenkins job object
    """
    def __init__(self, config_hw=None, config_sw=None,
                 job_number='lastSuccessfulBuild',
                 log_type='ckcm',
                 url_results=None):
        """
        Instantiate a JenkinsJob object
        Download tgz trace file
        Patch to avoid jenkins connection error (SSLv3 forced)
        """
        
        self._ckcm_tgz_file_name = '/tmp/ckcm-%s-%s.tgz' % (config_hw, config_sw)
        self._octopylog_tgz_file_name = '/tmp/octopylog-%s-%s.tgz' % (config_hw, config_sw)
        self.server = JENKINS_SERVER
        base_url = self.server + 'job/nb_' + config_hw.upper() + \
                           '/CONFIG_HW=' + config_hw.upper() + \
                           ',CONFIG_SW=' + config_sw + ',label=' + config_hw.upper() + \
                           '/' + job_number
        if not url_results:
            self.results = "{0}{1}".format(base_url, '/artifact/results/')
        else:
            self.results = url_results

        self.ckcm_traces = self.results + 'ckcm.tgz'
        self.ctp_traces  = self.results + 'pytestemb.tgz'

        #Download jenkins tgz files
        if log_type == 'ckcm':
            download_tgz_file(self.ckcm_traces, self._ckcm_tgz_file_name)
        elif log_type == 'octopylog':
            download_tgz_file(self.ctp_traces, self._octopylog_tgz_file_name)

        self.build_number = int(requests.get("{0}{1}".format(base_url, '/buildNumber'), verify=False).text)

    @property
    def ckcm_tgz_file_name(self):
        """
        getter on ckcm_tgz_file_name
        """
        return self._ckcm_tgz_file_name

    @property
    def octopylog_tgz_file_name(self):
        """
        getter on octopylog_tgz_file_name
        """
        return self._octopylog_tgz_file_name

    def get_url(self):
        return self.results
