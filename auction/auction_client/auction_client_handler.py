import asyncio
import functools
from .resource_request import ResourceRequest
from .auction_session import AuctionSession
import ipaddress
 
def event_handler(loop, stop=False):
    print('Event handler called')
    if stop:
        print('stopping the loop')
        loop.stop()


def handle_add_resource_request(app, filename, loop):
    """
    Handle a new resource request. It parsers, adds and triggers the activation of the resource request.
    """
    resource_request = ResourceRequest(app['config']['TimeFormat'])
    resource_request.from_xml(filename)
    resource_request_manager = app.get_resource_request_manager()
    resource_request_manager.add_resource_request(resource_request, loop)


# def handle_remove_resource_request_interval():

def handle_activate_resource_request_interval(app, starttime, resource_request, loop):
    """
	Sends a new message to the auction server to establish an 
    auction session and get the auctions being performed. 
    """
    intervals = resource_request.get_interval_by_start_time(starttime)
    config = app['config']
    if config['useIPV6']:
        local_ip = ipaddress.ip_address(config['LocalAddr-V6'])
    else:
        local_ip = ipaddress.ip_address(config['LocalAddr-V4'])
    port = int(config['ControlPort'])
    session_manager = app.get_session_manager()
    for interval in intervals:
        session = AuctionSession(interval.start, interval.stop,resource_request)
        mid = session.get_next_message_id()
        # TODO: Create message for requesting auctions
        message = get_message_request(mid, request)
        session.add_pending_message(message)
        session_manager.add_session(session)
        interval.set_session(session)
        loop.call_soon(functools.partial(handle_send_message, message, loop))

def handle_remove_resource_request_interval(app, stoptime, resource_request, loop):
    logger.debug('starting handle_remove_resource_request_interval')

    intervals = resource_request.get_interval_by_stop_time(stoptime)
    for interval in intervals:
        session = interval.session
        auctions = session.get_auctions()
        for auction in auctions:
            # TODO: Teardown session.

            # TODO: remove prcess request

            # TODO: If the auction is not being used anymore remove all events.
            auction.decrement_references(session, loop)

    logger.debug('starting handle_remove_resource_request_interval')

def handle_activate_session(app, session_key, loop):
    logger.debug('starting handle_activate_session')
    try:
        session_manager = app.get_session_manager()
        session = session_manager.get_session(session_key)
        session.set_state(SessionState.SS_ACTIVE)
    except Exception as exp:
        logger.error('An error occurs - message: {}'.format(str(exp)))

    logger.debug('ending handle_activate_session')


def handle_push_execution():
    logger.debug('starting handle_push_execution')

    logger.debug('ending handle_push_execution')

def handle_remove_push_execution():
    logger.debug('starting handle_remove_push_execution')

    logger.debug('ending handle_remove_push_execution')

def handle_add_generate_bidding_objects(app, bidding_objects, loop):
    logger.debug('starting handle_add_generate_bidding_objects')

    bidding_manager = app.get_bidding_object_manager()
    for bidding_object in bidding_objects:
        bidding_manager.add_bidding_object(bidding_object, loop)

    logger.debug('ending handle_add_generate_bidding_objects')

def handle_activate_bidding_objects(app, bidding_objects, loop):
    logger.debug('starting handle_activate_bidding_objects')

    for bidding_object in bidding_objects:
        bidding_object.activate(loop)

    logger.debug('ending handle_activate_bidding_objects')

def handle_transmite_bidding_objects(app, bidding_objects, session, loop):
    logger.debug('starting handle_transmite_bidding_objects')

    for bidding_object in bidding_objects:
        auction = bidding_object.get_auction()
        mid = session.get_next_message_id()
        message = get_message_bidding_object(mid, bidding_object)
        session.add_pending_message(message)        
        loop.call_soon(functools.partial(handle_send_message, message, loop))


    logger.debug('ending handle_transmite_bidding_objects')


def hdnale_remove_bidding_objects(app,bidding_objects, loop):
    logger.debug('starting hdnale_remove_bidding_objects')

    bidding_object_manager = app.get_bidding_object_manager()
    for bidding_object in bidding_objects:
        bidding_object_manager.del_bidding_object(bidding_object)

    logger.debug('ending hdnale_remove_bidding_objects')


def handle_activate_auctions(app, auctions, loop):
    logger.debug('starting handle_activate_auctions')

    for auction in auctions:
        auction.activate(loop) 

    logger.debug('ending handle_activate_auctions')

def handle_remove_auctions(app, auctions, loop):
    logger.debug('starting handle_remove_auctions')

    auction_manager = app.get_auction_manager()
    for auction in auctions:

        # remove from processing the auction
        # TODO: Remove from procesing.

        # delete all binding objects related with the auction
        # TODO: remove binding objects

        auction_manager.del_auction(auction)

    logger.debug('ending handle_remove_auctions')

def handle_send_message(message, loop):
    """ 
    Sends a message to the auction server
    """

def handle_receive_message(message, loop):
    """
    Receives a new message from the auction server.
    """

def hndle_stop(loop):
    loop.stop()