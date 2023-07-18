# vCenter DynamoDB ETL
Python code to Extract-Transform-Load vCenter data to a DynamoDB table

# DynamoDB Table
## vCenter Item
```
PK - VC#<vcenter shortname>
SK - VC#<vcenter shortname>
ItemType - vcenter
Label - <vCenter short name>
VcFqdn - <vcenter FQDN>
GSI1PK - VC#<vcenter shortname>
```
## Datacenter Item
```
PK - VC#<vcenter shortname>
SK - DC#<vcenter shortname>
ItemType - datacenter
Label - <vSphere datacenter name>
GSI2PK - DC#<vSphere Datacenter name>#VC#<vcenter shortname>
```
## Computer Cluster Item
```
PK - DC#<vSphere Datacenter name>
SK - CC#<vSphere Compute Cluster name>
ItemType - compute_cluster
Label - <vSphere Compute Cluster name>
CpuCapacityMHz - <total Compute Cluster CPU capacity>
CpuFreeMHz - <available Compute Cluster CPU>
MemCapacityMB - <total Compute Cluster memory capacity>
MemFreeMB - <available Computer Cluster memory>
GSI3PK - CC#<vSphere Compute Cluster name>#DC#<vcenter shortname>
```
## Datastore Item
```
PK - CC#<vSphere Compute Cluster name>
SK - DS#<vSphere Datastore name>
ItemType - datastore
Label - <vSphere datastore name>
StorageCapacityGB - <total Datastore capacity>
StorageFreeGB - <available Datastore space>
GSI4PK - DS#<vSphere Datastore name>#CC#<vSphere Compute Cluster name>
```
## Network Item
```
PK - CC#<vSphere Compute Cluster name>
SK - NW#<subnet IP_Netmask>
ItemType - network
Label - <vSphere Network name>
GSI5PK - NW#<vSphere Network name>#CC#<vSphere Compute Cluster name>
```
## VM template Item
```
PK - VC#<vcenter shortname>
SK - VT#<VM Template name>
ItemType - vm_template
Label - <VM Template name>
Template - Stage|Prod
GSI6PK - VT#<Target parent name>#VC#<vcenter shortname>
```

