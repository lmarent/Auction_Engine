#auctioning_object.py

class AuctioningObject():
    """
    Defines common attributes and methods used for auctioning object. An auctioning object
    represents an abtract class of all objects  being exchanged in the auction.
    """
    AUCTIONING_OBJECT_STATE = (
        (0, 'NEW'),
        (1, 'VALID'),
        (2, 'SCHEDULED'),
        (3, 'ACTIVE'),
        (4, 'DONE'),
        (5, 'ERROR')
    )

    def __init__(self, key, state=0):
        self.state = state
        self.key = key

    def set_state(self,state):
        """
        Change the object's state.
        """
        self.state = state
    
    def get_state(self):
        """
        Return object's state.
        """		
        return self.state

    def get_key(self):
        """
        Return object's key.
        """     
        return self.key
