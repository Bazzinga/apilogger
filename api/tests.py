import unittest
import json

from django.test.client import Client
from rest_framework.test import APIClient
from api.logparser import BVParser, LoggerException
from mock import patch


class TestApiLogger(unittest.TestCase):
    """ API Logger class unit tests
    """
    LOG_PATH_URL = '/partnerprovisioning/v1/log'

    def setUp(self):
        self.client = Client()
        self.apiclient = APIClient()

    def tearDown(self):
        del self.apiclient
        del self.client

    def test_post_page_not_found(self):
        """ Testing POST page not found
        """
        ret = self.client.post('/partnerprovisioning/v1/log1')
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 404, "Page not found error")

    def test_get_log_method_not_allowed(self):
        """ Testing get call to apilog, returning method not allowed
        """
        ret = self.client.get(TestApiLogger.LOG_PATH_URL)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 405, "Method not allowed")
        self.assertEqual(ret.status_text, u'METHOD NOT ALLOWED')

    def test_post_log_empty_data(self):
        """ Testing status 400 POST with empty log data
        """
        ret = self.client.post(TestApiLogger.LOG_PATH_URL)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.data, 'Data received is empty')
        self.assertEqual(ret.status_code, 400, "Status 400 returned in POST because empty data")

    def test_with_Apiclient(self):
        """ Using django rest framework apiclient to test apilog
        """
        data = {"data": "datas"}
        ret = self.apiclient.post(TestApiLogger.LOG_PATH_URL, data, format='json')
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 201)
        self.assertEqual(ret.data['data'], 'datas')

    def test_post_log_BE_json_data(self):
        """ Testing POST json log returning data
        """
        data = json.dumps({"data": "datas"})
        ret = self.client.post(TestApiLogger.LOG_PATH_URL, data, content_type='application/json')
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 201)
        self.assertEqual(ret.data['data'], 'datas')

    @patch.object(BVParser, 'parse_log')
    def test_post_BE_content_log_text_plain(self, mock_parse_log):
        """ Testing BE log posted to apilog
        """
        data = '2013/10/11T11:48:50.860 2013/10/11T11:48:50.898 M2M 5f4e6060-58d5-443c-bafd-3f09ba532f28 BE ' \
               'MobileId / 21407 INFOSTATS 400 [{"MobileId":{"info":{"userAgent":"Mozilla/5.0 (Macintosh; ' \
               'Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36",' \
               '"xff":"10.70.15.127, 46.233.72.114","contentType":null}}}]'
        mock_parse_log.return_value = '{"ret": "1234567"}'
        ret = self.client.post(TestApiLogger.LOG_PATH_URL, data, content_type='text/plain')
        mock_parse_log.assert_called_once_with(data)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.data, mock_parse_log.return_value, "Correct data returned")

    @patch.object(BVParser, 'parse_log')
    def test_post_FE_content_text_plain(self, mock_parse_log):
        """ Testing FE data in text plain
        """
        data = '2013/05/17T02:10:25.335 2013/05/17T02:10:25.548 Microsoft 1e246bb8-1162-46a2-93af-1da64ca9e3cb FE ' \
               'FrontendTrustedPartner 9/18297 21407 INFOSTATS 500 [{"exceptionId":' \
               '"SVR1007","exceptionText":"Server Error in Request Processing, retry is allowed: Error sending post ' \
               'request to http://172.18.174.55:18047/notifications/paymentcallback.Error message: ' \
               'javax.ws.rs.client.ClientException: org.apache.cxf.interceptor.Fault: Could not send Message."}]'
        mock_parse_log.return_value = '{"ret": "1234567"}'
        ret = self.client.post(TestApiLogger.LOG_PATH_URL, data, content_type='text/plain')
        mock_parse_log.assert_called_once_with(data)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.data, mock_parse_log.return_value, "Correct data returned")

    @patch.object(BVParser, 'parse_log')
    def test_post_parse_log_exception(self, mock_parse_log):
        """ Testing parse log generating an exception
        """
        data = 'afadfadfadfa'
        mock_parse_log.side_effect = LoggerException('Error processing received log')
        ret = self.client.post(TestApiLogger.LOG_PATH_URL, data, content_type='text/plain')
        mock_parse_log.assert_called_once_with(data)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 400)
        self.assertEqual(ret.data, 'Error processing received log')


class TestApiCollection(unittest.TestCase):
    """ API Collection class unit tests
    """
    COL_PATH_URL = '/partnerprovisioning/v1/collection'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        del self.client

    def test_remove_log_collection_status_204(self):
        """ Testing deleting collection
        """
        ret = self.client.delete(TestApiCollection.COL_PATH_URL)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 204, "Correct remove status returned")


class LogParserTest(unittest.TestCase):
    """ Test log parser module
    """
    def setUp(self):
        self.parser = BVParser()

    def tearDown(self):
        del self.parser

    def test_parse_log_empty_data(self):
        with self.assertRaises(LoggerException):
            self.parser.parse_log('')

    def test_parse_log_be(self):
        data = '2013/10/11T11:48:50.860 2013/10/11T11:48:50.898 M2M 5f4e6060-58d5-443c-bafd-3f09ba532f28 BE ' \
               'MobileId / 21407 INFOSTATS 400 [{"MobileId":{"info":{"userAgent":"Mozilla/5.0 (Macintosh; ' \
               'Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36",' \
               '"xff":"10.70.15.127, 46.233.72.114","contentType":null}}}]'
        ret = self.parser.parse_log(data)
        self.assertIsNotNone(ret)
        self.assertEqual(ret['responseCode'], '400')
        self.assertEqual(ret['api'], 'mobileid')
        self.assertEqual(ret['app'], 'MobileId')
        self.assertEqual(ret['ob'], '21407')
        self.assertEqual(ret['domain'], 'M2M')
        self.assertEqual(ret['origin'], 'BE')

    def test_parse_log_fe(self):
        data = '2013/05/17T02:10:25.335 2013/05/17T02:10:25.548 Microsoft 1e246bb8-1162-46a2-93af-1da64ca9e3cb FE ' \
               'FrontendTrustedPartner 9/18297 21407 INFOSTATS 201 ["POST /payment/v2/payments HTTP/1.0"]'
        ret = self.parser.parse_log(data)
        self.assertIsNotNone(ret)
        self.assertEqual(ret['origin'], 'FE')

    def test_parse_log_fe_empty_body_exception(self):
        data = '2013/05/17T02:10:25.335 2013/05/17T02:10:25.548 Microsoft 1e246bb8-1162-46a2-93af-1da64ca9e3cb FE ' \
               'FrontendTrustedPartner 9/18297 21407 INFOSTATS 201 []'
        with self.assertRaises(LoggerException) as loggerexception:
            self.parser.parse_log(data)
        exc = loggerexception.exception
        self.assertEqual(exc.message, 'Error processing received log')

    def test_parse_data_no_ob_exception(self):
        data = '2013/05/17T02:10:25.335 2013/05/17T02:10:25.548 Microsoft 1e246bb8-1162-46a2-93af-1da64ca9e3cb FE ' \
               'FrontendTrustedPartner 9/18297 INFOSTATS 201 ["POST /payment/v2/payments HTTP/1.0"]'
        with self.assertRaises(LoggerException) as loggerexception:
            self.parser.parse_log(data)

        exc = loggerexception.exception
        self.assertEqual(exc.message, 'Send data does not match with log structure')

    def test_parse_data_without_exception_inside(self):
        data = '2013/05/17T02:10:25.335 2013/05/17T02:10:25.548 Microsoft 1e246bb8-1162-46a2-93af-1da64ca9e3cb FE ' \
               'FrontendTrustedPartner 9/18297 21407 INFOSTATS 500 [{"error": "me da igual lo que llegue"}]'
        ret = self.parser.parse_log(data)
        self.assertIsNotNone(ret)
        self.assertEqual(ret['origin'], 'FE')
        self.assertEqual(ret['responseCode'], '500')
        self.assertEqual(ret['body'][0]['error'], 'me da igual lo que llegue')

    def test_parse_SVR_exception(self):
        data = '2013/05/17T02:10:25.335 2013/05/17T02:10:25.548 Microsoft 1e246bb8-1162-46a2-93af-1da64ca9e3cb FE ' \
               'FrontendTrustedPartner 9/18297 21407 INFOSTATS 500 [{"exceptionId":' \
               '"SVR1007","exceptionText":"Server Error in Request Processing, retry is allowed: Error sending post ' \
               'request to http://172.18.174.55:18047/notifications/paymentcallback.Error message: ' \
               'javax.ws.rs.client.ClientException: org.apache.cxf.interceptor.Fault: Could not send Message."}]'
        ret = self.parser.parse_log(data)
        self.assertIsNotNone(ret)
        self.assertEqual(ret['exceptionId'], 'SVR1007')
        self.assertEqual(ret['app'], 'FrontendTrustedPartner')
        self.assertEqual(ret['responseCode'], '500')

    def test_parse_SVR_exception_new_format(self):
        data = '2013/05/17T02:10:25.335 2013/05/17T02:10:25.548 Microsoft 1e246bb8-1162-46a2-93af-1da64ca9e3cb FE ' \
               'FrontendTrustedPartner 9/18297 21407 INFOSTATS 500 [{"error": {"exceptionId": "SVR1007",' \
               '"exceptionText": "Server Error in Request Processing, retry is allowed: Error sending post request ' \
               'to http://172.18.174.55:18047/notifications/paymentcallback.Error message: ' \
               'javax.ws.rs.client.ClientException: org.apache.cxf.interceptor.Fault: Could not send Message."}}]'
        ret = self.parser.parse_log(data)
        self.assertIsNotNone(ret)
        self.assertEqual(ret['exceptionId'], 'SVR1007')
        self.assertEqual(ret['app'], 'FrontendTrustedPartner')
        self.assertEqual(ret['responseCode'], '500')
