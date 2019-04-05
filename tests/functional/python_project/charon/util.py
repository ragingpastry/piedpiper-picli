from __future__ import print_function
import anyconfig
import base64
import contextlib
import json
import logging
import paramiko
import StringIO
import time
import yaml
import uuid
from rq import get_current_job

import charon.scanners.nessus
import charon.notifications.mattermost
import charon.cloudutils.openstack

MERGE_STRATEGY = anyconfig.MS_DICTS
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_command(hostname, username, key, command):
    """
    Execute a given command over a paramiko connection
    The exit code of the command to run must be 0
    param: hostname: The host to connect to
    param: username: The username to connect with
    param: key: The SSH private key as a string
    return: stdout of the command
    """
    try:
        keyfile = StringIO.StringIO(key)
        private_key = paramiko.RSAKey.from_private_key(keyfile)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, username=username, pkey=private_key)
        logger.debug("Initiating SSH session to host {} with user {}".format(hostname, username))
    except paramiko.AuthenticationException as e:
        logger.error('Error while attempting SSH connection. {}'.format(e))
        return False
    try:
        stdin, stdout, stderr = client.exec_command(command)
        logger.debug('Running command: {}'.format(command))
        exit_code = stdout.channel.recv_exit_status()
        if exit_code != 0:
            raise ValueError('Command "{}" returned with non-zero exit code. {}'.format(command, stderr.readlines()))
        output = stdout.readlines()
        logger.debug('Results: {}'.format(output))
        client.close()
        return output
    except Exception, e:
        client.close()
        logger.exception('Error while running SSH command. {}'.format(e))
    


@contextlib.contextmanager
def open_file(filename, mode='r'):
    """
    Open the provide file safely and returns a file type.
    :param filename: A string containing an absolute path to the file to open.
    :param mode: A string describing the way in which the file will be used.
    :return: file type
    """
    with open(filename, mode) as stream:
        yield stream


def merge_dicts(a, b):

    conf = a
    anyconfig.merge(a, b, ac_merge=MERGE_STRATEGY)

    return conf


def run_security_scan(config):
    """
    Run a security scan. Parses config for scanner
    :param config: An instance of the config object
    :return: json of functional test results
    """

    if config.scanner.name == 'nessus':
      scan = charon.scanners.nessus.Nessus(config)

    scan_results = scan.scan()

    return scan_results

def run_tests(config):
    """
    Run functional tests
    :param config: An instance of the config object
    :param cloud: An instance of the cloud object
    :return: json of functional test results
    """
    if config.cloud.name == 'openstack':
        logger.debug('Loading Openstack cloud config')
        cloud = charon.cloudutils.openstack.Openstack(config)

    if config.notification.name == 'mattermost':
        logger.debug("Loading Mattermost notification configuration")
        notify = charon.notifications.mattermost.Mattermost(config)

    with cloud as c:
        logger.debug('Starting security scan')
        security_scan_results = run_security_scan(config)
        logger.debug('Security scan finished')
        key = '123'

        try:
            logger_uuid = uuid.uuid4()
            charon.util.run_command('172.18.129.158', 'ansible', key,
                                    'logger RRC_new_machine_setup: {}'.format(logger_uuid))
            time.sleep(5)
            logging_results = charon.functional.verify_syslog('https://loghost.rinconres.com:8089', 'ftest_splunk',
                                                          '<insert_encrypted_password_here>',
                                                          logger_uuid)
        except Exception as e:
            logger.error('Error running remote command! {}'.format(e))
            logging_results = str(e)

        status = 'failed'

        if (security_scan_results['scan_compliance_failed'] < 44 and 
            logging_results['logging_verified'] == 'True'):
            logger.debug('Tests have passed!')
            status = 'passed'


        results = {
            'security_scan_results': security_scan_results,
            'logging_results': logging_results,
            'status': status
        }

        job = get_current_job()
        notify.send_notification("Job ({}) has finished.".format(job.id), 'test-logging', 'rincon')

        return results


    