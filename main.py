from dynamodb_vcenter_item import VcenterItem
from dynamodb_vcenter_item import DatacenterItem
from dynamodb_vcenter_item import ComputeClusterItem
from dynamodb_vcenter_item import DatastoreItem
from dynamodb_vcenter_item import NetworkItem
from dynamodb_vcenter_item import TemplateItem


def test_classes():
    vc_item = VcenterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    dc_item = DatacenterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    cc_item = ComputeClusterItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    ds_item = DatastoreItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    nw_item = NetworkItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    tp_item = TemplateItem("part_key", "sort_key", "item_label", {"attribute": "value"})

    for obj in [vc_item,dc_item,cc_item,ds_item,nw_item,tp_item]:
        print(obj.retrieve_item())

if __name__ == '__main__':
    test_classes()
