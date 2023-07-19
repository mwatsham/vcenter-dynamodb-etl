from dynamodb_vcenter_item import VcenterItem
from dynamodb_vcenter_item import DatacenterItem
from dynamodb_vcenter_item import ComputeClusterItem
from dynamodb_vcenter_item import DatastoreItem
from dynamodb_vcenter_item import NetworkItem
from dynamodb_vcenter_item import TemplateItem

#import pyvm_common
import vcenter_data


def test_item_classes():
    vc_item = VcenterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    dc_item = DatacenterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    cc_item = ComputeClusterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    ds_item = DatastoreItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    nw_item = NetworkItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    tp_item = TemplateItem("part_key", "sort_key", "item_label", {"attribute": "value"})

    for obj in [vc_item,dc_item,cc_item,ds_item,nw_item,tp_item]:
        print(obj.retrieve_item())

if __name__ == '__main__':
    """
    vc_connect_args = {
        'username': os.environ.get('USERNAME'),
        'password': os.environ.get('PASSWORD'),
        'host': os.environ.get('SERVER')
    }
    aws_connect_args = {
        'role_arn': os.environ.get('AWS_ROLE_ARN'),
        'access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
        'secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'region': os.environ.get('AWS_DEFAULT_REGION')
    }
    vcenter_name = os.environ.get('VC_NAME')
    content_lib_name = os.environ.get('CONTENT_LIB_NAME')

    vc_si = pyvm_common.service_instance_connect(**vc_connect_args)
    """

    vc_item = VcenterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    dc_item = DatacenterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    cc_item = ComputeClusterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    ds_item = DatastoreItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    nw_item = NetworkItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    tp_item = TemplateItem("part_key", "sort_key", "item_label", {"attribute": "value"})


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

    vc_root.traverse()

