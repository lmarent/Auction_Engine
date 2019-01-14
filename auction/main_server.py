from auction_server.server import AuctionServer


if __name__ == '__main__':

    agent = AuctionServer()
    agent.run()
    # agent.loop.close()
