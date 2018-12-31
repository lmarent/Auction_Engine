from enum import Enum
import ipaddress
import random

U32INT_MAX = 4294967295


class SessionState(Enum):
    SS_NEW = 0
    SS_VALID = 1
    SS_ACTIVE = 2
    SS_DONE = 3
    SS_ERROR = 4


class Session:
    """
    This class represents the sessions used to auction. 

    Attributes
    sender_addres: Sender host address.
    receiver_addres: Receiver host address.
    source_address: Source address.
    sender_port: Sneder port
    receiver_port: Receiver port
    protocol : Protocol being used
    """

    def __init__(self, session_id: str, sender_address: str, sender_port: int,
                 receiver_address: str, receiver_port: int, protocol: int):
        self.session_id = session_id
        self.session_state = SessionState.SS_NEW
        self.pending_messages = {}
        self.sender_address = ipaddress.ip_address(sender_address)
        self.receiver_address = ipaddress.ip_address(receiver_address)
        self.sender_port = sender_port
        self.receiver_port = receiver_port
        self.protocol = protocol
        self.next_message_id = random.randrange(0, U32INT_MAX)

    def get_key(self):
        """
        Gets the key of the session
        """
        return self.session_id

    def set_state(self, session_state: SessionState):
        """
        Sets the session's state
        """
        self.session_state = session_state

    def confirm_message(self, uid: int):
        """
        Confirms the message as acknowledged by the auction server.
        """
        if uid in self.pending_messages:
            del self.pending_messages[uid]
        else:
            raise ValueError('Message with key: {0} is not pending in tne session'.format(str(uid)))

    def add_pending_message(self, message):
        """
        Adds a new message to be acknowledged by the auction server
        """
        self.pending_messages[message.get_key()] = message

    def get_next_message_id(self):
        """
        Gets the next message identifier to be used for building the next message to send.
        """
        if (self.next_message_id + 1) == U32INT_MAX:
            self.next_message_id = 0
        else:
            self.next_message_id = self.next_message_id + 1
        return self.next_message_id
