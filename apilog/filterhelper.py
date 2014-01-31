import uuid
import threading
import logging

local = threading.local()


class AddMachineFilter(logging.Filter):
    def _generate_id(self):
        """Generates an id"""
        id = uuid.uuid4().hex
        id = '{0}-{1}-{2}-{3}-{4}{5}'.format(id[:7], id[8:12], id[13:17], id[17:21], id[22:], id[0:2])
        return id

    def filter(self, record):
        """Filter callback which modifies current record providing extra info"""
        if 'paramiko' in record.name:
            return False
        record.machine = getattr(local, 'machine', 'localhost')
        record.request_id = self._generate_id()
        return True
