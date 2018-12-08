# encoding:utf-8

from resource import *
from topo import *

vcfc1 = {
    "status": u"空闲",
    "id":1,
    "device_type": "VCFC"
}
vcfc2 = {
    "status": u"共享",
    "id":2,
    "device_type": "VCFC"
}

switch1 = {
    "status": u'空闲',
    'id':3,
    'device_type': u'交换机',
    'device_subtype': u's6800'
}
switch2 = {
    "status": u'空闲',
    'id':4,
    'device_type': u'交换机',
    'device_subtype': u's6800'
}

vm1 = {
    "status": u'空闲',
    'id': 5,
    'device_type': u'centos'
}

vm2 = {
    "status": u'空闲',
    'id': 6,
    'device_type': u'centos'
}

vm3 = {
    "status": u'空闲',
    'id': 7,
    'device_type': u'centos'
}

vm4 = {
    "status": u'空闲',
    'id': 8,
    'device_type': u'centos'
}

vm5 = {
    "status": u'空闲',
    'id': 9,
    'device_type': u'centos'
}

vm6 = {
    "status": u'空闲',
    'id': 10,
    'device_type': u'centos'
}


vm7= {
    "status": u'空闲',
    'id': 11,
    'device_type': u'centos'
}

vm8 = {
    "status": u'空闲',
    'id': 12,
    'device_type': u'centos'
}

vm9 = {
    "status": u'空闲',
    'id': 13,
    'device_type': u'centos'
}


switch1_link1 =  AutoLink(switch1['id'],'Ten0/1',switch2['id'], 'Ten0/1')
switch1_link2 =  AutoLink(switch1['id'],'Ten0/2',switch2['id'], 'Ten0/2')
switch2_link1 =  AutoLink(switch2['id'],'Ten0/1',switch1['id'], 'Ten0/1')
switch2_link2 =  AutoLink(switch2['id'],'Ten0/2',switch1['id'], 'Ten0/2')

switch1_link3 =  AutoLink(switch1['id'],'Ten0/13',vm1['id'], 'nic1')
switch1_link4 =  AutoLink(switch1['id'],'Ten0/13',vm2['id'], 'nic1')
switch1_link5 =  AutoLink(switch1['id'],'Ten0/13',vm3['id'], 'nic1')
switch1_link6 =  AutoLink(switch1['id'],'Ten0/14',vm4['id'], 'nic1')
switch2_link3 =  AutoLink(switch2['id'],'Ten0/13',vm5['id'], 'nic1')
switch2_link4 =  AutoLink(switch2['id'],'Ten0/13',vm6['id'], 'nic1')
switch2_link5 =  AutoLink(switch2['id'],'Ten0/14',vm7['id'], 'nic1')
switch2_link6 =  AutoLink(switch2['id'],'Ten0/15',vm8['id'], 'nic1')


R1 = AutoResource(vcfc1)
R2 = AutoResource(vcfc2)
R3 = AutoResource(switch1)
R3.add_link(switch1_link1)
R3.add_link(switch1_link2)

R4 = AutoResource(switch2)
R4.add_link(switch2_link1)
R4.add_link(switch2_link2)



R3.add_link(switch1_link3)
R3.add_link(switch1_link4)
R3.add_link(switch1_link5)
R3.add_link(switch1_link6)
R4.add_link(switch2_link3)
R4.add_link(switch2_link4)
R4.add_link(switch2_link5)
R4.add_link(switch2_link6)
R5=AutoResource(vm1)
R6=AutoResource(vm2)
R7=AutoResource(vm3)
R8=AutoResource(vm4)
R9=AutoResource(vm5)
R10=AutoResource(vm6)
R11=AutoResource(vm7)
R12=AutoResource(vm8)
R13=AutoResource(vm9)



AutoRS = {
    R1.resource['id']: R1,
    R2.resource['id']: R2,
    R3.resource['id']: R3,
    R4.resource['id']: R4,
    R5.resource['id']: R5,
    R6.resource['id']: R6,
    R7.resource['id']: R7,
    R8.resource['id']: R8,
    R9.resource['id']: R9,
    R10.resource['id']: R10,
    R11.resource['id']: R11,
    R12.resource['id']: R12,
    R13.resource['id']: R13
}