class Event:
    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in kwargs.items():
            self.__dict__[k] = v
