


def activate_auctions(app, auctions : list):
    """
    Activte auctions
    :param app:
    :param auctions:
    :return:
    """


def handle_get_info(app):
    """
    Get the information of the application
    :param app:
    :return:
    """


def handle_add_resource(Event * e, fd_sets_t * fds):
    """
    Handle adding a new resource to the auction server
    """


def handle_add_bidding_objects(Event * e, fd_sets_t * fds):
    """
    Handle adding a new bidding object to the auction server
    """


def handle_add_auctions(Event * e, fd_sets_t * fds):
    """
    Handle adding new auctions to the auction server
    """


def handle_add_bidding_objects_cntrl_comm(Event * e, fd_sets_t * fds):
    """
    Handle adding bidding objects by the http interface.
    """


def handle_add_bidding_objects_auction(Event * e, fd_sets_t * fds):
    """
    Handle adding new bidding objects to an auction.
    """


def handle_activate_bidding_objects(Event * e, fd_sets_t * fds):
    """
    Handle activating a bidding object
    """


def handle_activate_auction(Event * e, fd_sets_t * fds):
    """
    Handle the activation of an auction
    """


def handle_remove_auctions(Event * e, fd_sets_t * fds):
    """
    Handle the auction removal.
    """


def handle_remove_bidding_objects(Event * e, fd_sets_t * fds):
    """
    Handle the removal of a bidding object
    """


def handle_remove_bidding_objects_auction(Event * e, fd_sets_t * fds):
    """
    Handle the removal of a bidding object from an auction
    """


def handle_proc_modele_timer(Event * e, fd_sets_t * fds);


def handle_push_execution(Event * e, fd_sets_t * fds);


def handle_single_check_session(string sessionId,
                        anslp::mspec_rule_key
                        key, anslp::anslp_ipap_message * ipap_mes,
                        anslp::objectList_t * objectList);


def handle_create_check_session(Event * e, fd_sets_t * fds);


def handle_single_create_session(string
sessionId,
anslp::mspec_rule_key
key, anslp::anslp_ipap_message * ipap_mes,
            anslp::objectList_t * objectList);


def handle_create_session(Event * e, fd_sets_t * fds);


def handle_remove_session(Event * e, fd_sets_t * fds);


def handle_single_object_auctioning_interaction(string
sessionId, anslp::anslp_ipap_message * ipap_mes);


def handle_auctioning_interaction(Event * e, fd_sets_t * fds);


def handle_add_generated_bidding_objects(Event * e, fd_sets_t * fds);


def handle_transmit_bidding_objects(Event * e, fd_sets_t * fds);
