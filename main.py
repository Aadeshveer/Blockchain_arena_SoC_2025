import matplotlib.pyplot as plt
import networkx as nx
import random

min_num_peers = 50
max_num_peers = 100
min_degree = 3
max_degree = 6

num_peers = random.randint(min_num_peers, max_num_peers)


class Peer:

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return str(self.id)


class Network:

    def __init__(self):

        # will be used to decide how frequent should higher degree be
        self.extra_edge_fraction = 0.01
        self.graph = nx.Graph()

        # adds all the nodes to graph
        for i in range(num_peers):
            self.graph.add_node(Peer(i))

        # generates the edges until requirements are not met
        self.generate_edges()
        while not self.check_graph():
            self.graph.clear_edges()
            self.generate_edges()

    def generate_edges(self):
        '''
        Assigns edges to the graph based on given degree constraints
        '''
        # First generate a back bone of connected edges between entire graph
        nodes = list(self.graph.nodes)
        random.shuffle(nodes)
        for i in range(num_peers-1):
            self.graph.add_edge(nodes[i], nodes[i+1])

        # Nodes with degree < min_degree ie of high priority
        # it is effectively nodes that need to get more edges
        unsatisfied = list(self.graph.nodes)
        # Nodes with degree < max_degree ie of low priority
        # it is effectively nodes that can get more edges but are satisfied
        satisfied = []
        # Keeps adding edges until all unsatisfied nodes are not finished
        while len(unsatisfied) != 0:

            # always select an unsatisfied edge
            from_node = random.choice(unsatisfied)

            # choose second unsatisfied if availible
            if len(unsatisfied) != 0:
                to_node = random.choice(unsatisfied)

            if len(satisfied) != 0:
                # if satisfied is available
                # use probability to decide (un)satisfied node
                if (
                    random.random() > self.extra_edge_fraction
                    or
                    len(unsatisfied) == 0
                ):
                    to_node = random.choice(satisfied)

            # if both selected are same retry
            if to_node == from_node:
                continue

            self.graph.add_edge(from_node, to_node)

            # locate the unsatisfied node
            if self.graph.degree(from_node) >= min_degree:
                unsatisfied.remove(from_node)
                satisfied.append(from_node)

            # locate the to node based on list it is in
            if to_node in unsatisfied:

                if self.graph.degree(to_node) >= min_degree:
                    unsatisfied.remove(to_node)
                    satisfied.append(to_node)

            elif self.graph.degree(to_node) >= max_degree:
                satisfied.remove(to_node)

    def check_graph(self):
        '''
        Checks if the graph meets all requirements
        '''
        return nx.is_connected(self.graph) and self.degree_check()

    def degree_check(self):
        '''
        Checks the degree of all nodes
        '''
        print("Checking degree")
        for _, degree in self.graph.degree:
            if not min_degree <= degree <= max_degree:
                print("Graph failed degree check")
                return False
        print("Graph passes degree check")
        return True

    def draw(self):
        '''
        Draws the graph and saves it
        '''
        x = [self.graph.degree(node) for node in self.graph.nodes]
        s = [0 for _ in range(max_degree - min_degree + 1)]
        for i in x:
            s[i-min_degree] += 1
        for i in range(max_degree - min_degree + 1):
            print(f"Percentage of {i + min_degree} is {s[i]/sum(s) * 100}")
        nx.draw(
            self.graph,
            with_labels=True,
            linewidths=1,
            edgecolors='black',
            font_size=10,
            font_color='white'
        )
        plt.savefig('network.png')


Network().draw()
