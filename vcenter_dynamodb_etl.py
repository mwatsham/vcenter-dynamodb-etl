from common.dynamodb_vcenter_item import VcenterItem
from common.dynamodb_vcenter_item import DatacenterItem
from common.dynamodb_vcenter_item import ComputeClusterItem
from common.dynamodb_vcenter_item import DatastoreItem
from common.dynamodb_vcenter_item import NetworkItem
from common.dynamodb_vcenter_item import TemplateItem
from common import vcenter_data
from common import aws_common
from os import getenv
import re
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import json
from decimal import Decimal


def _convert_bytes_to_gb(bytes):
    result = float(bytes) / pow(1024, 3)
    return round(result, 2)


def _check_for_ipv4(test_str):
    match = re.search(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", test_str)
    return match


def extract_vc_data(**vc_args):
    vc_args = {
        'vc_name': vc_args.get('vc_name'),
        'vc_username': vc_args.get('vc_username'),
        'vc_password': vc_args.get('vc_password'),
        'vc_fqdn': vc_args.get('vc_fqdn'),
        'vc_content_lib': vc_args.get('vc_content_lib')
    }

    # Create vCenter service instance object
    vc_si_obj = vcenter_data.VcServiceInstance(**vc_args)

    # Create vCenter data entity
    vc_entity = vcenter_data.VcenterEntity({'vc_name': vc_args['vc_name'], 'VcFqdn': vc_args['vc_fqdn']})

    # Create vCenter data tree root/node
    vc_root = vcenter_data.TreeNode(vc_entity, 'vcenter')

    # Retrieve VM Templates from Content Library
    vm_templates = vcenter_data.get_vc_rest_api_content_libraries(vc_args.get('vc_content_lib'), **vc_args)

    # Loop through retrieved Templates and add items to vCenter data tree as child items of vCenter node
    for vm_template in vm_templates:
        # Create Template data entity
        tp_entity = vcenter_data.TemplateEntity(vc_entity.name, {'name': vm_template.get('name')})

        # Create Template tree node
        tp_node = vcenter_data.TreeNode(tp_entity, 'template')

        # Add Template tree node as child of vCenter tree root
        vc_root.add_child(tp_node)

    # Loop vCenter Datacenters and add items to vCenter data tree as child items of vCenter node
    for datacenter in vc_si_obj.get_datacenters():
        # Create Datacenter data entity
        dc_entity = vcenter_data.DatacenterEntity(vc_entity.name, {'name': datacenter.name})

        # Create Datacenter data tree node
        dc_node = vcenter_data.TreeNode(dc_entity, 'datacenter')

        # Add Datacenter tree node as child of vCenter tree root
        vc_root.add_child(dc_node)

        # Retrieve Compute clusters for Datacenter
        dc_compute_cluster_objs = vc_si_obj.get_compute_clusters(datacenter)

        # Loop through Compute clusters and extract cluster data and
        # data for child Datastores/Networks
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
    return vc_root.traverse()


def transform_vc_data(vc_entities):
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
        elif entity.node_type == 'template':
            dynamodb_items.append(
                TemplateItem(entity.data.parent_name, entity.data.name, entity.data.label, entity.data.attributes)
            )

    return dynamodb_items


def load_vc_data(db_items, **aws_args):
    aws_connect_args = {
        'role_arn': aws_args.get('aws_role_arn'),
        'access_key_id': aws_args.get('aws_access_key_id'),
        'secret_access_key': aws_args.get('aws_secret_access_key'),
        'region': aws_args.get('aws_region')
    }

    aws_session = aws_common.aws_session(**aws_connect_args)

    # Retrieve DynamoDB Resource
    dynamodb = aws_session.dynamodb_resource()

    table = dynamodb.Table(aws_args.get('dynamodb_table_name'))

    # "overwrite_by_pkeys=['PK', 'SK']" bypasses no duplication limitation of single batch write request
    # 'An error occurred (ValidationException) when calling the BatchWriteItem operation: Provided list of item
    # keys contains duplicates'
    with table.batch_writer(overwrite_by_pkeys=['PK', 'SK']) as batch:
        for db_item in db_items:
            # Following line deals with 'TypeError: Float types are not supported. Use Decimal types instead.'
            db_item = json.loads(json.dumps(db_item.retrieve_item()), parse_float=Decimal)
            batch.put_item(Item=db_item)


def _parse_args():
    main_parser = ArgumentParser(
        prog='vcenter_dynamodb_etl',
        description="Extract-Transform-Load vCenter data to DynamoDB table.",
        formatter_class=ArgumentDefaultsHelpFormatter)

    main_parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        action="store_true"
    )

    subparsers = main_parser.add_subparsers(
        dest="sub_command"
    )

    # NB: the positional arguments will be optional due to the nargs='?' setting, which allows the script to use
    # the environment variables as default values if no positional arguments are provided.
    output_only = subparsers.add_parser('output_only', help='output_only --help')
    output_only.add_argument(
        "vc_name",
        help="Short name for vCenter instance",
        type=str,
        nargs='?',
        default=getenv('VC_SHORT_NAME')
    )
    output_only.add_argument(
        "vc_fqdn",
        help="FQDN for vCenter instance",
        type=str,
        nargs='?',
        default=getenv('VC_FQDN')
    )
    output_only.add_argument(
        "vc_username",
        help="Username to access vCenter instance",
        type=str,
        nargs='?',
        default=getenv('VC_USERNAME')
    )
    output_only.add_argument(
        "vc_password",
        help="Password for user to access vCenter instance",
        type=str,
        nargs='?',
        default=getenv('VC_PASSWORD')
    )
    output_only.add_argument(
        "vc_content_lib",
        help="vCenter Content Library name storing VM Templates.",
        type=str,
        nargs='?',
        default=getenv('VC_CONTENT_LIB')
    )

    output_load = subparsers.add_parser('load_dynamodb', help='load_dynamodb --help')
    output_load.add_argument(
        "vc_name",
        help="Short name for vCenter instance",
        type=str,
        nargs='?',
        default=getenv('VC_SHORT_NAME')
    )
    output_load.add_argument(
        "vc_fqdn",
        help="FQDN for vCenter instance",
        type=str,
        nargs='?',
        default=getenv('VC_FQDN')
    )
    output_load.add_argument(
        "vc_username",
        help="Username to access vCenter instance",
        type=str,
        nargs='?',
        default=getenv('VC_USERNAME')
    )
    output_load.add_argument(
        "vc_password",
        help="Password for user to access vCenter instance",
        type=str,
        nargs='?',
        default=getenv('VC_PASSWORD')
    )
    output_load.add_argument(
        'aws_access_key_id',
        type=str,
        nargs='?',
        help="AWS account access key id.",
        default=getenv('AWS_ACCESS_KEY_ID')
    )
    output_load.add_argument(
        'aws_secret_access_key',
        type=str,
        nargs='?',
        help="AWS account secret access key.",
        default=getenv('AWS_SECRET_ACCESS_KEY')
    )
    output_load.add_argument(
        'aws_role_arn',
        type=str,
        nargs='?',
        help="AWS Role.",
        default=getenv('AWS_ROLE_ARN')
    )
    output_load.add_argument(
        'aws_region_name',
        type=str,
        nargs='?',
        help="AWS Region.",
        default=getenv('AWS_DEFAULT_REGION')
    )
    output_load.add_argument(
        'dynamodb_table_name',
        type=str,
        nargs='?',
        help="AWS DynamoDB table name.",
        default=getenv('AWS_DYNAMODB_TABLE')
    )
    output_load.add_argument(
        "vc_content_lib",
        help="vCenter Content Library name for location of VM Templates.",
        type=str,
        nargs='?',
        default=getenv('VC_CONTENT_LIB')
    )

    return main_parser.parse_args()


if __name__ == '__main__':
    args = vars(_parse_args())

    if args['sub_command'] == 'output_only':
        vc_data = extract_vc_data(**args)
        for item in transform_vc_data(vc_data):
            print(item.retrieve_item())
    elif args['sub_command'] == 'load_dynamodb':
        vc_data = extract_vc_data(**args)
        db_items = transform_vc_data(vc_data)
        for item in db_items:
            print(item.retrieve_item())
        load_vc_data(db_items, **args)
