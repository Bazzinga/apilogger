import logging
import logging.config
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import BaseParser, JSONParser
from rest_framework.views import APIView

from api.logparser import BVParser, LoggerException
from apilog.mongo import RequestsDao, DBLogException
from pymongo.errors import DuplicateKeyError
from apilog import settings


logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('apilog')
dao = RequestsDao()


def _prepare_result(result):
    """ Prepare result dictionary
    """
    return {"result": result}


class PlainTextParser(BaseParser):
    """ Plain text parser
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """ Simply return a string representing the body of the request.
        """
        return stream.read()


class Logger(APIView):
    """ Get and post all log information
    """
    # Indicating which content-types are accepted in logger api
    parser_classes = (JSONParser, PlainTextParser,)

    def get(self, request, format=None):
        """ Return all logs in a list
        """
        return Response(_prepare_result([doc for doc in dao.select()]), status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """ Post a list of logs
        :request data posted to store in data base
        """
        data = request.DATA
        if data:
            try:
                if isinstance(data, dict):
                    # direct insert in db
                    return Response(_prepare_result(dao.insert(data)), status=status.HTTP_201_CREATED)
                else:
                    parser = BVParser()
                    try:
                        return Response(_prepare_result(dao.insert(parser.parse_log(data))),
                                        status=status.HTTP_201_CREATED)
                    except LoggerException as e:
                        logger.error("POST error: {}".format(e.value))
                        return Response(e.value, status=status.HTTP_400_BAD_REQUEST)
            except DuplicateKeyError as dex:
                logger.error("Duplicate key error {}".format(dex.message))
                return Response(dex.message, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error("Received data is empty")
            return Response("Received data is empty", status=status.HTTP_400_BAD_REQUEST)


class LoggerDetail(APIView):
    """ Logger detail api
    """
    # Indicating which content-types are accepted in logger api
    parser_classes = (JSONParser, PlainTextParser,)

    def delete(self, request, log_id, format=None):
        """ Delete log
        :log_id: log id identifier
        """
        result = dao.delete_doc(log_id)
        if result['n'] > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logger.error("Unknown log {} to delete".format(log_id))
            return Response("Unknown log {} to delete".format(log_id), status=status.HTTP_404_NOT_FOUND)

    def get(self, request, log_id, format=None):
        """ Retrieve log information from received id
        :log_id: id from log to be retrieved
        """
        try:
            return Response(_prepare_result(dao.select(log_id)), status=status.HTTP_200_OK)
        except DBLogException as dbex:
            logger.error("DB error: {}".format(dbex.value))
            return Response(dbex.value, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, log_id, format=None):
        """ Update log data in database from log_id
        """
        data = request.DATA
        if data:
            result = dao.update_doc(log_id, data)
            if result['updatedExisting']:
                return Response("Log {} updated correctly".format(log_id), status=status.HTTP_200_OK)
            else:
                logger.error("Unknown log {} to update".format(log_id))
                return Response("Unknown log {} to update".format(log_id), status=status.HTTP_404_NOT_FOUND)
        else:
            logger.error("Received data is empty")
            return Response("Received data is empty", status=status.HTTP_400_BAD_REQUEST)


class Collection(APIView):
    """ Database collection api
    """
    def delete(self, request, *args, **kwargs):
        """ Remove default log collection
        """
        dao.remove()
        return Response(status=status.HTTP_204_NO_CONTENT)
