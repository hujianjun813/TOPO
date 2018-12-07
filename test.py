# encoding:utf-8

from resource import *
from topo import *

resource1 = {
    "status": u"空闲",
    "id":1,
    "device_type": "VCFC"
}
resource2 = {
    "status": u"共享",
    "id":2,
    "device_type": "VCFC"
}

R1 = AutoResource(resource1)
R2 = AutoResource(resource2)
AutoRS = {
    R1.resource['id']: R1,
    R2.resource['id']: R2
}

DUT1 = TopoNode("VCFC")
DUT1.type = "VCFC"
DUT2 = TopoNode("VCFC")
DUT2.type = "VCFC"
DUT2.share = True

for _ in yeild_topo(AutoRS, DUT2):
   # print DUT1.resource.resource
    print DUT2.resource.resource
    print "***********"

print 123