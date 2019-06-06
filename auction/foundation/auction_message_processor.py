from python_wrapper.ipap_message import IpapMessage


class AuctionMessageProcessor:

    # time in milliseconds
    TIMEOUT_SYN = 3000

    def __init__(self, domain: int):
        self.domain = domain

    @staticmethod
    def is_auction_message(msg: str) -> IpapMessage:
        """
        Establishes whether the given message is a valid auction message.

        :param msg: message to verify
        :return: An IpapMessage if it is a valid message, raise ValueError otherwise.
        """
        return IpapMessage(0, 0, True, msg)


    def build_syn_message(self, sequence_nbr: int) -> IpapMessage:
        """
        Builds a syn message to start a connection

        :param sequence_nbr: sequence number for the message
        :return: message with the syn flag set
        """
        message = IpapMessage(domain_id=int(self.domain), ipap_version=IpapMessage.IPAP_VERSION, _encode_network=True)
        message.set_syn(True)
        message.set_seqno(sequence_nbr)
        return message

    def build_fin_message(self, sequence_nbr: int, ack_nbr: int) -> IpapMessage:
        """
        Builds a fin message to teardown a connection
        :param sequence_nbr: sequence number for the message
        :param ack_nbr: ack number to send within the message
        :return: message with the fin flag set
        """
        message = IpapMessage(domain_id=int(self.domain), ipap_version=IpapMessage.IPAP_VERSION, _encode_network=True)
        message.set_fin(True)
        message.set_seqno(sequence_nbr)
        message.set_ack_seq_no(ack_nbr)
        return message

    def build_syn_ack_message(self, sequence_nbr: int, ack_nbr: int) -> IpapMessage:
        """
        Builds an ack to respond syn_ack message
        :param sequence_nbr: sequence number for the message
        :param ack_nbr: ack number to send within the message
        :return:
        """
        print('build syn ack message {0}.{1}'.format(str(sequence_nbr), str(ack_nbr)))
        message = IpapMessage(domain_id=int(self.domain), ipap_version=IpapMessage.IPAP_VERSION, _encode_network=True)
        message.set_syn(True)
        message.set_ack(True)
        message.set_seqno(sequence_nbr)
        message.set_ack_seq_no(ack_nbr)
        return message

    def build_ack_message(self, sequence_nbr: int, ack_nbr: int) -> IpapMessage:
        """
        Builds an ack to respond other messages
        :param sequence_nbr: sequence number for the message
        :param ack_nbr: ack number to send within the message
        :return:
        """
        message = IpapMessage(domain_id=int(self.domain), ipap_version=IpapMessage.IPAP_VERSION, _encode_network=True)
        message.set_ack(True)
        message.set_seqno(sequence_nbr)
        message.set_ack_seq_no(ack_nbr)
        return message
