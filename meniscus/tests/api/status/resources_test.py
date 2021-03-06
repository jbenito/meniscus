import unittest

import falcon
import falcon.testing as testing
from mock import MagicMock, patch

from meniscus.api.status.resources import WorkerStatusResource
from meniscus.api.status.resources import WorkersStatusResource
from meniscus.data.model.worker import Worker
from meniscus.data.model.worker import SystemInfo
from meniscus.data.model.worker import WorkerRegistration
from meniscus.openstack.common import jsonutils


def suite():
    suite = unittest.TestSuite()
    suite.addTest(WhenTestingWorkerUpdateOnPut())

    return suite


class WhenTestingWorkerUpdateOnPut(testing.TestBase):
    def before(self):
        self.status = 'online'
        self.system_info = SystemInfo().format()
        self.worker_status = {
            'worker_status': {
                'system_info': self.system_info,
                'status': self.status
            }
        }

        self.bad_status = 'bad_status'
        self.bad_system_info = SystemInfo()
        self.bad_worker_status = {
            'worker_status': {
                'system_info': self.system_info,
                'status': self.bad_status
            }
        }

        self.req = MagicMock()
        self.resp = MagicMock()
        self.registration = WorkerRegistration('worker').format()
        self.worker_dict = Worker(**self.registration).format()
        self.worker_not_found = None
        self.db_handler = MagicMock()
        self.resource = WorkerStatusResource(self.db_handler)
        self.worker_id = '51375fc4eea50d53066292b6'
        self.test_route = '/v1/worker/{worker_id}/status'
        self.api.add_route(self.test_route, self.resource)

    def test_returns_400_body_validation(self):
        self.db_handler.find_one.return_value = self.worker_dict
        self.simulate_request(
            self.test_route,
            method='PUT',
            headers={'content-type': 'application/json'},
            body=jsonutils.dumps(self.bad_worker_status))
        self.assertEqual(falcon.HTTP_400, self.srmock.status)

    def test_raises_worker_not_found(self):
        self.db_handler.find_one.return_value = self.worker_not_found
        self.simulate_request(
            self.test_route,
            method='PUT',
            headers={'content-type': 'application/json'},
            body=jsonutils.dumps(self.worker_status))
        self.assertEqual(falcon.HTTP_404, self.srmock.status)

    def test_returns_400_bad_worker_status(self):
        self.db_handler.find_one.return_value = self.worker_dict
        self.simulate_request(
            self.test_route,
            method='PUT',
            headers={'content-type': 'application/json'},
            body=jsonutils.dumps(self.bad_worker_status))
        self.assertEqual(falcon.HTTP_400, self.srmock.status)

    def test_returns_200_worker_status(self):
        self.db_handler.find_one.return_value = self.worker_dict
        self.simulate_request(
            self.test_route,
            method='PUT',
            headers={'content-type': 'application/json'},
            body=jsonutils.dumps(self.worker_status))
        self.assertEqual(falcon.HTTP_200, self.srmock.status)


class WhenTestingWorkersStatus(unittest.TestCase):
    def setUp(self):
        self.req = MagicMock()
        self.resp = MagicMock()
        self.db_handler = MagicMock()
        self.resource = WorkersStatusResource(self.db_handler)
        self.registration = WorkerRegistration('worker').format()
        self.worker = Worker(**self.registration)
        self.worker_dict = Worker(**self.registration).format()

    def test_returns_200_on_get(self):
        self.db_handler.find.return_value = [self.worker_dict]
        self.resource.on_get(self.req, self.resp)
        self.assertEquals(self.resp.status, falcon.HTTP_200)
        resp = jsonutils.loads(self.resp.body)
        status = resp['status'][0]

        for key in resp.keys():
            self.assertTrue(key in self.worker.get_status().keys())


class WhenTestingWorkerStatus(unittest.TestCase):
    def setUp(self):
        self.req = MagicMock()
        self.resp = MagicMock()
        self.db_handler = MagicMock()
        self.resource = WorkerStatusResource(self.db_handler)
        self.registration = WorkerRegistration('worker').format()
        self.worker = Worker(**self.registration)
        self.worker_dict = Worker(**self.registration).format()
        self.worker_id = '51375fc4eea50d53066292b6'
        self.worker_not_found = None

    def test_raises_worker_not_found(self):
        self.db_handler.find_one.return_value = self.worker_not_found
        with self.assertRaises(falcon.HTTPError):
            self.resource.on_get(self.req, self.resp, self.worker_id)

    def test_returns_200_on_get(self):
        self.db_handler.find_one.return_value = self.worker_dict
        self.resource.on_get(self.req, self.resp, self.worker_id)
        self.assertEquals(self.resp.status, falcon.HTTP_200)
        resp = jsonutils.loads(self.resp.body)
        status = resp['status']

        for key in resp.keys():
            self.assertTrue(key in self.worker.get_status().keys())


if __name__ == '__main__':
    unittest.main()
