import networkx as nx
import random

class BGPRouting:
    def __init__(self, net):
        self.net = net
        self.graph = self.build_graph()
        self.as_numbers = self.assign_as_numbers()

    def build_graph(self):
        G = nx.Graph()
        for link in self.net.links:
            node1, node2 = link.intf1.node.name, link.intf2.node.name
            G.add_edge(node1, node2)
        return G

    def assign_as_numbers(self):
        as_numbers = {}
        for node in self.graph.nodes():
            as_numbers[node] = random.randint(1, 65535)
        return as_numbers

    def compute_routes(self):
        routes = {}
        for src in self.graph.nodes():
            routes[src] = {}
            for dst in self.graph.nodes():
                if src != dst:
                    path = nx.shortest_path(self.graph, src, dst)
                    routes[src][dst] = path
        return routes

    def apply_routing(self):
        routes = self.compute_routes()
        for src in self.net.hosts:
            for dst in self.net.hosts:
                if src != dst:
                    path = routes[src.name][dst.name]
                    if len(path) > 1:
                        next_hop = path[1]
                        src.cmd(f'route add -host {dst.IP()} gw {self.net.get(next_hop).IP()}')

    def get_next_hop(self, source, destination):
        routes = self.compute_routes()
        path = routes[source][destination]
        return path[1] if len(path) > 1 else destination