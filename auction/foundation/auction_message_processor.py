from abc import ABC
from abc import abstractmethod
from python_wrapper.ipap_message import IpapMessage


class AuctionMessageProcessor(metaclass=ABC):

    def __init__(self,domain: int):
        self.domain = domain
        pass

    def is_auction_message(self, msg: str) -> IpapMessage:
        """
        Establishes whether the given message is a valid auction message.

        :param msg: message to verify
        :return: An IpapMessage if it is a valid message, None otherwise.
        """
        # parse the message
        ipap_message = IpapMessage()
        ret = ipap_message.ipap_import(msg)

        if ret:
            # if the parsing could be done, then it is valid auction message
            return ipap_message
        else:
            # else is not a valid message.
            return None

    def build_syn_message(self, sequence_nbr: int) -> IpapMessage:
        """
        Builds a syn message to start a connection

        :param sequence_nbr: sequence number for the message
        :return: message with the syn flag set
        """
        message = IpapMessage(domain_id=self.domain, ipap_version=0, _encode_network=True)
        message.set_syn(True)
        message.set_seqno(sequence_nbr)
        message.set
        return message

    async def build_fin_message(self, sequence_nbr: int, ack_nbr: int) -> IpapMessage:
        """
        Builds a fin message to teardown a connection
        :param sequence_nbr: sequence number for the message
        :param ack_nbr: ack number to send within the message
        :return: message with the fin flag set
        """
        message = IpapMessage(domain_id=self.domain, ipap_version=0, _encode_network=True)
        message.set_fin(True)
        message.set_seqno(sequence_nbr)
        message.set_ack(ack_nbr)
        return message

    async def build_syn_ack_message(self, sequence_nbr: int, ack_nbr: int) -> IpapMessage:
        """
        Builds an ack to respond syn_ack message
        :param sequence_nbr: sequence number for the message
        :param ack_nbr: ack number to send within the message
        :return:
        """
        message = IpapMessage(domain_id=self.domain, ipap_version=0, _encode_network=True)
        message.set_syn(True)
        message.set_ack(True)
        message.set_seqno(sequence_nbr)
        message.set_ack(ack_nbr)
        return message

    async def build_ack_message(self, sequence_nbr: int, ack_nbr: int) -> IpapMessage:
        """
        Builds an ack to respond other messages
        :param sequence_nbr: sequence number for the message
        :param ack_nbr: ack number to send within the message
        :return:
        """
        message = IpapMessage(domain_id=self.domain, ipap_version=0, _encode_network=True)
        message.set_ack(True)
        message.set_seqno(sequence_nbr)
        message.set_ack(ack_nbr)
        return message
