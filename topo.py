#! encoding:utf-8

def is_available_resource(auto_resource, node):
    resource = auto_resource.resource
    # 剔除所需信息不匹配的资源
    if node.type != resource['device_type']:
        return False
    if node.subtype and node.subtype != resource['device_subtype']:
        return False
    if node.id and node.id != resource['id']:
        return False
    if node.version and node.version != resource['version']:
        return False
    if node.size and node.size != resource['size']:
        return False
    return True


def yeild_node(auto_resources, node, resource_ids=None):
    """ 生成当前节点
    :param auto_resources: 自动化资源池
    :param node: 所需节点
    :param resource_ids: 只有如下资源才可使用
    :return:
    """

    idle_auto_resources = list()
    share_auto_resources = list()

    for resource_id in auto_resources:
        auto_resource = auto_resources[resource_id]

        # 剔除已被使用且为独占模式的资源
        if auto_resource.is_used and not auto_resource.is_share:
            continue

        # 剔除所需节点为独占模式 但资源为共享
        if not node.share and auto_resource.is_share:
            continue

        # 剔除非指定节点的资源
        if resource_ids and resource_id not in resource_ids:
            continue

        # 资源放入缓存
        if auto_resource.is_share:
            share_auto_resources.append(auto_resource)
        else:
            idle_auto_resources.append(auto_resource)


    # 进行资源查找
    # 所需节点为共享资源，从共享资源中查询
    # 如果匹配不到从空闲资源次中匹配
    # 再次匹配不到，从空闲资源池中分配，添加升级标签

    if node.share:

        for auto_resource in share_auto_resources:
            if not is_available_resource(auto_resource, node):
                continue
            auto_resource.resource['issu'] = False
            auto_resource.is_used = True
            node.resource = auto_resource
            yield True

        for auto_resource in idle_auto_resources:
            if not is_available_resource(auto_resource, node):
                continue
            auto_resource.resource['issu'] = False
            auto_resource.is_used = True
            auto_resource.is_share = True
            node.resource = auto_resource
            yield True

        if idle_auto_resources:
            auto_resource = idle_auto_resources[0]
            auto_resource.resource['issu'] = True
            auto_resource.is_used = True
            auto_resource.is_share = True
            node.resource = auto_resource
            yield True

    # 当所需资源为独占模式时，从空闲资源池中查询
    # 如果匹配不到，从空闲资源池中分配，添加升级标签
    else:
        for auto_resource in idle_auto_resources:
            if not is_available_resource(auto_resource, node):
                continue
            auto_resource.resource['issu'] = False
            auto_resource.is_used = True
            node.resource = auto_resource
            yield True

        if idle_auto_resources:
            auto_resource = idle_auto_resources[0]
            auto_resource.resource['issu'] = True
            auto_resource.is_used = True
            node.resource = auto_resource
            yield True

def yeild_link_nodes(auto_resources, node, index, link_nodes, resource_link):
    """ 从资源的链路信息中生成对应的节点，
    :param auto_resources:
    :param link_nodes:
    :param resource_link:
    :return:
    """
    if not link_nodes:
        yield True
    else:
        link_node = link_nodes[0]
        resource_ids = [x for x in resource_link['remote']]
        # 该节点中已存在资源，判断资源是否匹配当前的链路信息
        if link_node.resource:
            if link_node.resource['id'] in resource_ids:
                node.next_nodes[index][link_node] = resource_link['remote'][link_node.resource['id']]
                yield True
                node.next_nodes[index][link_node] = None

        # 需新生成节点
        else:
            for _ in yeild_node(
                    auto_resources, link_node,resource_ids=resource_ids):
                node.next_nodes[index][link_node] = resource_link['remote'][
                    link_node.resource['id']]
                for _ in yeild_link_nodes(
                        auto_resources, node, index, link_nodes[1:], resource_link):
                    yield True
                node.next_nodes[index][link_node] = None
                link_node.resouce.is_used = False
                link_node.resource.is_share = link_node.resource.resource_share
                link_node.resouce = None



def _yeild_link(auto_resources, node, index, node_link, resource_link):
    if resource_link['is_used']:
        yield False
    elif 'type' in node_link and 'type' not in resource_link:
        yield False
    elif 'type' in node_link and  node_link['type'] != resource_link['type']:
        yield False
    else:
        for _ in yeild_link_nodes(
                auto_resources, node, index, node_link['remote'], resource_link):

            node.next_nodes[index]['link'] = resource_link
            resource_link['is_used'] = True
            yield _
            node.next_nodes[index]['link'] = None
            resource_link['is_used'] = False


def yeild_link(auto_resources, node, index, node_link):
    """ 资源链路和需要的节点链路进行匹配
    :param auto_resource:
    :param node:
    :param node_link:
    :return:
    """
    for port_name in node.resource.links:
        for has_link in _yeild_link(
                auto_resources, node, index, node_link,
                node.resource.links[port_name]):
            if has_link:
                yield True

def yeild_next_nodes(auto_resources, node):
    """对node节点中对应的链路节点进行匹配"""

    if not node.next_nodes:
        yield True
    else:
        index, node_link = node.unselect_links[0]
        for _ in yeild_link(auto_resources, node, index, node_link):
            node.unselect_links = node.unselect_links[1:]
            for _ in yeild_next_nodes(auto_resources, node):
                yield _


def yeild_topo(auto_resources, *nodes):

    if not nodes:
        yield True
    else:
        node = nodes[0]
        # 当前节点的资源已经查询到，无需新生成节点
        if node.resource:
            # 遍历该节点下链路节点
            for _ in yeild_next_nodes(auto_resources, node):
                # 遍历剩余的拓扑节点
                for _ in yeild_topo(auto_resources, *nodes[1:]):
                    yield _
        else:
            # 遍历节点
            for _ in yeild_node(auto_resources, node):
                # 遍历该节点下链路节点
                for _ in yeild_next_nodes(auto_resources, node):
                    # 遍历剩余的拓扑节点
                    for _ in yeild_topo(auto_resources, *nodes[1:]):
                        yield _
                node.resource.is_used = False
                node.resource.is_share = node.resource.resource_share
                node.resource = None

    
