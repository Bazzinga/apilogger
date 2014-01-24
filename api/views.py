from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import BaseParser, JSONParser
from rest_framework.views import APIView

from api.logparser import BVParser, LoggerException


class PlainTextParser(BaseParser):
    """ Plain text parser.
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """Simply return a string representing the body of the request.
        """
        return stream.read()


class Logger(APIView):
    """ Logger api
    """
    # Indicating which content-types are accepted in logger api
    parser_classes = (JSONParser, PlainTextParser,)

    def post(self, request, *args, **kwargs):
        """ Save log data in database
        """

        data = request.DATA
        if data:
            parser = BVParser()
            if isinstance(data, dict):
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                try:
                    return Response(parser.parse_log(data), status=status.HTTP_201_CREATED)
                except LoggerException as e:
                    return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Data received is empty", status=status.HTTP_400_BAD_REQUEST)


class Collection(APIView):
    """ Database collection api
    """
    def delete(self, request, *args, **kwargs):
        """ Remove default log collection
        """
        return Response(status=status.HTTP_204_NO_CONTENT)
