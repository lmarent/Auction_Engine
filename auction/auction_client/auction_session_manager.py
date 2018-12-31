from foundation.session_manager import SessionManager
from auction_client.auction_session import AuctionSession
import uuid


class AuctionSessionManager(SessionManager):

    def __init__(self):
        super(AuctionSessionManager, self).__init__()

    def _create_agent_session(self, session_id: str, s_sender_address: str, s_destin_address: str,
                              sender_port: int, destin_port: int,
                              protocol: int, life_time: int) -> AuctionSession:
        """
        Creates a new session with the same session Id given

        Sessions with the same id must be understood as sessions that belong to the same request,
        but with different destination.

        :param session_id:          Session id
        :param s_sender_address:    Sender address for the session
        :param s_destin_address:    Destination address for the session
        :param sender_port:         Sender port for the session
        :param destin_port:         Destination por for the session
        :param protocol:            Sender protocol for the session
        :param life_time:           life time for the session.
        :return:
        """
        agent_session = AuctionSession(session_id, s_sender_address, s_destin_address,
                                       sender_port, destin_port, protocol, life_time)

        self.add_session(agent_session)
        return agent_session

    def create_agent_session(self, s_sender_address: str, s_destin_address: str,
                             sender_port: int, destin_port: int,
                             protocol: int, life_time: int) -> AuctionSession:
        """
        Creates a new session with the same session Id given

        Sessions with the same id must be understood as sessions that belong to the same request,
        but with different destination.

        :param s_sender_address:    Sender address for the session
        :param s_destin_address:    Destination address for the session
        :param sender_port:         Sender port for the session
        :param destin_port:         Destination por for the session
        :param protocol:            Sender protocol for the session
        :param life_time:           life time for the session.
        :return:
        """
        session_id = str(uuid.uuid1())
        return self._create_agent_session(session_id, s_sender_address, s_destin_address,
                                          sender_port, destin_port, protocol, life_time)
