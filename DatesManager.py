#!/usr/bin/python
# -*- coding: latin-1 -*-
import datetime
class DatesManager():
    def __init__(self):
        pass

    @staticmethod
    def secs2date(s):
        return datetime.datetime.fromtimestamp(s)

    @staticmethod
    def date2str(d):
        return d.strftime('%Y%m%d%H%M%S')

    @staticmethod
    def date2secs(d):
        date_base = datetime.datetime(1970, 1, 1, 0, 0, 0)
        return (d - date_base).total_seconds()

    def secs2str(self, s):
        return self.date2str(self.secs2date(s))

    def str2secs(self, sd):
        date = datetime.datetime.strptime(sd, '%Y%m%d%H%M%S')
        return self.date2secs(date)