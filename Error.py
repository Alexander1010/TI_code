#!/usr/bin/python
# -*- coding: latin-1 -*-
class Err():
    def __init__(self):
        self.nerr_ftp = 0
        self.nerr_soc = 0
        self.nerr_gen = 0
        self.nerr_cls = 0
        self.msg = ""
        self.e = None
        self.exit = 0

    def resetall(self):
        self.nerr_ftp = 0
        self.nerr_soc = 0
        self.nerr_gen = 0
        self.nerr_cls = 0
        self.msg = ""
        self.e = None
        self.exit = 0
