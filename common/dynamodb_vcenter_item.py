"""
Parent class: TableItem
Common DynamoDB item attributes...
 - 'PK' - Partition Key
 - 'SK' - Sort Key
 - 'ItemType' - item type i.e. vcenter, datacenter, compute_cluster, etc
 - 'Label' - Name of item extracted from vCenter
 - 'GSIxPK' - Secondary Index
Accepts:
  - 'primary_key' - dict
  - 'secondary_index' - dict
  - 'item_type' - string
  - 'item_label' - string
  - 'attributes' - dict
"""
class TableItem:
    def __init__(self, primary_key=None, secondary_index=None, item_type: str = "", item_label: str = "", attributes=None):
        if primary_key is None:
            self.primary_key = {}
        else:
            self.primary_key = primary_key
        if secondary_index is None:
            self.secondary_index = {}
        else:
            self.secondary_index = secondary_index
        if attributes is None:
            self.attributes = {}
        else:
            self.attributes = attributes

        self.item = {}
        self.item.update(self.primary_key)
        self.item.update(self.secondary_index)
        self.item['ItemType'] = item_type
        self.item['Label'] = item_label
        self.item.update(self.attributes)

    def retrieve_item(self):
        return self.item


"""
Child class: VcenterItem(TableItem)
Accepts:
  - 'partition_key' - string
  - 'sort_key' - string
  - 'item_label' - string
  - 'attributes' - dict
Constants:
  - self.partition_key_prefix = "VC#"
  - self.sort_key_prefix = "VC#"
  - self.type = "vcenter"
  - self.secondary_index_prefix = "GSI1"
Item structure:
    {
        'PK': 'VC#PART_KEY', 
        'SK': 'VC#SORT_KEY', 
        'GSI1PK': 'VC#SORT_KEY', 
        'ItemType': 'vcenter', 
        'Label': 'item_label', 
        'attribute': 'value'
    }
"""
class VcenterItem(TableItem):
    def __init__(self, partition_key: str = "", sort_key: str = "", item_label: str = "", attributes=None):
        self.partition_key_prefix = "VC#"
        self.sort_key_prefix = "VC#"
        self.type = "vcenter"
        self.secondary_index_prefix = "GSI1"
        self.partition_key = self.partition_key_prefix + str.upper(partition_key)
        self.sort_key = self.sort_key_prefix + str.upper(sort_key)
        self.primary_key = {"PK": self.partition_key, "SK": self.sort_key}
        self.secondary_index = {self.secondary_index_prefix + "PK": self.sort_key}

        super().__init__(self.primary_key, self.secondary_index, self.type, item_label, attributes)


"""
Child class: DatacenterItem(TableItem)
Accepts:
  - 'partition_key' - string
  - 'sort_key' - string
  - 'item_label' - string
  - 'attributes' - dict
Constants:
  - self.partition_key_prefix = "VC#"
  - self.sort_key_prefix = "DC#"
  - self.type = "datacenter"
  - self.secondary_index_prefix = "GSI2"
Item structure:
    {
        'PK': 'VC#PART_KEY', 
        'SK': 'DC#SORT_KEY', 
        'GSI2PK': 'DC#SORT_KEY', 
        'ItemType': 'datacenter', 
        'Label': 'item_label', 
        'attribute': 'value'
    }
"""
class DatacenterItem(TableItem):
    def __init__(self, partition_key: str = "", sort_key: str = "", item_label: str = "", attributes=None):
        self.partition_key_prefix = "VC#"
        self.sort_key_prefix = "DC#"
        self.type = "datacenter"
        self.secondary_index_prefix = "GSI2"
        self.partition_key = self.partition_key_prefix + str.upper(partition_key)
        self.sort_key = self.sort_key_prefix + str.upper(sort_key)
        self.primary_key = {"PK": self.partition_key, "SK": self.sort_key}
        self.secondary_index = {self.secondary_index_prefix + "PK": self.sort_key}

        super().__init__(self.primary_key, self.secondary_index, self.type, item_label,attributes)


"""
Child class: ComputeClusterItem(TableItem)
Accepts:
  - 'partition_key' - string
  - 'sort_key' - string
  - 'item_label' - string
  - 'attributes' - dict
Constants:
  - self.partition_key_prefix = "DC#"
  - self.sort_key_prefix = "CC#"
  - self.type = "compute_cluster"
  - self.secondary_index_prefix = "GSI3"
Item structure:
    {
        'PK': 'DC#PART_KEY', 
        'SK': 'CC#SORT_KEY', 
        'GSI3PK': 'CC#SORT_KEY, 
        'ItemType': 'compute_cluster', 
        'Label': 'item_label', 
        'attribute': 'value'
    }
"""
class ComputeClusterItem(TableItem):
    def __init__(self, partition_key: str = "", sort_key: str = "", item_label: str = "", attributes=None):
        self.partition_key_prefix = "DC#"
        self.sort_key_prefix = "CC#"
        self.type = "compute_cluster"
        self.secondary_index_prefix = "GSI3"
        self.partition_key = self.partition_key_prefix + str.upper(partition_key)
        self.sort_key = self.sort_key_prefix + str.upper(sort_key)
        self.primary_key = {"PK": self.partition_key, "SK": self.sort_key}
        self.secondary_index = {self.secondary_index_prefix + "PK": self.sort_key}

        super().__init__(self.primary_key, self.secondary_index, self.type, item_label, attributes)


"""
Child class: DatastoreItem(TableItem)
Accepts:
  - 'partition_key' - string
  - 'sort_key' - string
  - 'item_label' - string
  - 'attributes' - dict
Constants:
  - self.partition_key_prefix = "CC#"
  - self.sort_key_prefix = "DS#"
  - self.type = "datastore"
  - self.secondary_index_prefix = "GSI4"
Item structure:
    {
        'PK': 'CC#PART_KEY', 
        'SK': 'DS#SORT_KEY', 
        'GSI4PK': 'DS#SORT_KEY#CC#PART_KEY', 
        'ItemType': 'datastore', 
        'Label': 'item_label', 
        'attribute': 'value'
    }
"""
class DatastoreItem(TableItem):
    def __init__(self, partition_key: str = "", sort_key: str = "", item_label: str = "", attributes=None):
        self.partition_key_prefix = "CC#"
        self.sort_key_prefix = "DS#"
        self.type = "datastore"
        self.secondary_index_prefix = "GSI4"
        self.partition_key = self.partition_key_prefix + str.upper(partition_key)
        self.sort_key = self.sort_key_prefix + str.upper(sort_key)
        self.primary_key = {"PK": self.partition_key, "SK": self.sort_key}
        self.secondary_index = {self.secondary_index_prefix + "PK": self.sort_key + "#" + self.partition_key}

        super().__init__(self.primary_key, self.secondary_index, self.type, item_label ,attributes)

"""
Child class: NetworkItem(TableItem)
Accepts:
  - 'partition_key' - string
  - 'sort_key' - string
  - 'item_label' - string
  - 'attributes' - dict
Constants:
  - self.partition_key_prefix = "CC#"
  - self.sort_key_prefix = "NW#"
  - self.type = "network"
  - self.secondary_index_prefix = "GSI5"
Item structure:
    NetworkItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    {
        'PK': 'CC#PART_KEY', 
        'SK': 'NW#SORT_KEY', 
        'GSI5PK': 'NW#SORT_KEY#CC#PART_KEY',
        'ItemType': 'network', 
        'Label': 'item_label', 
        'attribute': 'value'
    }
"""
class NetworkItem(TableItem):
    def __init__(self, partition_key: str = "", sort_key: str = "", item_label: str = "", attributes=None):
        self.partition_key_prefix = "CC#"
        self.sort_key_prefix = "NW#"
        self.type = "network"
        self.secondary_index_prefix = "GSI5"
        self.partition_key = self.partition_key_prefix + str.upper(partition_key)
        self.sort_key = self.sort_key_prefix + str.upper(sort_key)
        self.primary_key = {"PK": self.partition_key, "SK": self.sort_key}
        self.secondary_index = {self.secondary_index_prefix + "PK": self.sort_key + "#" + self.partition_key}

        super().__init__(self.primary_key, self.secondary_index, self.type, item_label, attributes)


"""
Child class: TemplateItem(TableItem)
Accepts:
  - 'partition_key' - string
  - 'sort_key' - string
  - 'item_label' - string
  - 'attributes' - dict
Constants:
  - self.partition_key_prefix = "VC#"
  - self.sort_key_prefix = "VT#"
  - self.type = "vm_template"
  - self.secondary_index_prefix = "GSI6"
Item Structure:
    TemplateItem("part_key", "sort_key", "item_label", {"attribute": "value"})
    {
        'PK': 'VC#PART_KEY', 
        'SK': 'VT#SORT_KEY', 
        'GSI6PK': 'VT#SORT_KEY#VC#PART_KEY', 
        'ItemType': 'vm_template', 
        'Label': 'item_label', 
        'attribute': 'value'
    }
"""
class TemplateItem(TableItem):
    def __init__(self, partition_key: str = "", sort_key: str = "", item_label: str = "", attributes=None):
        self.partition_key_prefix = "VC#"
        self.sort_key_prefix = "VT#"
        self.type = "vm_template"
        self.secondary_index_prefix = "GSI6"
        self.partition_key = self.partition_key_prefix + str.upper(partition_key)
        self.sort_key = self.sort_key_prefix + str.upper(sort_key)
        self.primary_key = {"PK": self.partition_key, "SK": self.sort_key}
        self.secondary_index = {self.secondary_index_prefix + "PK": self.sort_key + "#" + self.partition_key}

        super().__init__(self.primary_key, self.secondary_index, self.type, item_label ,attributes)