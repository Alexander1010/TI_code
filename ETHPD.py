#!/usr/bin/python
# -*- coding: latin-1 -*-
from GeneralClass import SETTINGS,LOG
from vardbvar import VarDBVar, VarDBReadVar
# ETHPD VARS
class ETHPD():
    def __init__(self):
        self.lst = SETTINGS.VARS
        self.var = {}

        for n in self.lst:
            self.var[n] = VarDBReadVar(n)
            self.var[n].load()

    def readvars(self):
        for n in self.lst:
            self.var[n].load()

    def value(self, varname):
        # return ERROR, VALUE, QUALITY
        if varname in self.lst:
            return False, self.var[varname].value(), self.var[varname].good()
        else:
            LOG.error("%s doesn't exist in vardb" % varname)
            return True, 0, 0