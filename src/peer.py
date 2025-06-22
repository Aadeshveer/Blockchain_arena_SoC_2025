import enum
from chain import Block, BlockTree, Transaction
import numpy
import random

MINING_FEE = 50
MEAN_TIME = 1
SCALE = 10


class CPUPower(enum.Enum):
    LOW = 0
    HIGH = 1


class NetworkSpeed(enum.Enum):
    SLOW = 0
    FAST = 1


class Peer:

    def __init__(
        self,
        id,
        cpu_power,
        network_speed,
        genesis_block,
        interval,
        transaction_mean
    ) -> None:
        self.id = id
        self.interval_time = interval
        self.transaction_mean = transaction_mean
        self.cpu_power = cpu_power
        self.network_speed = network_speed
        self.block_tree = BlockTree(genesis_block, self.id)
        self.hashing_fraction = 0
        self.money = 0
        self.read_transaction_IDs = set()
        self.to_process_transactions = []
        self.read_block_IDs = set()
        self.block_to_push: None | Block = None
        self.push_in: None | int = None
        self.push_from = None
        self.transact = None
        self.new_transaction: None | Transaction = None

    def generate_block(self) -> None:
        point_of_adding = self.block_tree.find_longest_chain()
        generated_block = Block(self.id, point_of_adding.block.ID)
        ctr = 0
        for transaction in self.to_process_transactions:
            if transaction.sender_ID in point_of_adding.accounts:
                present_money = point_of_adding.accounts[transaction.sender_ID]
                if present_money >= transaction.amount:
                    generated_block.transaction_list.append(transaction)
                    self.to_process_transactions.remove(transaction)
                    ctr += 1
                    if ctr == 1000:
                        break
        generated_block.transaction_list.append(
            Transaction(None, self.id, MINING_FEE)
        )
        time = numpy.random.poisson(
            self.interval_time*SCALE/self.hashing_fraction
        )
        self.push_in = time
        self.block_to_push = generated_block
        self.push_from = point_of_adding

    def validate_block_operation(self) -> None | Block:
        if (self.push_in is None or self.block_tree.find_longest_chain() != self.push_from):  # Noqa:E501
            self.generate_block()
        else:
            self.push_in -= 1
        if self.push_in is not None and self.push_in <= 0:
            if self.block_to_push is not None:
                self.read_block_IDs.add(self.block_to_push.ID)
            self.money += MINING_FEE
            self.add_block(self.block_to_push)
            ready_block = self.block_to_push
            self.generate_block()
            return ready_block
        return None

    def generate_transaction(self, num_peers) -> None:
        if self.money > 0:
            time = numpy.random.poisson(self.transaction_mean*SCALE)
            self.transact = time
            pay_to = random.randint(0, num_peers-1)
            while pay_to == self.id:
                pay_to = random.randint(0, num_peers-1)
            self.new_transaction = Transaction(
                self.id,
                pay_to,
                numpy.random.randint(1, self.money+1)
            )
            self.money -= self.new_transaction.amount

    def validate_transaction_operation(self, num_peers) -> Transaction | None:
        if self.transact is None:
            self.generate_transaction(num_peers)
        else:
            self.transact -= 1
            if self.transact <= 0:
                if self.new_transaction is not None:
                    self.to_process_transactions.append(self.new_transaction)
                    self.read_transaction_IDs.add(self.new_transaction.ID)
                ready_transaction = self.new_transaction
                self.generate_transaction(num_peers)
                return ready_transaction
        return None

    def set_hashing_power(self, h_k) -> None:
        self.hashing_fraction = h_k

    def __str__(self) -> str:
        return str(self.id)

    def add_block(self, block) -> bool:
        self.read_block_IDs.add(block.ID)
        return self.block_tree.add_block(block)
