import datetime
from datetime import timezone
from common import pyvm_common
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def get_vc_rest_api_content_libraries(lib_name, **kwargs):
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    # Set up the REST API endpoint URLs
    base_url = f'https://{ kwargs.get("vc_fqdn")}/rest'
    auth_url = f'{base_url}/com/vmware/cis/session'
    lib_url = f'{base_url}/com/vmware/content/library'
    lib_item_url = f'{base_url}/com/vmware/content/library/item'
    verify_ssl = False
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}

    # Authenticate to the vSphere REST API
    session = requests.Session()
    session.auth = (kwargs.get('vc_username'), kwargs.get('vc_password'))
    session.post(auth_url, headers=headers, verify=verify_ssl)

    # Retrieve a list of all content libraries
    response = session.get(lib_url, headers=headers, verify=verify_ssl)
    response.raise_for_status()

    # Extracted IDs for available Content Libraries
    content_lib_ids = response.json()['value']
    libs = []

    # Loop through available Content Library IDs to extract
    # library items from named Content Library in 'lib_name'
    for content_lib_id in content_lib_ids:
        tmp_lib_url = lib_url + f'/id:{content_lib_id}'
        response = session.get(tmp_lib_url, headers=headers, verify=verify_ssl)
        lib = response.json()['value']
        if lib['name'] == lib_name:
            tmp_lib_items_url = lib_item_url + f'?library_id={lib["id"]}'
            response = session.get(tmp_lib_items_url, headers=headers, verify=verify_ssl)
            lib_items = response.json()['value']
            for item in lib_items:
                tmp_lib_item_url = lib_item_url + f'/id:{item}'
                response = session.get(tmp_lib_item_url, headers=headers, verify=verify_ssl)
                lib_item = response.json()['value']
                libs.append(lib_item)

    # Logout of the vSphere REST API
    session.delete(auth_url, verify=verify_ssl)

    return libs


class TreeNode:
    def __init__(self, data_object, node_type):
        self.data = data_object  # data
        self.node_type = node_type
        self.children = []  # references to other nodes

    def add_child(self, child_node):
        # creates parent-child relationship
        self.children.append(child_node)

    def traverse(self):
        nodes = []
        # moves through each node referenced from self downwards
        nodes_to_visit = [self]
        while len(nodes_to_visit) > 0:
            current_node = nodes_to_visit.pop()
            nodes.append(current_node)
            nodes_to_visit += current_node.children
        return nodes


class VsphereEntity:
    def __init__(self, name: str = "", parent_name: str = "", label: str = "", attributes=None):
        self.name = name
        self.parent_name = parent_name
        self.label = label
        self.attributes = attributes


class VcenterEntity(VsphereEntity):
    def __init__(self, entity_attributes=None):
        # Getting the current date and time in UTC
        dt = datetime.datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        utc_timestamp = utc_time.timestamp()

        name = entity_attributes.get('vc_name')
        parent_name = name
        label = name
        attributes = {
            'VcFqdn': entity_attributes.get('VcFqdn'),
            'LastUpdatedUtc': utc_timestamp
        }

        super().__init__(name, parent_name, label, attributes)


class DatacenterEntity(VsphereEntity):
    def __init__(self, parent_name, entity_attributes=None):
        name = entity_attributes.get('name')
        label = name

        super().__init__(name, parent_name, label)


class ComputeClusterEntity(VsphereEntity):
    def __init__(self, parent_name, entity_attributes=None):
        name = entity_attributes.get('name')
        label = name
        attributes = {
            'CpuCapacityMHz': entity_attributes.get('CpuCapacityMHz'),
            'CpuFreeMHz': entity_attributes.get('CpuFreeMHz'),
            'MemoryCapacityMB': entity_attributes.get('MemoryCapacityMB'),
            'MemoryFreeMB': entity_attributes.get('MemoryFreeMB')
        }

        super().__init__(name, parent_name, label, attributes)


class NetworkEntity(VsphereEntity):
    def __init__(self, parent_name, entity_attributes=None):
        name = entity_attributes.get('name')
        label = entity_attributes.get('label')

        super().__init__(name, parent_name, label)


class DatastoreEntity(VsphereEntity):
    def __init__(self, parent_name, entity_attributes=None):
        name = entity_attributes.get('name')
        label = name
        attributes = {
            'StorageCapacityGB': entity_attributes.get('StorageCapacityGB'),
            'StorageFreeGB': entity_attributes.get('StorageFreeGB')
        }

        super().__init__(name, parent_name, label, attributes)


class TemplateEntity(VsphereEntity):
    def __init__(self, parent_name, entity_attributes=None):
        name = entity_attributes.get('name')
        label = name

        super().__init__(name, parent_name, label)


class VcServiceInstance:
    def __init__(self, **kwargs):
        self.vc_name = kwargs.get('vc_name')
        self.vc_connect_args = {
            'host': kwargs.get('vc_fqdn'),
            'username': kwargs.get('vc_username'),
            'password': kwargs.get('vc_password')
        }

        # Establish connection with vCenter instance
        self.service_instance = pyvm_common.service_instance_connect(**self.vc_connect_args)

        # Retrieve all vCenter ServiceInstance Content level objects
        self.service_content = self.service_instance.RetrieveContent()

    def get_datacenters(self):
        if 'Datacenter' in self.service_content.rootFolder.childType:
            datacenters = self.service_content.rootFolder.childEntity
        else:
            datacenters = []

        return datacenters

    # Need to flatten computer clusters as they could be organised in a nested
    # folder structure. We're only interested in finding out which compute
    # clusters belong to a particular Datacenter.
    # NB: We ignore standalone ESXi hosts
    def _process_compute_clusters(self, compute_object):
        computer_cluster_objs = []

        for compute_resource in compute_object:
            if hasattr(compute_resource, 'childEntity'):
                # Check for empty Compute resource
                if compute_resource.childEntity:
                    computer_cluster_objs + self._process_compute_clusters(compute_resource.childEntity)
            else:
                # Ignore standalone ESXi hosts
                if len(compute_resource.host) > 1:
                    computer_cluster_objs.append(compute_resource)

        return computer_cluster_objs

    def get_compute_clusters(self, dc_object):
        compute_resource_object = dc_object.hostFolder.childEntity
        return self._process_compute_clusters(compute_resource_object)











