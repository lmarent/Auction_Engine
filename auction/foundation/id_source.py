

class IdSource:
    """

    Attributes
    ----------
    Unique: bool : if unique is set to true, ids should be unique until we wrap around 2^16

    """
    def __init__(self):
        self.num = 0
        self.unique = False
        self.free_ids = []
        self.ids_reserved = []

    def new_id(self) -> int:
        """

        :return:
        """
        if len(self.free_ids) == 0:
            self.num = self.num + 1

            while True:
                if self.num in self.ids_reserved:
                    self.num = self.num + 1
                else:
                    return self.num
        else:
            id = self.free_ids.pop(0)
            return id

    def free_id(self, id_to_release: int ):
        """

        :param id_to_release:
        :return:
        """
        if not self.unique:
            self.free_ids.append(id)
            self.num = self.num - 1


