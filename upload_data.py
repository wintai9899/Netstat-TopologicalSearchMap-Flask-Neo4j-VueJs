import json
import pprint
from hashlib import md5
from py2neo import Graph, Node, Relationship
import datetime


graph = Graph("http://localhost:7474/db/data/")
graph.delete_all()
net_data = {}


def node_relationship(source_node, relation, target_node):
    node_1_relationship_company_region = Relationship(source_node, relation, target_node)
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

def handler_netstat_data(filename):

    with open(filename, 'r') as f:
        lines = f.readlines()
        host = {"hostname": None, "listen_port": set(), "listen_ip": set()}
        record = []

        for line in lines:
            line = line.strip('\n')
            if line.startswith("Proto") or line.startswith(" "):
                continue
            strings = line.split()
            record.append({"local_ip": strings[3].replace("::", '0.0.0.0').split(':')[0],
                           "local_port": strings[3].replace("::", '0.0.0.0').split(':')[1],
                           "foreign_ip": strings[4].replace("::", '.0.0.0.0').split(':')[0],
                           "foreign_port": strings[4].replace("::", '0.0.0.0').split(':')[1],
                           "state": strings[5],
                           "pid":strings[-1].split("/")[0],
                           "process":strings[-1].split("/")[-1],
                           "proto":strings[0]
                           })

        for item in record:

            timestamp = str('{0:%Y%m%d%H%M}'.format(datetime.datetime.now()))
            hash_id = md5(timestamp.encode('utf-8')).hexdigest()
            listen_ip = set()
            listen_port = set()

            src_ip = item["local_ip"]
            src_port = item["local_port"]
            dst_ip = item["foreign_ip"]
            dst_port = item["foreign_port"]
            proto = item["proto"]
            process = item["process"]
            pid = item["pid"]
            state = item["state"]
            hash_id = ''
            src_ip = item["local_ip"]

            if src_ip not in ['::', '::1', '0.0.0.0'] and "127.0.0." not in src_ip:
                listen_ip.add(src_ip)

            # 监听端口
            if item["state"] in ["LISTEN", "UNCONN"]:
                listen_port.add(item["local_port"])
            for ip in listen_ip:
                node_ip = query_node("IP", {"ip": ip})

                if not node_ip:
                    node_ip = create_node("IP", {"ip": ip, "hash_id": hash_id})
                    print("Create IP Node: {} {}".format(ip,hash_id))

                if not node_ip["hostname"]:  # 补充Hostname字段
                    print("Update Node Hostname: {} --> {}".format(node_ip['ip'], hash_id))
                    node_update(node_ip, "hash_id", hash_id)
                    node_update(node_ip, "hash_id", hash_id)

            if src_ip in ["127.0.0.1", "::ffff:127.0.0.1", "::1"]:
                node_src_ip = query_node("IP", {"ip": src_ip})  # 处理127.0.0.1
                if not node_src_ip:
                    node_src_ip = create_node("IP", {"ip": src_ip,"hash_id": hash_id})
                    print("Create Local IP Node: {} {}".format(src_ip, hash_id))

            if dst_ip in ["127.0.0.1", "::ffff:127.0.0.1", "::1"]:
                node_dst_ip = query_node("IP", {"ip": src_ip})
                if not node_dst_ip:
                    node_dst_ip = create_node("IP", {"ip": dst_ip,  "hash_id": hash_id})
                    print("Create Foreign IP Node: {} {}".format(src_ip, hash_id))

            elif dst_ip not in ["0.0.0.0", "::", ".0.0.0.0"]:
                node_dst_ip = query_node("IP", {"ip": dst_ip})
                if not node_dst_ip:
                    node_dst_ip = create_node("IP", {"ip": dst_ip})
                    print("Create Foreign IP Node: {} {}".format(dst_ip,hash_id))    # 创建一个没有Hostname属性的IP节点
                node_src_ip = query_node("IP", {"ip": src_ip, "hash_id":hash_id})




if __name__ == '__main__':
    handler_netstat_data(r"netstat.txt")




