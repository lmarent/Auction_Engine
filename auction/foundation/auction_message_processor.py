from abc import ABC
from abc import abstractmethod
from python_wrapper.ipap_message import IpapMessage

class AuctionMessageProcessor(metaclass=ABC):

    def __init__(self):
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


    @abstractmethod
    async def process_message(self, ws, msg : str):
        """
        Process a message arriving from an agent.

        :param ws: web socket used for communicating with the agent
        :param msg: message
        :return:
        """

    async def send_message(self, ws, message: str):
        """
        Sends the message for an agent thought the websocket ws

        :param message: message to be send
        :param ws: web socket to be used to send the message.
        """
