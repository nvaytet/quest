import collections


class Team(collections.UserDict):

    def __init__(self, creator: str, **kwargs):
        super().__init__(kwargs)
        self.creator = creator

    def reset_team(self):
        """
        A stud method which can be used  to reset states if needed.
        """
        pass
