import datetime
from datetime import timezone
class TreeNode:
    def __init__(self, data_object, node_type):
        self.data = data_object  # data
        self.node_type = node_type
        self.children = []  # references to other nodes

    def add_child(self, child_node):
        # creates parent-child relationship
        self.children.append(child_node)

    def traverse(self):
        # moves through each node referenced from self downwards
        nodes_to_visit = [self]
        while len(nodes_to_visit) > 0:
            current_node = nodes_to_visit.pop()
            print(current_node.data.__dict__)
            nodes_to_visit += current_node.children


class VsphereEntity:
    def __init__(self, name: str = "", parent_name: str = "", attributes=None):
        self.name = name
        self.parent_name = parent_name
        self.attributes = attributes


class VcenterEntity(VsphereEntity):
    def __init__(self, entity=None):
        # Getting the current date and time in UTC
        dt = datetime.datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        utc_timestamp = utc_time.timestamp()

        name = entity.get('name')
        parent_name = name
        attributes = {
            'VcFqdn': entity.get('VcFqdn'),
            'LastUpdatedUtc': utc_timestamp
        }

        super().__init__(name, parent_name, attributes)


class DatacenterEntity(VsphereEntity):
    def __init__(self, parent_name, entity=None):
        name = entity.get('name')

        super().__init__(name, parent_name)


class ComputeClusterEntity(VsphereEntity):
    def __init__(self, parent_name, entity=None):
        name = entity.get('name')
        attributes = {
            'CpuCapacityMHz': entity.get('CpuCapacityMHz'),
            'CpuFreeMHz': entity.get('CpuFreeMHz'),
            'MemoryCapacityMB': entity.get('MemoryCapacityMB'),
            'MemoryFreeMB': entity.get('MemoryFreeMB')
        }

        super().__init__(name, parent_name, attributes)


class NetworkEntity(VsphereEntity):
    def __init__(self, parent_name, entity=None):
        name = entity.get('name')

        super().__init__(name, parent_name)