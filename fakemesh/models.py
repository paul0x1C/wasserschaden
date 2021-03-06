import random, os

class Node:
    def __init__(self, id, gateway):
        self.id = id
        self.gateway = gateway
        self.open = False
        self.connected = False
    def handle_msg(self, msg):
        if msg == "ping":
            self.gateway.send(self.id, "pong")
            print("opening", self.id)
        elif msg == "open":
            self.open = True
            self.gateway.send(self.id, "opening")
        elif msg == "close":
            self.open = False
            self.gateway.send(self.id, "closing")
            print("closing", self.id)
        else:
            print("not handeling", msg)
    def connect(self):
        self.connected = True
        self.gateway.send(self.id, "online")

class Group:
    # generates random nodes
    def __init__(self, gateway, n_nodes):
        self.nodes = []
        self.gateway = gateway
        for i in range(n_nodes):
            node_id = random.randint(1e8, 1e12)
            node = gateway.add_node(node_id)
            self.nodes.append(node)
    def connect(self):
        for node in self.nodes:
            node.connect()

class Gateway:
    def __init__(self, topic, send):
        self.topic = topic
        self.nodes = []
        self.node_ids = []
        self.send = send
    def add_node(self, node_id):
        node = Node(node_id, self)
        self.nodes.append(node)
        self.node_ids.append(node_id)
        return node
    def handle_msg(self, topic, msg):
        to = topic.split('/')[2]
        if to == "broadcast":
            for node in self.nodes:
                node.handle_msg(msg)
        elif to == "gateway":
            self.send("gateway","pong")
        else:
            node_id = int(to)
            try:
                index = self.node_ids.index(node_id)
            except:
                print("Node %s not found" % node_id)
            else:
                self.nodes[index].handle_msg(msg)
