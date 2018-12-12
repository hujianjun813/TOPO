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
        tmp_share = list()
        tmp_idle = list()
        for auto_resource in share_auto_resources:
            if not is_available_resource(auto_resource, node):
                continue
            tmp_share.append(auto_resource)
        for auto_resource in idle_auto_resources:
            if not is_available_resource(auto_resource, node):
                continue
            tmp_idle.append(auto_resource)


        if tmp_share:
            for auto_resource in tmp_share:
                auto_resource.resource['issu'] = False
                auto_resource.is_used = True
                node.resource = auto_resource
                yield True
        elif tmp_idle:
            for auto_resource in tmp_share:
                auto_resource.resource['issu'] = False
                auto_resource.is_used = True
                auto_resource.is_share = True
                node.resource = auto_resource
                yield True
        else:
            for auto_resource in idle_auto_resources:
                auto_resource.resource['issu'] = True
                auto_resource.is_used = True
                auto_resource.is_share = True
                node.resource = auto_resource
                yield True


    # 当所需资源为独占模式时，从空闲资源池中查询
    # 如果匹配不到，从空闲资源池中分配，添加升级标签
    else:
        tmp_resources = list()
        for auto_resource in idle_auto_resources:
            if not is_available_resource(auto_resource, node):
                continue
            tmp_resources.append(auto_resource)

        if tmp_resources:
            for auto_resource in tmp_resources:
                auto_resource.resource['issu'] = False
                auto_resource.is_used = True
                node.resource = auto_resource
                yield True
        else:
            for auto_resource in idle_auto_resources:
                auto_resource.resource['issu'] = True
                auto_resource.is_used = True
                node.resource = auto_resource
                yield True

def get_reverse_link(node, next_node, link):
    """根据node_link，获取next_node中 next_node->node的资源链路"""
    if not next_node.resource:
        return False, 'no such resource'

    remote_port = link.remote_port
    if remote_port not in next_node.resource.links:
        return False, 'no such link'

    return True, next_node.resource.links[remote_port]


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
        if node.next_nodes[index][link_node]:
            yield True
        else:
            resource_ids = [x for x in resource_link['remote']]
            # 该节点中已存在资源，判断资源是否匹配当前的链路信息
            if link_node.resource:
                if link_node.resource.resource['id'] in resource_ids:
                    link = resource_link['remote'][link_node.resource.resource['id']]
                    node.next_nodes[index][link_node] =link
                    link_code, rev_link = get_reverse_link(node, link_node, link)
                    if link_code:
                        for (next_index, next_node_link) in link_node.unselect_links:
                            if node not in next_node_link['remote']:
                                continue
                            for has_link in _yeild_link(auto_resources, link_node, next_index, next_node_link,
                                                        rev_link):
                                if has_link:
                                    yield True
                    node.next_nodes[index][link_node] = None

            # 需新生成节点
            else:
                for _ in yeild_node(
                        auto_resources, link_node,resource_ids=resource_ids):
                    link = resource_link['remote'][link_node.resource.resource['id']]
                    # 添加node-> next_node 的链路信息
                    node.next_nodes[index][link_node] = link

                    # 处理next_node -> node 的链路信息
                    # 在 next_node节点resource中找到当前链路到对端链路
                    # 使用该链路信息，对next_node中的next_node的node信息进行遍历匹配
                    link_code, rev_link = get_reverse_link(node, link_node, link)
                    if link_code:
                        for (next_index, next_node_link) in link_node.unselect_links:
                            if node not in next_node_link['remote']:
                                continue
                            for has_link in _yeild_link(auto_resources, link_node, next_index, next_node_link, rev_link):
                                if has_link:
                                    for _ in yeild_link_nodes(
                                            auto_resources, node, index, link_nodes[1:],
                                            resource_link):
                                        yield True
                    link_node.resource.is_used = False
                    link_node.resource.is_share = link_node.resource.resource_share
                    link_node.resource = None
                    node.next_nodes[index][link_node] = None

def _yeild_link(auto_resources, node, index, node_link, resource_link):
    if resource_link['is_used']:
        yield False
    if 'type' in resource_link and node_link['type'] != resource_link['type']:
        yield False
    else:
        for _ in yeild_link_nodes(
                auto_resources, node, index, node_link['remote'],
                resource_link):
            node.next_nodes[index]['link'] = resource_link
            resource_link['is_used'] = True
            yield _
            resource_link['is_used'] = False
            node.next_nodes[index]['link'] = None




def yeild_link(auto_resources, node, index, node_link):
    """ 资源链路和需要的节点链路进行匹配
    :param auto_resource:
    :param node:
    :param node_link:
    :return:
    """
    for port_name in node.resource.links:
        resource_link = node.resource.links[port_name]
        for has_link in _yeild_link(
                auto_resources, node, index, node_link,
                resource_link):
            if has_link:
                yield True


def yeild_next_nodes(auto_resources, node, unselect_links):
    """对node节点中对应的链路节点进行匹配"""
    if not unselect_links:
        yield True
    else:
        index, node_link = unselect_links[0]
        if node.next_nodes[index]['link']:
            yield True
        else:
            for _ in yeild_link(auto_resources, node, index, node_link):
                for _ in yeild_next_nodes(auto_resources, node, unselect_links[1:]):
                    yield _


def yeild_topo(auto_resources, *nodes):

    if not nodes:
        yield True
    else:
        node = nodes[0]
        # 当前节点的资源已经查询到，无需新生成节点
        if node.resource:
            # 遍历该节点下链路节点
            for _ in yeild_next_nodes(
                    auto_resources, node, node.unselect_links):
                # 遍历剩余的拓扑节点
                for _ in yeild_topo(auto_resources, *nodes[1:]):
                    yield _
        else:
            # 遍历节点
            for _ in yeild_node(auto_resources, node):
                # 遍历该节点下链路节点
                for _ in yeild_next_nodes(
                        auto_resources, node, node.unselect_links):
                    # 遍历剩余的拓扑节点
                    for _ in yeild_topo(auto_resources, *nodes[1:]):
                        yield _
                node.resource.is_used = False
                node.resource.is_share = node.resource.resource_share
                node.resource = None
