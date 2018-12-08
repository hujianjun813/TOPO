#! encoding:utf-8

class AutoLink(object):

    def __init__(self, local_id, local_port, remote_id, remote_port):
        self.local_id = local_id
        self.local_port = local_port
        self.remote_id = remote_id
        self.remote_port = remote_port

    def __str__(self):
        return "%s.%s -> %s.%s" %(
            self.local_id, self.local_port, self.remote_id, self.remote_port)

    def __repr__(self):
        return "%s.%s -> %s.%s" %(
            self.local_id, self.local_port, self.remote_id, self.remote_port)

class AutoResource(object):

    """
    self.links = {
        'port_name': {
            'type':'',
            'is_used':False,
            'remote': {
                'remote_id': LINK,
                'remote_id': LINK,
            }
        }
    }


    """


    def __init__(self, resource):
        self.resource = resource
        self.links = dict()
        self.is_used = False
        self.is_share = resource['status'] == u'共享'
        self.resource_share = resource['status'] == u'共享'

    def __str__(self):
        return self.resource['id']

    def __repr__(self):
        return self.resource['id']

    def add_link(self, link):
        if link.local_port not in self.links:
            self.links[link.local_port] = {'is_used': False,'remote': dict()}
        self.links[link.local_port]['remote'][link.remote_id] = link


class TopoNode(object):
    """
    self.next_nodes = {'index':{
        'type': "",
        Node:Link,
        Node:Link
    }}

    self.unselect_nodes = [(index,{
        "type":"",
        "remote":{
            Node: remote_index
            Node: remote_index
        }
    })]
    """


    def __init__(self, name):
        self.name = name
        self.type = None
        self.subtype = None
        self.id = None
        self.version = None
        self.size = None
        self.share = False
        self.next_nodes = dict()
        self.unselect_links = list()
        self.resource = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def add_next_node(self, index, nodes, type=None):
        self.next_nodes[index] = dict()
        for node in nodes:
            self.next_nodes[index][node] = None
        self.unselect_links.append(
            (index,{"type": type if type else "","remote": nodes})
        )


def prt_node(topo):

    nodes = dict()
    # 生成节点
    for node_name in topo:
        topo_node = topo[node_name]
        node = TopoNode(node_name)
        node.type = topo_node['type']
        node.subtype = topo_node['subtype'] if 'subtype' in topo_node else None
        nodes[node_name] = node

    # 对节点产生链路信息
