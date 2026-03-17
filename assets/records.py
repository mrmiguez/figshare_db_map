import re

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

    def _clean_text(self, text):
        mark_up_re = re.compile('<.*?>')
        new_line_re = re.compile('\n')
        date_time_code_re = re.compile('T\\d{2}:\\d{2}:\\d{2}Z')

        # remove extraneous leading and trailing characters
        clean_text = text.strip(':').strip(' ')

        # remove markup
        clean_text = re.sub(mark_up_re, '', clean_text)

        # remove newlines
        clean_text = re.sub(new_line_re, ' ', clean_text)

        # remove timecode data trailing a date
        clean_text = re.sub(date_time_code_re, '', clean_text)
        return clean_text

class ObjectRecord(Record):

    def __init__(self, record):
        Record.__init__(self)
        self.record = record

    @property
    def iid(self):
        return self.record.iid

class AuthorRecord(Record):

    def __init__(self, record):
        Record.__init__(self)
        self.record = record

