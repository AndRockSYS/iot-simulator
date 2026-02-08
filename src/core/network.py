import random

from typing import TYPE_CHECKING, List

from ..config import PT_LOSS, PROP_DELAY_RANGE
from ..node.mode import Mode

if TYPE_CHECKING:
    from ..node.node import Node

class Network:
    nodes: List["Node"] = []
    mailboxes = {}

    @classmethod
    def register_node(cls, node: "Node"):
        """
        Registers node in the network and creates mailbox for it
        """
        cls.nodes.append(node)
        cls.mailboxes[node.id] = []

    @classmethod
    def broadcast(cls, sender: "Node", message: dict):
        """
        Broadcasts the message from sender to all the nodes in the network
        The message is received only by other nodes, who are in RECEIVE mode
        Packet has additional propagration delay as well as chance of being lost
        """
        yield sender.env.timeout(random.uniform(*PROP_DELAY_RANGE))
        for node in cls.nodes:
            if node.id == sender.id:
                continue
            if node.mode != Mode.RECEIVE:
                continue
            if random.random() > PT_LOSS:
                yield node.env.process(node.receive(message)) 
                cls.mailboxes[node.id].append(message)
    
    @classmethod
    def messages_received_from(cls, node: "Node") -> list[int]:
        """
        Returns the ids of all nodes it received the messages from during a specific period
        """
        ids = [msg['from'] for msg in cls.mailboxes[node.id]]
        cls.mailboxes[node.id] = []
        return ids