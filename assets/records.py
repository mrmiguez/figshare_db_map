class Record(object):

    def __init__(self):
        object.__init__(self)

    def __contains__(self, key):
        if key in self.__dict__.keys():
            return True
        else:
            return False

    def __iter__(self):
        for k in self.__dict__.keys():
            yield k

    def __delitem__(self, key):
        if key in self.__dict__.keys():
            del self.__dict__[key]
        else:
            raise KeyError

    def __getitem__(self, item):
        if item in self.__dict__.keys():
            return self.__dict__[item]
        else:
            raise KeyError

    def __setattr__(self, key, value):
        if value:
            self.__dict__[key] = value

    def __setitem__(self, key, value):
        if value:
            self.__dict__[key] = value

    # def __str__(self):
    #     pass
    #
    # def __repr__(self):
    #     pass

class ObjectRecord(Record):

    def __init__(self, **kwargs):
        Record.__init__(self)

