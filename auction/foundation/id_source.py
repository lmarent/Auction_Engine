from foundation.singleton import Singleton


class IdSource(metaclass=Singleton):
    """

    Attributes
    ----------
    unique: bool : if unique is set to true, ids should be unique until we wrap around 2^16

    """

    def __init__(self, unique: bool = False):
        self.num = 0
        self.unique = unique
        self.free_ids = []
        self.ids_reserved = []

    def new_id(self) -> int:
        """

        :return:
        """
        self.num = self.num + 1
        if len(self.free_ids) == 0:
            while True:
                if self.num in self.ids_reserved:
                    self.num = self.num + 1
                else:
                    return self.num
        else:
            id_source = self.free_ids.pop(0)
            return id_source

    def free_id(self, id_to_release: int):
        """

        :param id_to_release:
        :return:
        """
        if not self.unique:
            self.free_ids.append(id_to_release)
            self.num = self.num - 1
