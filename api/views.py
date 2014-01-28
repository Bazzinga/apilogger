from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import BaseParser, JSONParser
from rest_framework.views import APIView

from api.logparser import BVParser, LoggerException
from apilog.mongo import RequestsDao
from pymongo.errors import DuplicateKeyError

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
    """ Logger api
    """
    # Indicating which content-types are accepted in logger api
    parser_classes = (JSONParser, PlainTextParser,)

    def get(self, request, *args, **kwargs):
        """ Retrieve log information from received id
        """
        log_id = request.QUERY_PARAMS.get('id', None)
        if log_id:
            return Response(_prepare_result(dao.select(log_id)), status=status.HTTP_200_OK)
        else:
            return Response("Unknown log ID", status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        """ Store log data in database
        """
        data = request.DATA
        if data:
            parser = BVParser()
            try:
                if isinstance(data, dict):
                    return Response(_prepare_result(dao.insert(data)), status=status.HTTP_201_CREATED)
                else:
                    try:
                        return Response(_prepare_result(dao.insert(parser.parse_log(data))),
                                        status=status.HTTP_201_CREATED)
                    except LoggerException as e:
                        return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
            except DuplicateKeyError as dex:
                return Response(dex.message, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Data received is empty", status=status.HTTP_400_BAD_REQUEST)


class Collection(APIView):
    """ Database collection api
    """
    def delete(self, request, *args, **kwargs):
        """ Remove default log collection
        """
        dao.remove()
        return Response(status=status.HTTP_204_NO_CONTENT)
