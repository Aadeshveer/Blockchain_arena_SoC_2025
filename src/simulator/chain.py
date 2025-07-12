from collections import deque
import matplotlib.pyplot as plt
import networkx as nx
import copy
from settings import SCALE


class Transaction:

    def __init__(self, sender: int | None, reciever: int, value: int) -> None:
        self.ID: int = id(self)
        self.sender_ID: int | None = sender
        self.reciever_ID: int = reciever
        self.amount: int = value

    def __str__(self) -> str:
        return f'{self.ID}: {self.sender_ID} pays {self.reciever_ID} {self.amount} coins'  # Noqa:E501


class Block:

    def __init__(self, creator: str | int, baseID: int | None = None) -> None:
        self.ID = id(self)
        self.last_block_ID = baseID
        self.creator = creator
        self.transaction_list = []


class TreeNode:

    def __init__(self, block, depth) -> None:
        self.next = []
        self.block: Block = block
        self.depth: int = depth
        self.accounts = {}

    def __str__(self) -> str:
        return f'{self.depth} by {self.block.creator}'


class BlockTree:

    def __init__(self, genesis_block: Block, peer_id: int) -> None:
        self.peer_id = peer_id
        self.root = TreeNode(genesis_block, 0)
        self.node_list = [self.root]

    def find_node_by_ID(self, ID) -> TreeNode | None:
        to_scan_stack = deque()
        to_scan_stack.append(self.root)
        while len(to_scan_stack) != 0:
            node_to_search = to_scan_stack.pop()
            if node_to_search.block.ID == ID:
                return node_to_search
            for node in node_to_search.next:
                to_scan_stack.append(node)
        return None

    def add_block(self, block: Block) -> bool:
        found_node = self.find_node_by_ID(block.last_block_ID)
        if found_node is None or block in found_node.next:
            return False
        if self.validate_transactions(block, found_node):
            new_node = TreeNode(block, found_node.depth+1)
            new_node.accounts = copy.deepcopy(found_node.accounts)
            account = new_node.accounts
            for transaction in block.transaction_list:
                if transaction.reciever_ID not in account:
                    account[transaction.reciever_ID] = 0
                if transaction.sender_ID is not None:
                    account[transaction.sender_ID] -= transaction.amount
                account[transaction.reciever_ID] += transaction.amount
            found_node.next.append(new_node)
            self.node_list.append(new_node)
            return True
        return False

    def find_longest_chain(self):
        max_depth_node = self.root
        for i in self.node_list:
            if max_depth_node.depth < i.depth:
                max_depth_node = i
        return max_depth_node

    def validate_transactions(self, block: Block, last_node: TreeNode) -> bool:
        accounts = last_node.accounts
        for transaction in block.transaction_list:
            if transaction.sender_ID is None:
                return True
            if transaction.sender_ID not in accounts:
                return False
            if accounts[transaction.sender_ID] - transaction.amount < 0:
                return False
        return True

    def draw(self, time: int, result_folder: str, plot_idx: int) -> None:
        graph = nx.Graph()
        cmap = []
        for node in self.node_list:
            graph.add_node(node)
            if node.depth == 0:
                cmap.append('red')
            else:
                cmap.append('lightblue')
        draw_stack = deque()
        draw_stack.append(self.root)
        while len(draw_stack) != 0:
            root = draw_stack.pop()
            for node in root.next:
                graph.add_edge(root, node)
                draw_stack.append(node)
        plt.figure(figsize=(8, 8), dpi=600)
        plt.title(
            f'Block chain Tree for peer {self.peer_id} at timestep {time/SCALE}'  # Noqa:E501
        )
        nx.draw(
            graph,
            pos=nx.spring_layout(graph, iterations=100),
            with_labels=True,
            node_size=max(300-graph.number_of_nodes()*5, 30),
            font_size=max(8-int(graph.number_of_nodes()/15), 4),
            node_color=cmap,
        )
        plt.savefig(result_folder+f'/blockchain{plot_idx}.png')
        plt.close()
