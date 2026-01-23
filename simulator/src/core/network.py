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
    def broadcast(cls, sender: "Node", message):
        """
        Broadcasts the message from sender to all the nodes in the network
        The message is received only by other nodes, who are in RECEIVE mode
        Packegt has additional propagration delay as well as chance of being lost
        """
        yield sender.env.timeout(*PROP_DELAY_RANGE)
        for node in cls.nodes:
            if node.id == sender.id:
                continue
            if node.state != Mode.RECEIVE:
                continue
            if random.random() > PT_LOSS:
                node.env.process(node.receive(message)) 
                cls.mailboxes[node.id].append(message)
    
    @classmethod
    def messages_received_from(cls, node: "Node"):
        """
        Returns the ids of all nodes it received the messages from during a specific period
        """
        ids = [msg['id'] for msg in cls.mailboxes[node.id]]
        cls.mailboxes[node.id] = []
        return ids