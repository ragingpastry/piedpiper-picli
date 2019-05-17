import anyconfig
import datetime
from typing import Dict
import json
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists, SignatureDoesNotMatch)
import hashlib
import re
import requests
import time
import sys
import uuid
import yaml

from picli.logger import get_logger

LOG = get_logger(__name__)


class SafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(SafeDumper, self).increase_indent(flow, False)


def merge_dicts(a: Dict, b: Dict) -> Dict:
    """
    Merges the values of B into A and returns a mutated dict A.
    ::
        dict a
        b:
           - c: 0
           - c: 2
        d:
           e: "aaa"
           f: 3
        dict b
        a: 1
        b:
           - c: 3
        d:
           e: "bbb"
    Will give an object such as::
        {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}
    :param a: the target dictionary
    :param b: the dictionary to import
    :return: dict
    """
    anyconfig.merge(a, b, ac_merge=anyconfig.MS_DICTS)

    return a


def generate_hashsum(input_file):
    hash = hashlib.sha256()
    byte_array = bytearray(128 * 1024)
    memory_view = memoryview(byte_array)
    with open(input_file, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(memory_view), 0):
            hash.update(memory_view[:n])
    return hash.hexdigest()


def upload_artifact(bucket_name, object_name, file_path, url, access_key, secret_key):
    try:
        minioClient = Minio(url,
                            access_key=access_key,
                            secret_key=secret_key,
                            secure=False
                          )
    except ResponseError as err:
        message = f"Unable to connect to storage endpoint. \n\n{err}"
        sysexit_with_message(message)
    try:
        minioClient.make_bucket(bucket_name)
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except (ResponseError,SignatureDoesNotMatch) as err:
        message = f"Unable to connect to storage endpoint. \n\n{err}"
        sysexit_with_message(message)
    finally:
        try:
            minioClient.fput_object(bucket_name, object_name, file_path)
            return minioClient.stat_object(bucket_name, object_name)
        except ResponseError as e:
            message = f"Unable to upload artifact to {url}. \n\n{e}"
            sysexit_with_message(message)


def camelize(string):
    return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)


def safe_load(string):
    try:
        return yaml.safe_load(string) or {}
    except yaml.scanner.ScannerError as e:
        sysexit_with_message(str(e))


def safe_load_file(filename):
    try:
        with open(filename) as file:
            return safe_load(file)
    except EnvironmentError as e:
        message = f"Unable to load file {filename}.\n\n{e}"
        sysexit_with_message(message)


def safe_dump(data):
    return yaml.dump(data, Dumper=SafeDumper,
                     default_flow_style=False,
                     explicit_start=True)


def generate_run_id():
    return str(uuid.uuid4())


def sysexit_with_message(msg, code=1):
    LOG.critical(msg)
    sys.exit(code)


def request_new_task_id(run_id=None,
                        gman_url=None,
                        project=None,
                        caller='picli',
                        debug=False):
    try:
        if debug:
            LOG.info(f'Requesting new {id_type} from gman at {gman_url}')
        data = {
            'run_id': run_id,
            'caller': caller,
            'project': project,
            'message': 'Requesting new taskID',
            'status': 'started',
        }
        r = requests.post(f"{gman_url}", data=json.dumps(data))
    except requests.exceptions.RequestException as e:
        message = f"Failed to request new taskID from gman at {gman_url}. \n\n{e}"
        sysexit_with_message(message)

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        message = f"Failed to request new taskID from gman at {gman_url}. \n\n{e}"
        sysexit_with_message(message)
    else:
        if debug:
            LOG.info
        id = r.json()['task']['task_id']
        return id


def get_artifact_uri(hash=None, gman_url=None):
        try:
            r = requests.get(f"{gman_url}/hash/{hash}")
        except requests.exceptions.RequestException as e:
            message = f'Failed to send hash to {gman_url}. \n\n{e}'
            sysexit_with_message(message)
        else:
            if r.status_code == 302:
                LOG.info(f'Hashsum found')
                try:
                    return r.json()['artifact']['uri']
                except KeyError as e:
                    message = f'Received invalid json from {gman_url}. \n\n{e}'
                    sysexit_with_message(message)
            elif r.status_code == 404:
                LOG.info('Hashsum not found')
                return None


def wait_for_task_status(task_id=None, status=None, gman_url=None, debug=False, retry_max=10):
    retries = 0
    while retries < retry_max:
        try:
            if debug:
                LOG.info(f'Checking status of task {task_id}')
            r = requests.get(f'{gman_url}/{task_id}/events')
        except requests.exceptions.RequestException as e:
            message = f'Failed to check status of task. \n\n{e}'
            sysexit_with_message(message)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            message = f"Failed to check status of task. \n\n{e}"
            sysexit_with_message(message)
        else:
            # Obviously this will have to change. We should instead wait for ALL event status' to be True
            print(r.json())
            for event in r.json():
                if event.get('status') == status:
                    return True
            else:
                retries += 1
                time.sleep(1)

    message = f'Checking task status timeout for task {task_id}'
    sysexit_with_message(message)


def download_artifact(bucket_name, object_name, file_path, url, access_key, secret_key):
    minioClient = Minio(url,
                        access_key=access_key,
                        secret_key=secret_key,
                        secure=False
                        )
    return minioClient.fget_object(bucket_name, object_name, file_path)


