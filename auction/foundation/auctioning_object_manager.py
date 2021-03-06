# auctioning_object_manager.py
from foundation.auctioning_object import AuctioningObjectState
from utils.auction_utils import log



class AuctioningObjectManager:
    """
      The auctioningObjectManager class allows to add and remove Auction Objects 
        in the core system. Auctioning objects data are a set of ascii strings that are parsed
        and syntax checked by the auctioningObjectManager and then their respective
        settings are used to configure the other Core components.

    Attributes
    ---------
    domain : int
        This field identifies uniquely the agent.

    """

    def __init__(self, domain:int ):
        self.domain = domain
        self.auctioning_objects = {}
        self.auctioning_objects_done = {}
        self.logger = log().get_logger()

    def add_auctioning_object(self, auctioning_object):
        """
        Adding new bidding objects to the Auction system will parse and syntax
        check the given auction object specifications.

        It look up the database for already installed auction objects
        and store the auction object into the database.
        """
        key = auctioning_object.get_key()
        if key in self.auctioning_objects.keys():
            raise ValueError('Auctioning Object with this name is already installed')

        self.auctioning_objects[key] = auctioning_object
        self.logger.debug("nbr objects after insert {0}:".format(len(self.auctioning_objects)))

    def get_auctioning_object(self, key):
        """
        lookup the database of auction objects for a specific auction object
        """
        if key in self.auctioning_objects.keys():
            return self.auctioning_objects[key]
        else:
            self.logger.debug("nbr objects: {0}".format(len(self.auctioning_objects)))
            for key_found in self.auctioning_objects.keys():
                self.logger.debug("key present: {0}".format(key_found))
            raise ValueError('Auctioning Object {0} does not exist'.format(key))

    def get_auctioning_object_done(self, key):
        """
        Get auction object with key from the stored mark as done.
        """
        if key in self.auctioning_objects_done.keys():
            return self.auctioning_objects_done[key]
        else:
            raise ValueError('Auctioning Object {} does not exist'.format(key))

    def del_actioning_object(self, key):
        """
        Deleting an auction object parses and syntax checks the
        identification string, it tests the presence of the given auction object
        in the database, and it removes the auction object from the database
        """
        if key in self.auctioning_objects.keys():
            del self.auctioning_objects[key]
        else:
            raise ValueError('Auctioning Object {} does not exist'.format(key))

    def store_auctioning_object_done(self, auctioning_object):
        """
        Add the auctioning object to the list of finished bids
        """
        auctioning_object.set_state(AuctioningObjectState.DONE)
        key = auctioning_object.get_key()
        self.auctioning_objects_done[key] = auctioning_object

    def get_num_auctioning_objects(self) -> int:
        """
        Returns the number of current registed auctioning ojects
        :return: number of auctioning objects.
        """
        return len(self.auctioning_objects)

    def get_auctioning_object_keys(self)-> list:
        """
        Returns the keys of the auction objects
        :return: set of keys
        """
        lst_return = []
        for key in self.auctioning_objects.keys():
            lst_return.append(key)

        return lst_return