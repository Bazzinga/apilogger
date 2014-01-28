import re
import json
import base64
#import logging
#import logging.config
import dateutil.parser
#from logs import config


#logging.config.dictConfig(config.LOGGING)
#logger = logging.getLogger('bvapilog')


class LoggerException(Exception):
    """ Logger exception
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BVParser(object):
    SUPPORTED_APIS = ['Payment', 'payment', 'NeoPayment', 'MobileId']
    """List of fields with interesting info"""
    INTERESTING_FIELDS = [
        'partnerName',
        'text',
        'status',
        'MCCMNC',
        'user',
        'msisdn',
        'targetURL',
        'shortCode',
        'keyword',
        'userIdentifier',
        'taxAmount',
        'currency',
        'totalAmount',
        'merchantId',
        'productId',
        'paymentMethodType',
        'exceptionId',
        'exceptionText']

    def _dict_depth(self, d, keys, field_list):
        """Recursively find a key in dict
        :param d:
        :param key:
        :return:
        """
        for key in keys:
            if key in d:
                field_list[key] = d[key]

        for k, v in d.items():
            if isinstance(v, dict):
                self._dict_depth(v, keys, field_list)

    def _match_api(self, body_json):
        """Matches one of the apis
        :param body_json:
        :return:
        """
        for api in BVParser.SUPPORTED_APIS:
            if body_json.get(api, None):
                return api
        return None

    def date_to_ts(self, date):
        date = dateutil.parser.parse(date)
        return date

    def parse_log(self, oneLog):
        """Parses the log
        :param oneLog:
        :return:
        """
        line_part_regexp = re.compile(r'(?P<start>[0-9/:\.T]+)[ ]+(?P<end>[0-9/:\.T]+).*(?P<statType>INFOSTATS).*')

        log_regexp = re.compile(
            r'(?P<requestDate>[0-9/:\.T]*)[ ]+(?P<responseDate>[0-9/:\.T]*)[ ]+(?P<domain>[0-9a-zA-Z]*)[ ]'
            r'+(?P<transactionId>[0-9a-z\-]*)[ ]'
            r'+(?P<origin>[A-Z]{2})[ ]+(?P<app>[\w]+)[ ]+(?P<serviceId>[0-9]*)/(?P<appId>[0-9]*)[\w]*[ ]'
            r'+(?P<ob>[0-9]*)[ ]+'
            r'(?P<statType>INFOSTATS)[ ]+(?P<responseCode>[0-9]{3})([ ]+(?P<body>.*))*')
        body_regexp = re.compile(r'[\"|\[]*(?P<method>[A-Z]+)[ ]+/(?P<url>(?P<api>[\w]+)/[\w|/]+)')

        # extract only fields
        infostats_match = line_part_regexp.match(oneLog)

        if infostats_match and len(infostats_match.groupdict()) > 0:
            expr_match = log_regexp.match(oneLog)
            if expr_match and len(expr_match.groupdict()) > 0:
                log_info = expr_match.groupdict()

                # try to parse simple fields
                body = log_info.get("body", "{}") or "{}"
                body_json = json.loads(body)

                api = ""
                http_request = {}
                body_request = {}

                # extract metadata from body
                #backend case
                if len(body_json) > 0 and isinstance(body_json[0], dict):
                    api = self._match_api(body_json[0])
                    self._dict_depth(body_json[0], BVParser.INTERESTING_FIELDS, body_request)
                    log_info["body"] = body_json
                    if api and api.lower() == 'mobileid':
                        msisdn = body_request.get('msisdn', "")
                        msisdn = base64.b64decode(msisdn)
                        #body_request['msisdn'] = self.descypher.decrypt(msisdn).strip('\x04') #Commented
                # frontend case
                elif isinstance(log_info["body"], str) or isinstance(log_info["body"], unicode):
                    try:
                        body_match = body_regexp.match(log_info["body"])
                        http_request = body_match.groupdict()
                        api = http_request["api"]
                    except Exception, e:
                        #logger.error('Error processing log: {0} -- {1}'.format(log_info, e))
                        raise LoggerException("Error processing received log")

                log_info["api"] = api.lower() if api else ""
                log_info["http_request"] = http_request
                log_info["body_request"] = body_request
                log_info["requestDate"] = self.date_to_ts(log_info["requestDate"])
                log_info["responseDate"] = self.date_to_ts(log_info["responseDate"])
                if 'exceptionId' in body_request:
                    log_info['exceptionId'] = body_request['exceptionId']

                #logger.info('Processed data: {0}'.format(log_info))
                return log_info
            else:
                #logger.error('Send data does not match with logger structure {0}'.format(oneLog))
                raise LoggerException("Send data does not match with log structure")
        else:
            #logger.error('Invalid data log: {0}'.format(oneLog))
            raise LoggerException("Invalid data log")
