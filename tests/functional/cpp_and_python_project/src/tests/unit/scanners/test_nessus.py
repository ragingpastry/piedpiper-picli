import unittest
from mock import patch, Mock
import json
import pytest
import requests

from charon.scanners import nessus

class NessusTest(unittest.TestCase):

    def setUp(self):
        with patch.object(nessus.Nessus, "__init__", lambda x, y: None):
            self.scanner = nessus.Nessus(None)
            self.scanner.url = 'http://localhost'
            self.scanner.access_key = 'test'
            self.scanner.secret_key = 'test'
            self.scanner.policy_id = '123'
            self.scanner.verify = False
            self.headers = {
                'content-type': 'application/json',
                'X-APIKeys': 'accessKey='+self.scanner.access_key+'; secretKey='+self.scanner.secret_key
            }

    @patch('requests.get', autospec=True)
    def test_connect_get(self, mock_get):
        mock_get.return_value.status_code = 200

        result = self.scanner._connect('GET', '/test')

        mock_get.assert_called_once_with(
            self.scanner.url + '/test',
            params=None,
            headers=self.headers,
            verify=self.scanner.verify
            )

    
    @patch('requests.get', autospec=True)
    def test_connect_get_failure(self, mock_get):
        mock_get.return_value.status_code = 400

        result = self.scanner._connect('GET', '/test')

        self.assertRaises(requests.HTTPError)


    @patch('requests.post', autospec=True)
    def test_connect_post(self, mock_post):
        mock_post.return_value.status_code = 200

        result = self.scanner._connect('POST', '/test', data=None)

        mock_post.assert_called_once_with(
            self.scanner.url + '/test',
            data='null',
            headers=self.headers,
            verify=self.scanner.verify
        )

    @patch('requests.post', autospec=True)
    def test_connect_post_failure(self, mock_post):
        mock_post.return_value.status_code = 400

        result = self.scanner._connect('POST', '/test', data=None)

        self.assertRaises(requests.HTTPError)

    
    @patch('requests.put', autospec=True)
    def test_connect_put(self, mock_put):
        mock_put.return_value.status_code = 200

        result = self.scanner._connect('PUT', '/test', data=None)

        mock_put.assert_called_once_with(
            self.scanner.url + '/test',
            data='null',
            headers=self.headers,
            verify=self.scanner.verify
        )


    @patch('requests.put', autospec=True)
    def test_connect_put_failure(self, mock_put):
        mock_put.return_value.status_code = 400

        result = self.scanner._connect('PUT', '/test', data=None)

        self.assertRaises(requests.HTTPError)


    @patch('charon.scanners.nessus.Nessus._connect')
    def test_get_policy_uuid(self, mock_connect):
        mock_connect.return_value = {'uuid': '123'}

        result = self.scanner._get_policy_uuid('123')

        assert result == '123'


    @patch('charon.scanners.nessus.Nessus._connect')
    def test_get_history_ids(self, mock_connect):
        mock_connect.return_value = {
            'history': [
                {
                    'history_id': 123,
                    'uuid': '123'
                }
            ]
        }

        result = self.scanner._get_history_ids('123')

        assert result == {
            '123': 123
        }

    
    @patch('charon.scanners.nessus.Nessus._connect')
    def test_start_scan(self, mock_connect):
        
