#!/usr/bin/env python
# -*- coding: UTF-8 -*
""" parselog unitary tests """

import os
import unittest

import com
import jenkins
import log
import index

class TestJenkinsClass(unittest.TestCase):

    #test du module jenkins

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_jenkins_job_tgz_local_file(self):
        job = jenkins.JenkinsJob('fc6000ts', '256_Generic')
        #Ensure ckcm.tgz local name is OK
        self.assertEqual(job.ckcm_tgz_file_name, '/tmp/ckcm-fc6000ts-256_Generic.tgz')

        #Ensure download is OK
        self.assertTrue(os.path.isfile(job.ckcm_tgz_file_name))

    def test_02_decompressed_ckcm_tgz(self):
        job = jenkins.JenkinsJob('fc6000ts', '256_Generic')
        self.assertNotEqual(job.decompressed_ckcm_tgz('/tmp'), None)
        print 'untar directory: %s' % job.decompressed_ckcm_tgz('/tmp')
        
#Main entry of unitary tests campaigns
if __name__ == '__main__':
    unittest.main()
