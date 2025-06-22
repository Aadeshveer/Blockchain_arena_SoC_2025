import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import networkx as nx
import numpy as np
import random
import enum
from peer import Peer, CPUPower, NetworkSpeed
from chain import Block

min_degree = 3
max_degree = 6
SCALE = 10


class LatencyTerms(enum.Enum):
    PROPOGATION_DELAY = 0
    MESSAGE = 1
    LINK_SPEED = 2
    QUEUING_DELAY = 3


class Network:

    def __init__(
        self,
        num_peers: int,
        slow_network_frac: float,
        weak_cpu_frac: float,
        interval: int,
        transaction_mean: int
    ) -> None:

        # will be used to decide how frequent should higher degree be
        self.extra_edge_fraction = 0.01
        self.graph = nx.Graph()
        self.num_peers = num_peers
        self.peer_list: list[Peer] = []
        self.genesis_block = Block('Genesis')
        self.interval = interval
        self.transaction_mean = transaction_mean

        # adds all the nodes to graph
        high_power_ctr = 0
        for i in range(self.num_peers):

            if random.random() < weak_cpu_frac:
                cpu_power = CPUPower.LOW
            else:
                cpu_power = CPUPower.HIGH
                high_power_ctr += 1

            if random.random() < slow_network_frac:
                network_speed = NetworkSpeed.SLOW
            else:
                network_speed = NetworkSpeed.FAST

            self.peer_list.append(
                Peer(
                    i,
                    cpu_power,
                    network_speed,
                    self.genesis_block,
                    self.interval,
                    self.transaction_mean,
                )
            )
            self.graph.add_node(self.peer_list[-1])

        for peer in self.peer_list:
            if peer.cpu_power == CPUPower.HIGH:
                peer.set_hashing_power(10/(9*high_power_ctr + num_peers))
            else:
                peer.set_hashing_power(1/(9*high_power_ctr + num_peers))

        # generates the edges until requirements are not met
        self.generate_edges()
        while not self.check_graph():
            self.graph.clear_edges()
            self.generate_edges()

        self.initialize_latency()

    def generate_edges(self):
        '''
        Assigns edges to the graph based on given degree constraints
        '''
        # First generate a back bone of connected edges between entire graph
        nodes = list(self.graph.nodes)
        random.shuffle(nodes)
        for i in range(self.num_peers-1):
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

            if self.graph.degree(from_node) >= min_degree:  # type:ignore
                unsatisfied.remove(from_node)
                satisfied.append(from_node)

            # locate the to node based on list it is in
            if to_node in unsatisfied:

                if self.graph.degree(to_node) >= min_degree:  # type:ignore
                    unsatisfied.remove(to_node)
                    satisfied.append(to_node)

            elif self.graph.degree(to_node) >= max_degree:  # type:ignore
                satisfied.remove(to_node)

    def check_graph(self) -> bool:
        '''
        Checks if the graph meets all requirements
        '''
        return nx.is_connected(self.graph) and self.degree_check()

    def degree_check(self) -> bool:
        '''
        Checks the degree of all nodes
        '''
        print("Checking degree")
        for _, degree in self.graph.degree:  # type:ignore
            if not min_degree <= degree <= max_degree:
                print("Graph failed degree check")
                return False
        print("Graph passes degree check")
        return True

    def initialize_latency(self) -> None:
        for edge in self.graph.edges():
            dic = self.graph.edges[edge]
            if edge[0].network_speed.value + edge[1].network_speed.value == 2:
                dic[LatencyTerms.LINK_SPEED] = 100
            else:
                dic[LatencyTerms.LINK_SPEED] = 5
            dic[LatencyTerms.PROPOGATION_DELAY] = random.randrange(10, 500)

    def calculate_lataecy_for_message(self, edge, message_size):
        link_speed = self.graph.edges[edge][LatencyTerms.LINK_SPEED] * 1000000
        queuing_delay = np.random.poisson(96000/link_speed)
        latency = self.graph.edges[edge][LatencyTerms.PROPOGATION_DELAY]/1000
        latency += message_size*8000/link_speed
        latency += queuing_delay
        return latency*SCALE

    def draw(self) -> None:
        '''
        Draws the graph and saves it
        '''
        x = [self.graph.degree(node) for node in self.graph.nodes]  # type:ignore # Noqa:E501
        s = [0 for _ in range(max_degree - min_degree + 1)]
        color_map = []
        width_list = []
        edge_list = []
        for edge in self.graph.edges():
            fast1 = edge[0].network_speed == NetworkSpeed.FAST
            fast2 = edge[1].network_speed == NetworkSpeed.FAST
            if fast1 and fast2:
                width_list.append(3)
            else:
                width_list.append(1)
        for node in self.graph.nodes():
            if node.cpu_power == CPUPower.HIGH:
                color_map.append('red')
            else:
                color_map.append('blue')
            if node.network_speed == NetworkSpeed.FAST:
                edge_list.append(3)
            else:
                edge_list.append(1)
        for i in x:
            s[i-min_degree] += 1
        for i in range(max_degree - min_degree + 1):
            print(f"Percentage of {i + min_degree} is {s[i]/sum(s) * 100}")

        plt.figure(figsize=(8, 8), dpi=300)
        ax = plt.subplot()
        ax.set_title('Peer Network', size=24)
        text = '''
Red Node: High CPU power
Blue Node: Low CPU power
Thick outline node: High network speed
Thin outline node: Low network speed
Thick line: High speed connection
'''
        box = AnchoredText(text, loc='lower right', frameon=True, pad=0.5)
        ax.add_artist(box)
        nx.draw(
            self.graph,
            pos=nx.spring_layout(self.graph),
            with_labels=True,
            width=width_list,
            linewidths=edge_list,
            edgecolors='black',
            font_size=10,
            font_color='white',
            node_color=color_map,
        )
        plt.tight_layout()
        plt.savefig(f'results_{self.interval}_{self.transaction_mean}/network.png')  # Noqa:E501
        plt.close()
