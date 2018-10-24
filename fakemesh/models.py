class Node:
    def __init__(self, id, gateway):
        self.id = id
        self.gateway = gateway
        self.open = False
        self.connected = False
    def handle_msg(self, msg):
        if msg == "ping":
            return "pong|" + str(int(self.open))
        elif msg == "open"
            self.open = True
            return "opening valve"
        elif msg == "close"
            self.open = False
            return "closing valve"
    def connect(self):
        self.connected = True
        return "con|" + str(int(self.open))

class Gateway:
    def __init__(self, topic):
        self.topic = topic
        self.nodes = []
    def add_node(self, node, node_id):
        self.nodes.append(Node(node_id, self))
    def handle_msg(self, topic, msg):
        node_id = topic.split('/')[2]
        try:
            index = self.node.index(node_id)
        except:
            return "Node %s not found" % node_id
        else:
            return self.nodes[index].handle_msg(msg)
