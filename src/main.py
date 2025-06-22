import sys
import queue
import enum
from network import Network
from chain import Block, Transaction
from peer import Peer

min_num_peers = 50
max_num_peers = 100


class EventType(enum.Enum):
    BLOCK_SEND = 0
    BLOCK_RECIEVE = 1
    TRANSACTION_SEND = 2
    TRANSACTION_RECIEVE = 3


class Event:

    def __init__(
        self,
        type: EventType,
        peer: Peer,
        message: Block | Transaction,
        time: int
    ) -> None:
        self.event_type = type
        self.peer = peer
        self.message = message
        self.time = time


class DiscreteEventSimulator:

    def __init__(
        self,
        num_peers: int,
        slow_network_perc: int,
        low_cpu_perc: int,
        interval,
        transaction_mean
    ) -> None:
        self.num_peers: int = num_peers
        self.network: Network = Network(
            self.num_peers,
            slow_network_perc/100,
            low_cpu_perc/100,
            interval,
            transaction_mean,
        )
        self.interval = interval
        self.transaction_mean = transaction_mean
        self.time: int = 0
        self.event_queue = queue.Queue()

        self.network.draw()

    def run_simulation(self) -> None:
        while True:
            if self.time % 20000 == 0:
                print(f'Processing for time {self.time}')
                list(self.network.graph.nodes())[0].block_tree.draw(
                    self.time,
                    f'results_{self.interval}_{self.transaction_mean}'
                )
            if self.time >= 200000:
                break
            future_event_queue = queue.Queue()
            for peer in self.network.graph.nodes():
                peer: Peer
                block: None | Block = peer.validate_block_operation()
                if block is not None:
                    self.event_queue.put(
                        Event(EventType.BLOCK_SEND, peer, block, self.time)
                    )
                transaction = peer.validate_transaction_operation(
                    self.num_peers
                )
                if transaction is not None:
                    self.event_queue.put(
                        Event(
                            EventType.TRANSACTION_SEND,
                            peer,
                            transaction,
                            self.time
                        )
                    )
            while not self.event_queue.empty():
                event: Event = self.event_queue.get()
                if event.time <= self.time:
                    match event.event_type:
                        case EventType.BLOCK_SEND:
                            if type(event.message) is Block:
                                self.send_block(event.message, event.peer)
                        case EventType.BLOCK_RECIEVE:
                            if event.message.ID not in event.peer.read_block_IDs:  # Noqa:E501
                                if event.peer.add_block(event.message):
                                    self.event_queue.put(
                                        Event(
                                            EventType.BLOCK_SEND,
                                            event.peer,
                                            event.message,
                                            self.time
                                        )
                                    )
                        case EventType.TRANSACTION_SEND:
                            if type(event.message) is Transaction:
                                self.send_transaction(
                                    event.message,
                                    event.peer
                                )
                        case EventType.TRANSACTION_RECIEVE:
                            if type(event.message) is Transaction:
                                self.recieve_transaction(
                                    event.message,
                                    event.peer
                                )

                else:
                    future_event_queue.put(event)
            self.time += 1
            self.event_queue = future_event_queue

    def recieve_transaction(self, transaction: Transaction, peer: Peer) -> None:  # Noqa:E501
        if transaction.ID not in peer.read_transaction_IDs:
            peer.read_transaction_IDs.add(transaction.ID)
            peer.to_process_transactions.append(transaction)
            self.event_queue.put(
                Event(
                    EventType.TRANSACTION_SEND,
                    peer,
                    transaction,
                    self.time,
                )
            )

    def send_transaction(self, transaction: Transaction, peer: Peer) -> None:
        for reciever in self.network.graph.neighbors(peer):
            latency: int = int(self.network.calculate_lataecy_for_message(
                (peer, reciever),
                1
            ))
            self.event_queue.put(
                Event(
                    EventType.TRANSACTION_RECIEVE,
                    reciever,
                    transaction,
                    self.time + latency,
                )
            )

    def send_block(self, block: Block, peer: Peer) -> None:
        message_size: int = len(block.transaction_list)+1
        for reciever in self.network.graph.neighbors(peer):
            latency: int = int(self.network.calculate_lataecy_for_message(
                (peer, reciever),
                message_size,
            ))
            self.event_queue.put(
                Event(
                    EventType.BLOCK_RECIEVE,
                    reciever,
                    block,
                    self.time + latency
                )
            )


def take_input() -> tuple[int, int, int, int, int]:
    try:
        num_peers, slow_network_perc, low_cpu_perc, interval, transaction_mean = sys.argv[1:]  # Noqa:E501
    except ValueError:
        print('''Usage: python3 main.py arg1 arg2 arg3 arg4
    arg1 : number of peers in network
    arg2 : percentage of peers with slow network
    arg3 : percentage of peers with low CPU power
    arg4 : mean interval for block mining
    arg5 : mean interval for transaction mining''')
        sys.exit()

    try:
        num_peers = int(num_peers)
        slow_network_perc = int(slow_network_perc)
        low_cpu_perc = int(low_cpu_perc)
        interval = int(interval)
        transaction_mean = int(transaction_mean)
    except ValueError:
        print('Error: Command line arguments must be integers')
        sys.exit()

    if not min_num_peers <= num_peers <= max_num_peers:
        print(f'Error: Command line argument 1 (num of peers) must lie in [{min_num_peers}, {max_num_peers}]')  # Noqa:E501
        sys.exit()

    if not 0 <= slow_network_perc <= 100:
        print('Error: Command line argument 2 (percentage of slow network peers) must lie in [0, 100]')  # Noqa:E501
        sys.exit()

    if not 0 <= low_cpu_perc <= 100:
        print('Error: Command line argument 3 (percentage of low CPU power peers) must lie in [0, 100]')  # Noqa:E501
        sys.exit()

    if not interval > 0:
        print('Error: Command line argument 4 (mean mining interval time) must be positive')  # Noqa:E501
        sys.exit()

    if not interval > 0:
        print('Error: Command line argument 5 (mean transaction interval time) must be positive')  # Noqa:E501
        sys.exit()

    return (
        num_peers,
        slow_network_perc,
        low_cpu_perc,
        interval,
        transaction_mean,
    )


DiscreteEventSimulator(*take_input()).run_simulation()
