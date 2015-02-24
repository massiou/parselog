#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Get jenkins logs """

__copyright__ = "Copyright 2015, Matthieu Velay"


# Generic imports
import urllib2
import shutil

# Module imports
from src.com import JENKINS_SERVER
from src.com import logger

class JenkinsJob(object):
    """
    Build a jenkins job object
    """
    def __init__(self, config_hw=None, config_sw=None, \
                 job_number='lastSuccessfulBuild', \
                 log_type='ckcm', \
                 url_results=None):
        """
        Instantiate a JenkinsJob object
        Download tgz trace file
        Patch to avoid jenkins connection error (SSLv3 forced)
        """
        
        self._ckcm_tgz_file_name = '/tmp/ckcm-%s-%s.tgz' % (config_hw, config_sw)
        self._octopylog_tgz_file_name = '/tmp/octopylog-%s-%s.tgz' % (config_hw, config_sw)
        self.server = JENKINS_SERVER

        if url_results == None:
            self.results = self.server + 'job/03_OV_' + config_hw.upper() + \
                           '/CONFIG_HW=' + config_hw.upper() + \
                           ',CONFIG_SW=' + config_sw + ',label=' + config_hw.upper() + \
                           '/' + job_number + '/artifact/results/'
        else:
            self.results = url_results

        self.ckcm_traces = self.results + 'ckcm.tgz'
        self.ctp_traces  = self.results + 'pytestemb.tgz'

        def download_tgz_file(url_tgz_traces, output_file_name):
            '''
            @goal: download tgz file
            @param url_tgz_traces: tar.gz file url
            @param output_file_name: local filename where to save file
            '''
            request = urllib2.Request(url_tgz_traces)
            response = urllib2.urlopen(request)

            with open(output_file_name, 'wb') as output_file:
                shutil.copyfileobj(response.fp, output_file)

        try:
            ####### Fix to force SSLv3 connection.Otherwise, ######
            ####### we get an error from Jenkins.            ######
            import httplib
            import socket
            import ssl

            class HTTPSConnectionV3(httplib.HTTPSConnection):
                '''
                HTTPS connections V3 class
                '''
                def __init__(self, *args, **kwargs):
                    #super(HTTPSConnectionV3, self).__init__(*args, **kwargs)
                    httplib.HTTPSConnection.__init__(self, *args, **kwargs)

                def connect(self):
                    sock = socket.create_connection((self.host, self.port), self.timeout)
                    if self._tunnel_host:
                        self.sock = sock
                        self._tunnel()
                    try:
                        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv3)
                    except ssl.SSLError:
                        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv23)

            class HTTPSHandlerV3(urllib2.HTTPSHandler):
                '''
                HTTPS Handler V3 class
                '''
                def https_open(self, req):
                    return self.do_open(HTTPSConnectionV3, req)

            handler = HTTPSHandlerV3()
            opener = urllib2.build_opener(handler)
            urllib2.install_opener(opener)
            ############## End of the fix ####################

            #Download jenkins tgz files
            if log_type == 'ckcm':
                download_tgz_file(self.ckcm_traces, self._ckcm_tgz_file_name)
            elif log_type == 'octopylog':
                download_tgz_file(self.ctp_traces, self._octopylog_tgz_file_name)

        except urllib2.HTTPError as exc:
            logger.error('urllib2.HTTPError')
            logger.error("url_results: %s", url_results)
            raise exc
        except Exception as exc:
            logger.error('url_results:%s', self.results)
            raise exc

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

