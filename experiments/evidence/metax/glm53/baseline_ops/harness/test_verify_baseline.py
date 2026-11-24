import copy
import unittest
from verify_baseline import normalized_containers


class ContainerComparisonTests(unittest.TestCase):
    def test_mount_order_is_not_a_configuration_change(self):
        before = {'x': {'Id': 'same', 'Mounts': [{'Destination': '/a', 'RW': False}, {'Destination': '/b', 'RW': True}]}}
        after = copy.deepcopy(before)
        after['x']['Mounts'].reverse()
        self.assertEqual(normalized_containers(before), normalized_containers(after))
        self.assertEqual(before['x']['Mounts'][0]['Destination'], '/a')

    def test_mount_permission_change_is_detected(self):
        before = {'x': {'Id': 'same', 'Mounts': [{'Destination': '/a', 'RW': False}]}}
        after = copy.deepcopy(before)
        after['x']['Mounts'][0]['RW'] = True
        self.assertNotEqual(normalized_containers(before), normalized_containers(after))


if __name__ == '__main__':
    unittest.main()
