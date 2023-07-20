from dynamodb_vcenter_item import VcenterItem
from dynamodb_vcenter_item import DatacenterItem
from dynamodb_vcenter_item import ComputeClusterItem
from dynamodb_vcenter_item import DatastoreItem
from dynamodb_vcenter_item import NetworkItem
import vcenter_data
from os import environ
import re

def test_item_classes():
    vc_item = VcenterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    dc_item = DatacenterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    cc_item = ComputeClusterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    ds_item = DatastoreItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    nw_item = NetworkItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    tp_item = TemplateItem("part_key", "sort_key", "item_label", {"attribute": "value"})

    for obj in [vc_item,dc_item,cc_item,ds_item,nw_item,tp_item]:
        print(obj.retrieve_item())

def test_vcenter_data_classes():
    vc_attributes = {
        'name': "CTI3",
        'VcFqdn': "chi-cti3-vc1.ice.bskyb.com"
    }
    vc_entity = vcenter_data.VcenterEntity(vc_attributes)
    vc_root = vcenter_data.TreeNode(vc_entity, 'vcenter')

    dc_attributes = {
        'name': "Datacenter01"
    }
    dc_entity = vcenter_data.DatacenterEntity(vc_entity.name, dc_attributes)
    dc_node = vcenter_data.TreeNode(dc_entity, 'datacenter')
    vc_root.add_child(dc_node)

    cc_attributes = {
        'name': "ComputeCluster01",
        'CpuCapacityMHz': "cpu capacity",
        'CpuFreeMHz': "free cpu",
        'MemoryCapacityMB': "memory capacity",
        'MemoryFreeMB': "free memory"
    }
    cc_entity = vcenter_data.ComputeClusterEntity(dc_entity.name, cc_attributes)
    cc_node = vcenter_data.TreeNode(cc_entity, 'compute_cluster')
    dc_node.add_child(cc_node)

    nw_attributes = {
        'name': "192.168.0.1"
    }
    nw_entity = vcenter_data.NetworkEntity(cc_entity.name, nw_attributes)
    nw_node = vcenter_data.TreeNode(nw_entity, 'network')
    cc_node.add_child(nw_node)

    ds_attributes = {
        'name': "Datastore01",
        'StorageCapacityGB': 12345,
        'StorageFreeGB': 12345
    }
    ds_entity = vcenter_data.DatastoreEntity(cc_entity.name, ds_attributes)
    ds_node = vcenter_data.TreeNode(ds_entity, 'datastore')
    cc_node.add_child(ds_node)

    tp_attributes = {
        'name': "Template01"
    }
    tp_entity = vcenter_data.TemplateEntity(vc_entity.name, tp_attributes)
    tp_node = vcenter_data.TreeNode(tp_entity, 'template')
    vc_root.add_child(tp_node)

    vc_root.traverse()


def _convert_bytes_to_gb(bytes):
    result = float(bytes) / pow(1024, 3)
    return round(result, 2)


def _check_for_ipv4(test_str):
    match = re.search(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", test_str)
    return match


def main():
    vc_args = {
        'vc_name': environ.get('VC_SHORT_NAME'),
        'vc_username': environ.get('VC_USERNAME'),
        'vc_password': environ.get('VC_PASSWORD'),
        'vc_fqdn': environ.get('VC_FQDN')
    }

    """
    aws_connect_args = {
        'role_arn': environ.get('AWS_ROLE_ARN'),
        'access_key_id': environ.get('AWS_ACCESS_KEY_ID'),
        'secret_access_key': environ.get('AWS_SECRET_ACCESS_KEY'),
        'region': environ.get('AWS_DEFAULT_REGION')
    }
    """

    # Create vCenter service instance object
    vc_si_obj = vcenter_data.VcServiceInstance(**vc_args)

    # Create vCenter data entity
    vc_entity = vcenter_data.VcenterEntity({'vc_name': vc_args['vc_name'], 'VcFqdn': vc_args['vc_fqdn']})

    # Create vCenter data tree root/node
    vc_root = vcenter_data.TreeNode(vc_entity, 'vcenter')

    for datacenter in vc_si_obj.get_datacenters():
        # Create Datacenter data entity
        dc_entity = vcenter_data.DatacenterEntity(vc_entity.name, {'name': datacenter.name})

        # Create Datacenter data tree node
        dc_node = vcenter_data.TreeNode(dc_entity, 'datacenter')

        # Add Datacenter tree node as child of vCenter tree root
        vc_root.add_child(dc_node)

        dc_compute_cluster_objs = vc_si_obj.get_compute_clusters(datacenter)

        for compute_cluster in dc_compute_cluster_objs:
            compute_usage = compute_cluster.GetResourceUsage()
            cc_attributes = {
                'name': compute_cluster.name,
                'CpuCapacityMHz': compute_usage.cpuCapacityMHz,
                'CpuFreeMHz': compute_usage.cpuCapacityMHz - compute_usage.cpuUsedMHz,
                'MemoryCapacityMB': compute_usage.memCapacityMB,
                'MemoryFreeMB': compute_usage.memCapacityMB - compute_usage.memUsedMB
            }
            cc_entity = vcenter_data.ComputeClusterEntity(dc_entity.name, cc_attributes)
            cc_node = vcenter_data.TreeNode(cc_entity, 'compute_cluster')
            dc_node.add_child(cc_node)

            # Extract Datastores in compute cluster
            for datastore in compute_cluster.datastore:
                ds_attributes = {
                    'name': datastore.name,
                    'StorageCapacityGB': _convert_bytes_to_gb(datastore.summary.capacity),
                    'StorageFreeGB': _convert_bytes_to_gb(datastore.summary.freeSpace)
                }
                ds_entity = vcenter_data.DatastoreEntity(compute_cluster.name, ds_attributes)
                ds_node = vcenter_data.TreeNode(ds_entity, 'datastore')
                cc_node.add_child(ds_node)

            # Extract Networks in compute cluster
            for network in compute_cluster.network:
                contains_ipv4 = _check_for_ipv4(network.name)
                if contains_ipv4:
                    matched_ipv4 = contains_ipv4.group()
                    nw_attributes = {
                        'name': matched_ipv4,
                        'label': network.name
                    }
                    nw_entity = vcenter_data.NetworkEntity(compute_cluster.name, nw_attributes)
                    nw_node = vcenter_data.TreeNode(nw_entity, 'network')
                    cc_node.add_child(nw_node)


    # Return data tree
    vc_entities = vc_root.traverse()

    dynamodb_items = []
    for entity in vc_entities:
        if entity.node_type == 'vcenter':
            dynamodb_items.append(
                VcenterItem(entity.data.parent_name, entity.data.name, entity.data.label, entity.data.attributes)
            )
            print(entity.data.name)
        elif entity.node_type == 'datacenter':
            dynamodb_items.append(
                DatacenterItem(entity.data.parent_name, entity.data.name, entity.data.label, entity.data.attributes)
            )
        elif entity.node_type == 'compute_cluster':
            dynamodb_items.append(
                ComputeClusterItem(entity.data.parent_name, entity.data.name, entity.data.label, entity.data.attributes)
            )
        elif entity.node_type == 'datastore':
            dynamodb_items.append(
                DatastoreItem(entity.data.parent_name, entity.data.name, entity.data.label, entity.data.attributes)
            )
        elif entity.node_type == 'network':
            dynamodb_items.append(
                NetworkItem(entity.data.parent_name, entity.data.name, entity.data.label, entity.data.attributes)
            )

    for item in dynamodb_items:
        print(item.retrieve_item())

if __name__ == '__main__':

    #test_item_classes()
    #test_vcenter_data_classes()

    main()




