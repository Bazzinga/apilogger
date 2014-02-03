import unittest
from apilog import mongo
from mock import patch, create_autospec
from pymongo.cursor import Cursor


class mongoTest(unittest.TestCase):
    """ Mongo db class testing
    """
    DATA = {u'text': u'My first log post!', u'author': u'Jalp', u'tags': [u'mongodb', u'python', u'pymongo']}

    def setUp(self):
        self.dao = mongo.RequestsDao()

    def tearDown(self):
        del self.dao

    def test_select_log(self):
        """ Find all data (limit 50)
        """
        with patch.object(Cursor, 'limit', return_value=mongoTest.DATA) as mock_limit:
            mock_cursor = create_autospec(Cursor, return_value=mock_limit)
            with patch.object(self.dao.dbcoll, 'find', return_value=mock_cursor):
                result = self.dao.select()
                for doc in result:
                    self.assertEqual(doc['text'], 'My first log post!')
                    self.assertEqual(doc['author'], 'Jalp')

    def test_select_by_log_id(self):
        """ Select data information
        """
        with patch.object(self.dao.dbcoll, 'find_one', return_value=mongoTest.DATA) as mock_select:
            result = self.dao.select(1)
            self.assertIsNotNone(result)
            mock_select.caassert_called_once_with(1)
            self.assertEqual(result['text'], "My first log post!")
            self.assertEqual(result['tags'][0], "mongodb")
            self.assertEqual(result['tags'][2], "pymongo")

    def test_select_empty_data(self):
        """ Selecting an empty log data
        """
        with patch.object(self.dao.dbcoll, 'find_one', return_value=None) as mock_find_one:
            with self.assertRaises(mongo.DBLogException) as exc:
                self.dao.select(1)
                mock_find_one.assert_called_once_with(1)
            ret_except = exc.exception
            self.assertEqual(ret_except.value, "Data log 1 does not exist")

    def test_insert_request_dao(self):
        """ Inserting data in mongoDB requests collection
        """
        with patch.object(self.dao, '_get_id_value', return_value=123456) as mock_id:
            with patch.object(self.dao.dbcoll, 'insert') as mock_insert:
                result = self.dao.insert(mongoTest.DATA)
                self.assertIsNotNone(result)
                self.assertEqual(result, 123456)
                mock_id.assert_called_once_with()
                mock_insert.assert_called_once_with(mongoTest.DATA, w=1)

    def test_update_request_dao(self):
        """ Update log data
        """
        with patch.object(self.dao.dbcoll, 'update', return_value={u'updatedExisting': True, u'connectionId': 462,
                                                                   u'ok': 1.0, u'err': None, u'n': 1}) as mock_update:
            result = self.dao.update_doc(1, mongoTest.DATA)
            self.assertIsNotNone(result)
            self.assertEqual(result['n'], 1)
            self.assertTrue(result['updatedExisting'])
            mock_update.assert_called_once_with({"id": 1}, mongoTest.DATA, w=1)

    def test_delete_request_dao(self):
        """ Delete log
        """
        with patch.object(self.dao.dbcoll, 'remove', return_value={u'connectionId': 479, u'ok': 1.0,
                                                                   u'err': None, u'n': 1}) as mock_remove:
            result = self.dao.delete_doc(1)
            self.assertIsNotNone(result)
            self.assertEqual(result['n'], 1)
            mock_remove.assert_called_once_with({"id": 1}, w=1)

    def test_remove_request_dao(self):
        """ Remove request collection
        """
        with patch.object(self.dao.dbcoll, 'drop') as mock_drop:
            self.dao.remove()
            mock_drop.assert_called_once_with()
