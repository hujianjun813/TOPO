# encoding:utf-8

from resource import *
from topo import *

resource = {
    "status": u"空闲",
    "id":1,
    "device_type": "VCFC"
}

R1 = AutoResource(resource)
AutoRS = {
    R1.resource['id']: R1
}

DUT1 = TopoNode("VCFC")
DUT1.type = "VCFC"

for _ in yeild_topo(AutoRS, DUT1):
    print DUT1.resource.resource
    print "***********"