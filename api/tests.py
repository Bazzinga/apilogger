import unittest
import json

from django.test.client import Client
from rest_framework.test import APIClient
from api.logparser import BVParser, LoggerException
from apilog.mongo import RequestsDao
from pymongo.errors import DuplicateKeyError
from mock import patch
from django.core.urlresolvers import reverse


class TestApiLogger(unittest.TestCase):
    """ API Logger class unit tests
    """
    LOG_PATH_URL = reverse('logger-api')

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

    def test_delete_log_exception_method_not_allowed(self):
        """ Testing get call to apilog, returning method not allowed
        """
        ret = self.client.delete(TestApiLogger.LOG_PATH_URL)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 405, "Method not allowed")
        self.assertEqual(ret.status_text, u'METHOD NOT ALLOWED')

    def test_get_empty_log_info(self):
        """ Testing getting empty log information
        """
        ret = self.client.get(TestApiLogger.LOG_PATH_URL)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 400)
        self.assertEqual(ret.data, "Unknown log ID")

    @patch.object(RequestsDao, 'select')
    def test_get_log_info(self, mock_select):
        """ Testing getting log information
        """
        query = {"id": 12345678}
        mock_select.return_value = {
            "_id": {"$oid": "5280abe0fdc74475f9581e58"},
            "origin": "FE",
            "body": "[\"GET /provisioning/v1/applications?serviceId=1&fields=appId&appApi.keyword=wo15671 HTTP/1.1\"]",
            "http_request": {
                "url": "provisioning/v1/applications",
                "api": "provisioning",
                "method": "GET"
            },
            "responseDate": {"date": 1382323724329},
            "api": "provisioning",
            "app": "FrontendBasic",
            "domain": "Bluevia",
            "host": "nsdpgwfe1",
            "serviceId": "1",
            "requestDate": {"date": 1382323724170},
            "body_request": {

            },
            "responseCode": "200",
            "appId": "40601",
            "transactionId": "0866111a-d601-42a2-9ec4-403a1391735c",
            "id": 1,
            "statType": "INFOSTATS"
        }
        ret = self.client.get(TestApiLogger.LOG_PATH_URL, query)
        # QueryDict works with unicode data
        mock_select.assert_called_once_with(unicode(query['id']))
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 200)
        self.assertIsInstance(ret.data, dict)
        self.assertEqual(ret.data, {'result': mock_select.return_value})



    def test_post_log_empty_data(self):
        """ Testing status 400 POST with empty log data
        """
        ret = self.client.post(TestApiLogger.LOG_PATH_URL)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.data, 'Data received is empty')
        self.assertEqual(ret.status_code, 400, "Status 400 returned in POST because empty data")

    @patch.object(RequestsDao, 'insert')
    def test_insert_exception_mongodb(self, mock_request_dao):
        """ Using django rest framework apiclient to test apilog
        """
        data = {"data": "datas"}
        error_text = 'Duplicated data inserted'
        mock_request_dao.side_effect = DuplicateKeyError(error_text, code=1000)
        ret = self.apiclient.post(TestApiLogger.LOG_PATH_URL, data, format='json')
        mock_request_dao.assert_called_once_with(dict({"data": "datas"}))
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 400)
        self.assertEqual(ret.data, error_text)

    @patch.object(RequestsDao, 'insert')
    def test_with_Apiclient(self, mock_request_dao):
        """ Using django rest framework apiclient to test apilog
        """
        data = {"data": "datas"}
        mock_request_dao.return_value = 12345678
        ret = self.apiclient.post(TestApiLogger.LOG_PATH_URL, data, format='json')
        mock_request_dao.assert_called_once_with(dict({"data": "datas"}))
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 201)
        self.assertIsInstance(ret.data, dict)
        self.assertEqual(ret.data, {"result": 12345678})

    @patch.object(RequestsDao, 'insert')
    def test_post_log_BE_json_data(self, mock_request_dao):
        """ Testing POST json log returning internal id
        """
        data = json.dumps({"data": "datas"})
        mock_request_dao.return_value = 12345678
        ret = self.client.post(TestApiLogger.LOG_PATH_URL, data, content_type='application/json')
        mock_request_dao.assert_called_once_with(dict({"data": "datas"}))
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 201)
        self.assertIsInstance(ret.data, dict)
        self.assertEqual(ret.data, {"result": 12345678})

    @patch.object(RequestsDao, 'insert')
    @patch.object(BVParser, 'parse_log')
    def test_post_BE_content_log_text_plain(self, mock_parse_log, mock_request_dao):
        """ Testing BE log posted to apilog
        """
        data = '2013/10/11T11:48:50.860 2013/10/11T11:48:50.898 M2M 5f4e6060-58d5-443c-bafd-3f09ba532f28 BE ' \
               'MobileId / 21407 INFOSTATS 400 [{"MobileId":{"info":{"userAgent":"Mozilla/5.0 (Macintosh; ' \
               'Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36",' \
               '"xff":"10.70.15.127, 46.233.72.114","contentType":null}}}]'
        mock_parse_log.return_value = {
            "_id": {"$oid": "5280abe0fdc74475f9581e68"},
            "origin": "BE",
            "body": [
                {
                    "MobileId": {
                        "info": {
                            "partnerName": "microsoft",
                            "bidToken": "3896c84e4ebdcda938e6ce93e94e575d",
                            "contentType": "application/pkcs7-mime;smime-type=signed-data",
                            "appProvider": "40501",
                            "xff": "190.13.109.136",
                            "targetURL": "http://moservices.microsoft.com/mobi/identity/v1/FON-CO",
                            "userAgent": "ZDM/4.0; Windows Mobile 7.0;",
                            "msisdnHeaders": {
                                "name": "X-ZTGO-BearerAddress",
                                "value": "EVsgM21XSfhDatrWIh82QA=="
                            }
                        }
                    }
                }
            ],
            "http_request": {

            },
            "responseDate": {"date": 1382323842728},
            "api": "mobileid",
            "app": "MobileId",
            "domain": "Bluevia",
            "host": "nsdpgwfe1",
            "serviceId": "1",
            "requestDate": {"date": 1382323841853},
            "body_request": {
                "partnerName": "microsoft",
                "msisdn": "",
                "targetURL": "http://moservices.microsoft.com/mobi/identity/v1/FON-CO"
            },
            "responseCode": "200",
            "appId": "40501",
            "transactionId": "7143875b-5095-408e-a824-7bdd4e8bb929",
            "id": 17,
            "statType": "INFOSTATS"
        }
        mock_request_dao.return_value = 1234567
        ret = self.client.post(TestApiLogger.LOG_PATH_URL, data, content_type='text/plain')
        mock_parse_log.assert_called_once_with(data)
        mock_request_dao.assert_called_once_with(mock_parse_log.return_value)
        self.assertIsNotNone(ret)
        self.assertIsInstance(ret.data, dict)
        self.assertEqual(ret.data, {'result': mock_request_dao.return_value})

    @patch.object(RequestsDao, 'insert')
    @patch.object(BVParser, 'parse_log')
    def test_post_FE_content_text_plain(self, mock_parse_log, mock_request_dao):
        """ Testing FE data in text plain
        """
        data = '2013/05/17T02:10:25.335 2013/05/17T02:10:25.548 Microsoft 1e246bb8-1162-46a2-93af-1da64ca9e3cb FE ' \
               'FrontendTrustedPartner 9/18297 21407 INFOSTATS 500 [{"exceptionId":' \
               '"SVR1007","exceptionText":"Server Error in Request Processing, retry is allowed: Error sending post ' \
               'request to http://172.18.174.55:18047/notifications/paymentcallback.Error message: ' \
               'javax.ws.rs.client.ClientException: org.apache.cxf.interceptor.Fault: Could not send Message."}]'
        mock_parse_log.return_value = {
            "_id": {"$oid": "5280abe0fdc74475f9581e58"},
            "origin": "FE",
            "body": "[\"GET /provisioning/v1/applications?serviceId=1&fields=appId&appApi.keyword=wo15671 HTTP/1.1\"]",
            "http_request": {
                "url": "provisioning/v1/applications",
                "api": "provisioning",
                "method": "GET"
            },
            "responseDate": {"date": 1382323724329},
            "api": "provisioning",
            "app": "FrontendBasic",
            "domain": "Bluevia",
            "host": "nsdpgwfe1",
            "serviceId": "1",
            "requestDate": {"date": 1382323724170},
            "body_request": {

            },
            "responseCode": "200",
            "appId": "40601",
            "transactionId": "0866111a-d601-42a2-9ec4-403a1391735c",
            "id": 1,
            "statType": "INFOSTATS"
        }
        mock_request_dao.return_value = 1234567
        ret = self.client.post(TestApiLogger.LOG_PATH_URL, data, content_type='text/plain')
        mock_parse_log.assert_called_once_with(data)
        mock_request_dao.assert_called_once_with(mock_parse_log.return_value)
        self.assertIsNotNone(ret)
        self.assertIsInstance(ret.data, dict)
        self.assertEqual(ret.data, {'result': mock_request_dao.return_value})

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

    @patch.object(RequestsDao, 'insert')
    def test_post_return_json_data(self, mock_request_dao):
        """ Testing Post returning json id number
        """
        data = {"data": "hello"}
        mock_request_dao.return_value = 12345678
        ret = self.apiclient.post(TestApiLogger.LOG_PATH_URL, data, format='json')
        mock_request_dao.assert_called_once_with(dict(data))
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 201)
        self.assertIsInstance(ret.data, dict)
        self.assertEqual(ret.data, {"result": 12345678})


class TestApiCollection(unittest.TestCase):
    """ API Collection class unit tests
    """
    COL_PATH_URL = reverse('collection-api')

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        del self.client

    def test_remove_log_collection_status_204(self):
        """ Testing deleting collection
        """
    @patch.object(RequestsDao, 'remove')
    def test_remove_log_collection_status_204(self, mock_request_dao):
        """ Testing calling remove collection in mongo
        """
        ret = self.client.delete(TestApiCollection.COL_PATH_URL)
        mock_request_dao.assert_called_once_with()
        self.assertIsNotNone(ret)
        self.assertEqual(ret.status_code, 204, "Correct remove status returned")
        self.assertEqual(ret.status_text, 'NO CONTENT')


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
