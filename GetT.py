# encoding:utf-8

from resource import *
from topo import *
from auto import AutoRS

DUT1 = TopoNode("VCFC")
DUT1.type = "VCFC"

DUT2 = TopoNode("68_1")
DUT2.type = u"交换机"
DUT2.subtype = "s6800"


DUT3 = TopoNode("68_2")
DUT3.type = u"交换机"
DUT3.subtype = "s6800"


VM1 = TopoNode("vm1")
VM1.type = u"centos"
VM2 = TopoNode("vm2")
VM2.type = u"centos"
VM3 = TopoNode("vm3")
VM3.type = u"centos"
VM4 = TopoNode("vm4")
VM4.type = u"centos"
VM5 = TopoNode("vm5")
VM5.type = u"centos"
VM6 = TopoNode("vm6")
VM6.type = u"centos"

DUT2.add_next_node([DUT3])
DUT2.add_next_node([DUT3])
DUT2.add_next_node([VM1, VM2, VM3])
DUT3.add_next_node([DUT2])
DUT3.add_next_node([DUT2])
DUT3.add_next_node([VM4, VM5])
VM1.add_next_node([DUT2])
VM2.add_next_node([DUT2])
VM3.add_next_node([DUT2])
VM4.add_next_node([DUT3])
VM5.add_next_node([DUT3])

def out_link(dut):
    for index in dut.next_nodes:
        print dut.next_nodes[index]

def out_dut(*duts):
    for dut in duts:
        print dut.resource.resource
        out_link(dut)
    print "*****"

duts = [DUT2, DUT3, VM1, VM2, VM3, VM4, VM5, VM6]

N=1
for _ in yeild_topo(AutoRS,*duts):
    out_dut(*duts)
    N+=1
print N

print "************************************************"

# for rs in AutoRS:
#     print "%s->%s:%s" %(AutoRS[rs].resource, AutoRS[rs].is_used, AutoRS[rs].is_share)
#     print AutoRS[rs].links