import networkx as nx

class DijkstraRouting:
    def __init__(self, net):
        self.net = net
        self.graph = self.build_graph()

    def build_graph(self):
        G = nx.Graph()
        for link in self.net.links:
            node1, node2 = link.intf1.node.name, link.intf2.node.name
            G.add_edge(node1, node2, weight=1)  # Assuming all links have equal weight
        return G

    def compute_routes(self):
        routes = {}
        for node in self.graph.nodes():
            routes[node] = nx.single_source_dijkstra_path(self.graph, node)
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