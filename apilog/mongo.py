from settings import MONGODB
from pymongo import MongoClient, ReadPreference
from pymongo.errors import AutoReconnect

_connection = None


class DBLogException(Exception):
    """ Own database exception
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Connection(object):
    """
    Singleton connection
    """

    def get_connection(self):
        global _connection
        dbconfig = MONGODB

        if _connection is None:
            for host in dbconfig['hosts']:
                if dbconfig['slave_ok']:
                    read_preference = ReadPreference.SECONDARY
                else:
                    read_preference = ReadPreference.PRIMARY
                try:
                    _connection = MongoClient(
                        host,
                        w=dbconfig['operation_ack'],
                        replicaset=dbconfig["replicaset"],
                        read_preference=read_preference,
                        auto_start_request=dbconfig["autostart"])
                    return _connection[dbconfig['dbname']]
                except AutoReconnect as e:
                    print "Cannot connect to '{0}' trying next host. Error: {1}".format(host, e.message)
                    _connection = None
            raise SystemError("Cannot establish connection with hosts {0}".format(dbconfig["hosts"]))
        return _connection[dbconfig['dbname']]

    def close(self):
        _connection.close()


class Dao(object):
    def __init__(self):
        if self.coll is None:
            raise NotImplementedError("{0}.coll method must defined when overriding".format(self.__class__.__name__))

        client = Connection()
        self.dbconn = client.get_connection()
        self.dbcoll = self.dbconn[self.coll]

    def _get_id_value(self):
        """Retrieve max new value of the id for DAO collection
        :param coll_name: name of the collection whose max counter has to be retrieved
        :return counter value
        """
        coll = self.dbconn['ids']
        counter_doc = coll.find_and_modify(query={'_id': self.coll},
                                           update={'$inc': {'val': 1}},
                                           upsert=True,
                                           w=1,
                                           new=True)
        return counter_doc['val']


class RequestsDao(Dao):
    coll = 'requests'

    def __init__(self, *args, **kwargs):
        super(RequestsDao, self).__init__(*args, **kwargs)

    def insert(self, doc, operation_ack=1):
        """Insert document inside collection
        :param doc: document to store to the DB
        :param operation_ack: validate operation (slower)
        :raises DuplicateKeyError with operation_ack=1
        """
        doc.pop("_id", None)
        doc["id"] = self._get_id_value()
        self.dbcoll.insert(doc, w=operation_ack)
        # Not returning objectId, just our id
        return doc['id']

    def select(self, log_id=None):
        """ Retrieve log from log_id
        :log_id: id from log to retrieve
        :raises DBLogException
        """
        if log_id:
            doc = self.dbcoll.find_one({'id': log_id})
        else:
            # Getting 50 logs
            doc = self.dbcoll.find().limit(50)

        if doc:
            return doc
        else:
            raise DBLogException("Data log does not exist")

    def remove(self):
        """Remove requests collection
        """
        self.dbcoll.drop()
