# coding: utf-8
from flask import Flask, jsonify, render_template, request
from py2neo import Graph,Node, Relationship

from flask_cors import CORS
import os
from werkzeug.utils import *
import json

app = Flask(__name__)
CORS(app)


# 连接数据库
graph = Graph("http://localhost:7474/db/data/")

@app.after_request
def cors(environ):
    environ.headers['Access-Control-Allow-Origin'] = '*'
    environ.headers['Access-Control-Allow-Method'] = 'POST,GET,OPTIONS,PUT,PATCH,DELETE'
    environ.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return environ

def buildNodes(node):  # 获取节点数据，以json方式存储
    data = {"id": str(node.identity), "label": str(node.labels).replace(':', '')}
    data.update(dict(node))
    return {"data": data}


def buildEdges(relation):  # 获取边数据，以json方式存储
    data = {"source": str(relation.start_node.identity),  # 获取源节点和目标节点的id
            "target": str(relation.end_node.identity),
            "relationship": str(type(relation)).replace("<class 'py2neo.data.", '').replace("'>", '')}
    return {"data": data}


def buildPath(cypherStr):
    nodeList = set()  # 创建空元素集
    relationshipList = set()
    result = graph.run(cypherStr)  # 执行cypher查询语句
    for record in result:
        for node in record['p'].nodes:
            nodeList.add(node)
        for relationship in record['p'].relationships:
            relationshipList.add(relationship)
    nodes = map(buildNodes, nodeList)
    relationships = map(buildEdges, relationshipList)
    return nodes, relationships
def node_relationship(Bas_node, relation, BasInfo_node):
    node_1_relationship_company_region = Relationship(Bas_node, relation, BasInfo_node)
    node_1_relationship_company_region['relation'] = relation
    graph.create(node_1_relationship_company_region)

#通过节点ID 更新节点的信息
def node_update(node, key, value):
    tag = str(node.labels).strip(":")
    if isinstance(value, str):
        value = repr(value)
    query = 'MATCH(n: {}) WHERE ID(n) = {} SET n.{} = {}'.format(tag, node.identity, key, value)
    graph.run(query)

#创建节点
def create_node(tag, attrs):
    if not query_node(tag, attrs):
        drug_node = Node(tag, **attrs)
        graph.create(drug_node)
        return drug_node

#查询节点是否已用
def query_node(tag, attrs):
    return graph.nodes.match(tag, **attrs).first()

#解析青藤云数据
def handler_host(host, records):
    hostname = host["hostname"]
    host_id = host["host_id"]
    external_ip = host["external_ip"]
    internal_ip = host["internal_ip"]
    display_ip = host["display_ip"]

    # 创建主机节点
    node_host = query_node("HOST", {"host_id": host_id})
    if not node_host:
        host_info = {"hostname": hostname, "host_id": host_id, "external_ip": external_ip, "display_ip": display_ip, "internal_ip": internal_ip}
        node_host = create_node("HOST", host_info)
        # print("Create Host Node: {} {}".format(hostname, host_id))

    # 创建IP节点
    for ip in host["listen_ip"]:
        node_ip = query_node("IP", {"ip": ip})

        if not node_ip:
            node_ip = create_node("IP", {"ip": ip, "hostname": hostname, "host_id": host_id})
            print("Create IP Node: {} {}".format(ip, hostname))

        if not node_ip["hostname"]:  # 补充Hostname字段
            # print("Update Node Hostname: {} --> {}".format(node_ip['ip'], hostname))
            node_update(node_ip, "hostname", hostname)
            node_update(node_ip, "host_id", host_id)

        node_relationship(node_host, "bind", node_ip)
        # print("Create Relation {} --> {}".format(hostname, ip))

    for item in records:
        print(item)
        src_ip = item["local_ip"]
        src_port = item["local_port"]
        dst_ip = item["foreign_ip"]
        dst_port = item["foreign_port"]
        proto = item["proto"]
        process = item["proc_name"]
        pid = item["pid"]
        state = item["state"]
        iptype = item["iptype"]

        # 处理源IP节点， 创建IP与主机节点关系
        if src_ip in ["127.0.0.1", "::ffff:127.0.0.1", "::1"]:
            node_src_ip = query_node("IP", {"ip": src_ip, "hostname": hostname, "host_id": host_id})  # 处理127.0.0.1
            if not node_src_ip:
                node_src_ip = create_node("IP", {"ip": src_ip, "hostname": hostname, "host_id": host_id})
                print("Create IP Node: {} {}".format(src_ip, hostname))

            node_relationship(node_host, "bind", node_src_ip)
            # print("Create Relation {} --> {}".format(hostname, src_ip))

        # 创建目的IP节点， 创建IP节点关系
        if dst_ip in ["127.0.0.1", "::ffff:127.0.0.1", "::1"]:
            node_dst_ip = query_node("IP", {"ip": dst_ip, "hostname": hostname, "host_id": host_id})
            if not node_dst_ip:
                node_dst_ip = create_node("IP", {"ip": dst_ip, "hostname": hostname, "host_id": host_id})
                print("Create Foreign IP Node: {} {}".format(dst_ip, hostname))
                node_relationship(node_host, "bind", node_dst_ip)
                # print("Create Relation {} --> {}".format(hostname, dst_ip))

        elif dst_ip not in ["0.0.0.0", "::"]:
            node_dst_ip = query_node("IP", {"ip": dst_ip})
            if not node_dst_ip:
                node_dst_ip = create_node("IP", {"ip": dst_ip})
                #print("Create Foreign IP Node: {}".format(dst_ip))    # 创建一个没有Hostname属性的IP节点
            node_src_ip = query_node("IP", {"ip": src_ip, "hostname": hostname})

            # 判断IP与IP节点之间的请求关系
            if src_port in host["listen_port"]:
                src_h = node_dst_ip
                dst_h = node_src_ip
            else:
                src_h = node_src_ip
                dst_h = node_dst_ip

            node_relationship(src_h, "connect", dst_h)
            # print("Create Relation {} --> {}".format(src["ip"], dst["ip"]))

        # TODO 查询已存在的节点，信息更新
        if state in ["LISTEN", "UNCONN"]:
            if src_ip in ["0.0.0.0", "::"]:
                for ip in host["listen_ip"]:
                    node_src_ip = query_node("IP", {"ip": ip, "hostname": hostname})

                    port_info = {'port': src_port, "ip": ip, "proto": proto, "name": "{}:{}".format(ip, src_port) }
                    node_src_port = query_node("PORT", port_info)
                    if not node_src_port:
                        port_info["hostname"] = hostname
                        port_info["host_id"] = host_id
                        port_info["process"] = process
                        port_info["listen"] = src_ip
                        port_info["status"] = state
                        node_src_port = create_node("PORT", port_info,)

                    if not node_src_port["host_id"]:
                        node_update(node_src_port, "listen", src_ip)
                        node_update(node_src_port, "process", process)
                        node_update(node_src_port, "hostname", hostname)
                        node_update(node_src_port, "host_id", host_id)
                        node_update(node_src_port, "status",state)

                    node_relationship(node_src_ip, state, node_src_port)
                    print("Create Port Relation: {} --> {}".format(ip, src_port))
            else:   # 监听127.0.0.1 ::1 的情况
                host_info = {"ip": src_ip}
                if src_ip in ["127.0.0.1", "::ffff:127.0.0.1", "::1"]:
                    host_info["host_id"] = host_id
                    host_info["hostname"] = hostname
                node_src_ip = query_node("IP", host_info)
                if not node_src_ip:
                    node_src_ip = create_node("IP", host_info)
                    print("Create IP Node: {} {}".format(src_ip, hostname))

                if not node_src_ip["hostname"]:
                    node_update(node_src_ip, "hostname", hostname)
                    node_update(node_src_ip, "host_id", host_id)

                port_info = {'port': src_port, "ip": src_ip, "proto": proto,  "name": "{}:{}".format(src_ip, src_port)}
                if src_ip in ["127.0.0.1", "::ffff:127.0.0.1", "::1"]:
                    port_info["host_id"] = host_id
                    port_info["hostname"] = hostname
                    port_info["process"] = process

                node_src_port = query_node("PORT", port_info)
                if not node_src_port:
                    port_info["listen"] = src_ip
                    port_info["status"] = state
                    node_src_port = create_node("PORT", port_info)

                if not node_src_port["hostname"]:
                    node_update(node_src_port, "hostname", hostname)
                    node_update(node_src_port, "host_id", host_id)
                    node_update(node_src_port, "process", process)
                    node_update(node_src_port, "status", state)

                node_relationship(node_src_ip, state, node_src_port)
                print("Create Port Relation: {} --> {}".format(src_ip, src_port))

        else:
            src_port_info = {'port': src_port, "ip": src_ip, "proto": proto, "name": "{}:{}".format(src_ip, src_port)}
            if src_ip in ["127.0.0.1", "::ffff:127.0.0.1", "::1"]:
                src_port_info["hostname"] = hostname
                src_port_info["host_id"] = host_id
                src_port_info["process"] = process

            node_src_port = query_node("PORT", src_port_info)

            if not node_src_port:
                src_port_info["listen"] = src_ip
                src_port_info["name"] = "{}:{}".format(src_ip, src_port)
                print("Create Src Port Node: {} {}".format(src_ip, src_port))
                src_port_info["status"] = state
                node_src_port = create_node("PORT", src_port_info)

            # 处理地址为127.0.0.1的远程IP共用端口的问题
            dst_ip_info = {'ip': dst_ip}
            dst_port_info = {'port': dst_port, "ip": dst_ip, "proto": proto, "name": "{}:{}".format(dst_ip, dst_port)}

            if dst_ip in ["127.0.0.1", "::ffff:127.0.0.1", "::1"]:
                dst_port_info["hostname"] = hostname
                dst_port_info["host_id"] = host_id

            node_dst_ip = query_node("IP", dst_ip_info)
            node_dst_port = query_node("PORT", dst_port_info)
            if not node_dst_port:
                # print("Create Dst Port Node: {} {}".format(dst_ip, dst_port))
                dst_port_info["status"] = state
                node_dst_port = create_node("PORT", dst_port_info)

                node_relationship(node_dst_ip, state, node_dst_ip)
                # print("Create Port Relation: {} --> {}".format(dst_ip, dst_port))

            if src_port in host["listen_port"]:
                src = node_dst_port
                dst = node_src_port
                src_ip_port_relation = "LISTEN"
                dst_ip_port_relation = "REQUEST"
            else:
                dst = node_dst_port
                src = node_src_port
                src_ip_port_relation = "REQUEST"
                dst_ip_port_relation = "LISTEN"

            node_relationship(src, state, dst)
            print("Creat Port Relation: {}:{} --> {}:{}".format(src["ip"], src["port"], dst["ip"], dst["port"]))

            node_relationship(node_dst_ip, dst_ip_port_relation, node_dst_port)
            print("Creat Port Dst Relation: {} {} --> {}:{}".format(node_dst_ip["ip"], dst_ip_port_relation, node_dst_port["ip"], node_dst_port["port"]))

            # print(node_src_ip, node_src_port)
            node_src_ip = query_node("IP", {"ip": src_ip, "hostname": hostname})
            node_relationship(node_src_ip, src_ip_port_relation, node_src_port)
            print("Creat Port Src Relation: {} {} --> {}:{}".format(node_src_ip["ip"],src_ip_port_relation,  node_src_port["ip"], node_src_port["port"]))

@app.route('/')
def index():
    return render_template('index.html')

# 接收前端上传的青藤云数据
@app.route('/uploadqty', methods=['POST'])
def upload_qty():
    if request.method == 'POST':
        graph.delete_all()
        f = request.files.get('file', None)  # Flask中获取文件
        source = "json"
        items = f.read()
        try:
            items = json.loads(items)
        except Exception as e:
            source = "txt"

        host = {"hostname": None, "listen_port": set(), "listen_ip": set()}  # 当前处理的主机
        records = []  # 网络连接记录

        for item in items:
            print(items)
            if item["hostname"] != host["hostname"]:
                if host["hostname"]:
                    # handler_host(host, records)
                    records = []
                    host["listen_port"] = set()
                    host["listen_ip"] = set()

                host["name"] = item["hostname"]
                for key in ["hostname", "host_id", "external_ip", "display_ip", "internal_ip"]:
                    host[key] = item[key]

            # 添加记录
            records.append(item)

            # 监听IP
            for key in ["external_ip", "display_ip", "internal_ip"]:
                if item[key]:
                    host["listen_ip"].add(item[key])

            src_ip = item["local_ip"]
            if src_ip not in ['::', '::1', '0.0.0.0'] and "127.0.0." not in src_ip:
                host["listen_ip"].add(src_ip)

            # 监听端口
            if item["state"] in ["LISTEN", "UNCONN"]:
                host["listen_port"].add(item["local_port"])

        if records:
            return handler_host(host, records)



# 解析前端上传的NETSTAT数据 （未完成）
# @app.route('/uploadnetstat', methods=['POST'])
# def upload_netstat():
#     net_data = {}
#     if request.method == 'POST':
#         file_obj = request.files.get('file', None)  # Flask中获取文件
#         #data = json.loads(request.get_data())
#         if file_obj is None:
#             return "未上传文件"
#         for line in file_obj.readlines():
#             line = str(line).strip('\r\n')
#             if line.startswith("Proto") or line.startswith(" "):
#                 continue
#             strings = line.split()
#
#             for string in strings:
#
#                 print(string)
#         return ""
#快速查询
@app.route("/show_all_node")
def show_all_node():

    show_all_hosts = request.args.get('show_all_hosts', None)
    show_all_ip = request.args.get('show_all_ip', None)
    show_internal_ip = request.args.get('show_internal_ip', None)
    show_external_ip = request.args.get('show_external_ip', None)
    show_80 = request.args.get('show_80', None)

    show_estab = request.args.get("show_estab", None)
    show_listen = request.args.get("show_listen", None)
    show_request = request.args.get("show_request", None)
    show_unconn = request.args.get("show_unconn", None)
    internal_to_external = request.args.get("internal_to_external", None)
    node_limit = request.args.get("node_limit", None)

    internal_ip = "192.168.*|30.*|10.*|172.16.*"
    all_internal_ip = "192.168.*|30.*|10.0.*|10.10.*|::ffff:192.168.*|::ffff:30.*|::ffff:10.0.*|127.0.0.1.*|::1.*|::ffff:127.0.*|::ffff:10.10.*|172.16.*|::ffff:172.16.*"
    localhost_ip = "127.0.0.*|::1.*|::ffff:127.0.0.*"

    #快速查询所有主机
    if show_all_hosts:

        nodes, edges = buildPath(cypherStr='match p=(a:HOST) return p')
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    # 快速查询所有IP
    if show_all_ip:

        nodes, edges = buildPath(cypherStr='match p=((a:IP)-[re:connect]->(b:IP)) return p limit 30')
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    # 快速查询所有内网IP
    if show_internal_ip:
        nodes, edges = buildPath(cypherStr='match p=(n:IP) where n.ip=~"{}" return p'.format(internal_ip))
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    # 快速查询所有外网IP
    if show_external_ip:
        nodes, edges = buildPath(cypherStr='match p=(n:IP)-[re]-(b:PORT) where not n.ip=~"{}" return p'.format(all_internal_ip))
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    # 快速查询80端口
    if show_80:
        nodes, edges = buildPath(cypherStr='match p=((a:IP)-[re]->(b:PORT)-[re1]-(c:PORT)-[re2]-(d:IP)) where b.port=80 return p limit 500')
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    # 状态查询
    if show_estab:
        nodes, edges = buildPath(cypherStr='MATCH p=(()-[r:ESTAB]->()) RETURN p LIMIT 100')
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    if show_listen:
        nodes, edges = buildPath(cypherStr='MATCH p=()-[r:LISTEN]->() RETURN p LIMIT 100')
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    if show_request:
        nodes, edges = buildPath(cypherStr='MATCH p=()-[r:REQUEST]->() RETURN p LIMIT 100')
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    if show_unconn:
        nodes, edges = buildPath(cypherStr='MATCH p=()-[r:UNCONN]->() RETURN p LIMIT 100')
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    if internal_to_external:
        nodes, edges = buildPath(cypherStr='match p=((a:IP{ip:"%s"})-[r:bind|UNCONN|REQUEST|ESTAB|LISTEN*1..7]-(b:IP{ip:"%s"})) WHERE a.ip=~ return p limit 3')
        return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

#路径/节点/网段查询
@app.route('/json')
def get_graph():

    # 节点查询参数
    single_host_node = request.args.get("single_host", None)
    single_ip_node = request.args.get("single_ip", None)
    single_port_node = request.args.get("single_port", None)

    # 路径查询参数
    node_from = request.args.get("from", None)
    node_to = request.args.get("to", None)
    port = request.args.get("port", None)
    service = request.args.get("process", None)
    proto = request.args.get("protocol", None)

    # 主机路径查询参数
    host_from = request.args.get("host_from",None)
    host_to = request.args.get("host_to", None)

    #单选框数据
    path = request.args.get('path', None)
    type = request.args.get('type', None)
    host_path_filter = request.args.get('host_path_filter', None)
    ip_node_check = request.args.get('ip_node', None)

    # 网段查询参数
    segment = request.args.get('segment', None)
    segment_filter = request.args.get('segment_filter', None)

    ############################################################CYPHER查询语句#################################################
    # ------------------------------------------------网段查询
    if type == 'network_segment':
        if segment:
            #网段查询选项 -> 显示网段内所有主机/显示网段内IP
            if segment_filter == 'show_segment_host':
                nodes, edges = buildPath(cypherStr='match p=(a:HOST) where a.display_ip contains "%s" return p' % (segment))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})


            nodes, edges = buildPath(cypherStr='match p=((a:IP)-[re]-(m:PORT)) where a.ip contains "%s" return p limit 50' %(segment))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    # ------------------------------------------------主机路径查询
    elif type == 'host_path':
        if host_from and host_to:
            #显示最短路径
            if host_path_filter == 'short_host':
                nodes, edges = buildPath(
                    cypherStr='match p=shortestpath((a:HOST{hostname:"%s"})-[r:bind|UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:HOST{hostname:"%s"})) return p limit 3' % (
                    host_from, host_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})
            #显示所有主句
            if host_path_filter == 'all_host':
                nodes, edges = buildPath(
                    cypherStr='match p=((a:HOST{hostname:"%s"})-[r:bind|UNCONN|REQUEST|ESTAB|LISTEN*1..6]-(b:HOST{hostname:"%s"})) return p limit 10' % (
                    host_from, host_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            nodes, edges = buildPath(cypherStr='match p=((a:HOST{hostname:"%s"})-[r:bind|UNCONN|REQUEST|ESTAB|LISTEN|connect*1..6]-(b:HOST{hostname:"%s"})) return p limit 5' % (host_from, host_to))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})
    # ------------------------------------------------节点查询
    elif type == 'node':

        # 主机节点，IP节点，端口节点同时查询
        if all([single_host_node,single_ip_node,single_port_node]):
            #显示IP关联
            if ip_node_check == 'ip_connect':
                nodes, edges = buildPath(
                    cypherStr='match p=((nc:HOST{hostname:"%s"})-[re1:bind]-(na:IP{ip:"%s"})-[re2:connect]-(nb:IP)) return p ' % (single_host_node, single_ip_node))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})
            nodes, edges = buildPath(
                cypherStr='match p=((na:HOST{hostname:"%s"})-[re]->(nb:IP{ip:"%s"})-[re2]->(nc:PORT{port:%s})) return p limit 20' % (single_host_node, single_ip_node, single_port_node))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

        #同时查询 主机节点 + IP节点
        elif all([single_host_node, single_ip_node]):
            # 显示IP关联
            if ip_node_check == 'ip_connect':

                nodes, edges = buildPath(
                    cypherStr='match p=((nc:HOST{hostname:"%s"})-[re1:bind]-(na:IP{ip:"%s"})-[re2:connect]-(nb:IP)) return p ' % (single_host_node, single_ip_node))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            nodes, edges = buildPath(
                cypherStr='match p=((na:HOST{hostname:"%s"})-[re]->(nb:IP{ip:"%s"})-[re2]->(nc:PORT)) return p limit 20' % (single_host_node,single_ip_node))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

        # 同时查询 端口节点 + IP节点
        elif all([single_port_node, single_ip_node]):

            nodes, edges = buildPath(
                cypherStr='match p=((na:IP{ip:"%s"})-[re]->(nb:PORT{port:%s})-[re1]-(nc:PORT)-[re3]-(nd:IP)) return p limit 20' % (single_ip_node, single_port_node))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

        # 同时查询 端口节点 + 主机节点
        elif all([single_port_node, single_host_node]):

            nodes, edges = buildPath(
                cypherStr='match p=((na:PORT{port:%s})-[re]-(nb:IP)-[re2]-(nc:HOST{hostname:"%s"})) return p' % (single_port_node, single_host_node))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

        # 查询 主机节点
        elif single_host_node:

            nodes, edges = buildPath(
                cypherStr='match p=((na:HOST{hostname:"%s"})-[re]->(nb:IP)) return p' % (single_host_node))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

        # 查询 IP节点
        elif single_ip_node:
            if ip_node_check == 'ip_connect':
                nodes, edges = buildPath(
                    cypherStr='match p=((na:IP{ip:"%s"})-[re:connect]-(nb:IP)) return p limit 50 ' % (single_ip_node))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            nodes, edges = buildPath(
                cypherStr='MATCH p=(n:IP {ip: "%s"})-[re]->(m:PORT) RETURN p limit 100' % (single_ip_node))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

        # 查询端口节点
        elif single_port_node:
            nodes, edges = buildPath(
                cypherStr='match p=((na:PORT{port:%s})-[re]-(nb:IP)-[re1]-(nc:IP)) return p limit 80 ' % (single_port_node))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

    #------------------------------------------------IP 路径查询
    elif type == 'path':
        #查询 原IP + 目的IP 路径
        if all([node_from, node_to]):
            #包括 端口，服务，协议 作为过滤条件
            if all([port and service and proto]):
                nodes, edges = buildPath(
                     cypherStr='match (c:PORT{port:%s,process:"%s",proto:"%s"}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP{ip:"%s"})) where c in nodes(p) return p limit 2' % (
                     port, service, proto, node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            # 包括 端口，服务 作为过滤条件
            elif all([port and service]):
                nodes, edges = buildPath(
                     cypherStr='match (c:PORT{port:%s,process:"%s"}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP{ip:"%s"})) where c in nodes(p) return p limit 2' % (
                         port, service, node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            # 包括 服务，协议 作为过滤条件
            elif all([service and proto]):
                nodes, edges = buildPath(
                     cypherStr='match (c:PORT{process:"%s",proto:"%s"}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP{ip:"%s"})) where c in nodes(p) return p limit 2' % (
                         service, proto, node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            # 包括 端口，协议 作为过滤条件
            elif all([port and proto]):
                nodes, edges = buildPath(
                     cypherStr='match (c:PORT{port:%s,proto:"%s"}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP{ip:"%s"})) where c in nodes(p) return p limit 2' % (
                         port, proto, node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            #仅端口作为条件
            elif port:
                nodes, edges = buildPath(
                     cypherStr='match (c:PORT{port:%s}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP{ip:"%s"})) where c in nodes(p) return p limit 2' % (
                         port, node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            # 仅服务作为条件
            elif service:
                nodes, edges = buildPath(
                     cypherStr='match (c:PORT{process:"%s"}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP{ip:"%s"})) where c in nodes(p) return p limit 2' % (
                         service, node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})
            # 仅协议作为条件
            elif proto:
                nodes, edges = buildPath(
                     cypherStr='match (c:PORT{proto:"%s"}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP{ip:"%s"})) where c in nodes(p) return p limit 2' % (
                         proto, node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            # 显示最短路径
            elif path == 'short':
                nodes, edges = buildPath(
                    cypherStr='match p=shortestpath((a:IP{ip:"%s"})-[r:bind|UNCONN|REQUEST|ESTAB|LISTEN*1..20]-(b:IP{ip:"%s"})) return p limit 3' % (node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            #显示所有路径
            elif path == 'all':
                nodes, edges = buildPath(
                    cypherStr='match p=((a:IP{ip:"%s"})-[r:bind|UNCONN|REQUEST|ESTAB|LISTEN*1..9]-(b:IP{ip:"%s"})) return p limit 30' % (node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            #显示IP关联
            elif path == 'ip_only':
                nodes, edges = buildPath(
                    cypherStr='match p=((a:IP{ip:"%s"})-[r:connect*1..4]-(b:IP{ip:"%s"})) return p limit 8' % (
                    node_from, node_to))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            #默认输出
            nodes, edges = buildPath(
                cypherStr='match p=((a:IP{ip:"%s"})-[r:bind|UNCONN|REQUEST|ESTAB|LISTEN*1..7]-(b:IP{ip:"%s"})) return p limit 3' % (node_from, node_to))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

        #如果只输入了 原IP
        if node_from:
            if port:

                nodes, edges = buildPath(
                    cypherStr='match (c:PORT{port:%s}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP)) where c in nodes(p) RETURN p limit 30' % (port,node_from))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            if proto:
                nodes, edges = buildPath(
                    cypherStr='match (c:PORT{proto:"%s"}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP)) where c in nodes(p) RETURN p limit 30' % (proto, node_from))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

            if service:
                nodes, edges = buildPath(
                    cypherStr='match (c:PORT{process:"%s"}) match p=((a:IP{ip:"%s"})-[r:UNCONN|REQUEST|ESTAB|LISTEN*1..8]-(b:IP)) where c in nodes(p) RETURN p limit 30' % (service, node_from))
                return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})


            nodes, edges = buildPath(cypherStr='MATCH p=((n:IP {ip: "%s"})-[re:UNCONN|REQUEST|ESTAB|LISTEN*..2]-(m:PORT)-[re2:UNCONN|REQUEST|ESTAB|LISTEN*..2]-(k:PORT)-[re3:UNCONN|REQUEST|ESTAB|LISTEN*..2]-(o:IP)) RETURN p limit 30' % (node_from))
            return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})

        # 查看所有主机信息
    # else:
    #     nodes, edges = buildPath(cypherStr='match p=((na:HOST)-[re]->(nb:IP)-[re1]->(nc:IP)) return p limit 80')
    #     return jsonify(elements={"nodes": list(nodes), "edges": list(edges)})


if __name__ == '__main__':
    app.run(debug=True)


