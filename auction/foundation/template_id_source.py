from foundation.singleton import Singleton

class TemplateIdSource(metaclass=Singleton):
    """
    The TemplateIdSource class can generate unique 16 bit integer numbers to be
    used by other functions. A single number can be lent from the pool of
    available numbers, and this number will not be generated by a call to
    the newId function until it has been released with a call
    to the freeId function.

    Attributes
    ----------
    num:          last number given when no ids in the free pool
    unique:       whether or not the ids are unique
    free_ids:     list of previously freed (now unused) ids
    id_reserved:  List of ids reserved, so they can not be used.
    """

    def __init__(self, num=255, unique=False):
        self.num = num
        self.unique = unique
        self.ids_Reserved = []
        self.free_ids = []

    def new_id(self) -> int:
        """
        return a new Id value that is currently not in use. This value will be
        marked as used and will not returned by a call to newId unless it has
        been released again with a call to freeId

        :return: returns unique unused id value
        """
        if len(self.free_ids) == 0:
            if self.num == 65535:
                raise ValueError("Maximum template number reached")
            else:
                self.num = self.num + 1

            while True:
                if self.num in self.ids_Reserved:
                    if self.num == 255:
                        raise ValueError("Maximum template number reached")
                    else:
                        self.num = self.num + 1
                else:
                    return self.num
        else:
            id = self.free_ids.pop(0)
            return id


    def free_id(self,id : int):
        """
         The released id number can be reused (i.e. returned by newId) after
        the call to freeId. Do not release numbers that have not been obtained
        by a call to newId this will result in unpredictable behaviour.

        :param id: id value that is to be released for future use
        """

        if not self.unique:
            self.free_ids.append(id)
            self.num = self.num - 1


