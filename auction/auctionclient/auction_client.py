import asyncio
import functools
from .resource_request import ResourceRequest
 
def event_handler(loop, stop=False):
    print('Event handler called')
    if stop:
        print('stopping the loop')
        loop.stop()


def handle_add_resource_request(app, filename):
    resource_request = ResourceRequest(app['config']['TimeFormat'])
    resource_request.from_xml(filename)


# def handle_remove_resource_request_interval():

# def handle_activate_resource_request_interval():

# def handle_push_execution();

# def handle_remove_push_execution():

# def handle_add_generate_bidding_objects():

# def handle_activate_bidding_objects():

# def hdnale_remove_bidding_objects():

# def handle_transmite_bidding_objects():

# def handle_add_actions():

# def handle_activate_auctions():

# def handle_remove_auctions():

def hndle_stop(loop):
    loop.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        # Read the configuration file
        app['config'] = config

        # Read request file.


        # schedule resource request event for auctioning with those resources.
        loop.call_soon(functools.partial(event_handler, loop))

        print('starting event loop')
        loop.call_soon(functools.partial(event_handler, loop))
        current_time = loop.time()
        new_time = current_time + 60
        print('wait', current_time, new_time)
        loop.call_at(new_time, event_handler, loop, True)
        loop.run_forever()
    finally:
        print('closing event loop')
        loop.close()