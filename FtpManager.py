#!/usr/bin/python
# -*- coding: latin-1 -*-

import os
import ftplib
import socket
import time
from GeneralClass import SETTINGS,LOG,GLOBAL
from Error import Err
from GeneralFunctions import *
class FtpManager():
    def __init__(self, ip, usr, pas):
        self.ip = ip
        self.usr = usr
        self.pas = pas
        self.error = Err()
        self.connected = False
        self.ftp = None
        self.error.resetall()

    def copy(self, c):
        self.ip = c.ip
        self.usr = c.usr
        self.pas = c.pas
        self.error = c.error
        self.connected = c.connected
        self.ftp = c.ftp

    def connect(self):
        if not self.connected:
            try:
                self.ftp = ftplib.FTP(self.ip, self.usr, self.pas, timeout=5)
                self.connected = True
            except ftplib.all_errors, e:
                self.error.e = e
                self.copy(printerror("FTP", self))
            except socket.error, e:
                self.error.e = e
                self.copy(printerror("SOCKET", self))
            except Exception, e:
                self.error.e = e
                self.copy(printerror("GENERAL", self))

    def disconnect(self):
        if self.connected:
            try:
                self.ftp.close()
                self.connected = False
            except ftplib.all_errors, e:
                self.error.e = e
                self.copy(printerror("FTP.CLOSE", self))

    def getbinary(self, f):
        if self.connected:
            try:
                self.ftp.cwd("/%s" % f['rpath'])
                file_hand = open(f['flname'], "wb")
                self.ftp.retrbinary("RETR " + f['name'], file_hand.write)
                file_hand.close()
                self.error.resetall()
                self.error.exit = 1
            except ftplib.all_errors, e:
                self.error.e = e
                LOG.info("ERROR with file: %s" % f['name'])
                self.copy(printerror("FTP", self))
            except socket.error, e:
                self.error.e = e
                LOG.info("ERROR with file: %s" % f['name'])
                self.copy(printerror("SOCKET", self))
            except Exception, e:
                self.error.e = e
                LOG.info("ERROR with file: %s" % f['name'])
                self.copy(printerror("GENERAL", self))

    # Carga en srv remoto los ficheros incluidos
    def putftp(self, files, rpath):
        files_up = FilesManager.FilesManager()
        for f in files.list:
            LOG.info("uploading file: %s" % (f['ufname']))
            f['rpath'] = rpath
            self.error.resetall()
            while self.error.exit == 0:
                self.connect()
                self.putbinary(f)
                if self.error.exit == 1:
                    LOG.info("File %s uploaded" % (f['ufname']))
                    GLOBAL.UP_FILES += 1
                    files_up.addelement(f)
                    # END WHILE
        # END FOR

        self.disconnect()
        return files_up

    def putbinary(self, f):
        if self.connected:
            try:
                self.ftp.cwd("/%s" % f['rpath'])
                file_hand = open(f['ufname'], "rb")
                self.ftp.storbinary("STOR " + f['zname'], file_hand)
                file_hand.close()
                self.error.resetall()
                self.error.exit = 1
            except ftplib.all_errors, e:
                self.error.e = e
                self.copy(printerror("FTP", self))
            except socket.error, e:
                self.error.e = e
                self.copy(printerror("SOCKET", self))
            except Exception, e:
                self.error.e = e
                self.copy(printerror("GENERAL", self))

    # Se conecta a ftp y retorna ficheros nuevos
    def getnewfileslist(self, dev):
        ip = self.ip
        usr = self.usr
        pas = self.pas
        ret_lis = []
        data = []
        ftphandler = ftplib.FTP()
        self.error.resetall()
        while self.error.exit == 0:
            try:
                data[:] = []
                ret_lis[:] = []
                ftphandler = ftplib.FTP(ip, usr, pas)
                ftphandler.cwd("/%s" % dev.rpath)
                ftphandler.retrlines('MLSD', data.append)
                LOG.info(data)
                ret_lis = buildlistfromdata_MLSD(data, dev)
                self.error.resetall()
                self.error.exit = 1

            except ftplib.all_errors, e:
                self.error.e = e
                self.printerror("FTP")
            except socket.error, e:
                self.error.e = e
                self.printerror("SOCKET")

            except Exception, e:
                self.error.e = e
                self.printerror("GENERAL")

        # Closing ftp connection
        try:
            ftphandler.close()
        except ftplib.all_errors, e:
            self.error.e = e
            self.printerror("FTP.CLOSE")

        return ret_lis

    # Se conecta a ftp y retorna ficheros nuevos
    def getmodificationfile(self, dev):
        ip = self.ip
        usr = self.usr
        pas = self.pas
        ret_lis = []
        data = []
        ftphandler = ftplib.FTP()
        self.error.resetall()
        while self.error.exit == 0:
            try:
                # Se descarga el fichero del servidor y se le anade el nombre del device en local.
                dev_mod_file = "%s/%s" % (SETTINGS.MOD_PATH, SETTINGS.MODIFICATION_FILE_LOCAL + "_" + dev.name)
                # LOG.info("Getting MODIFICATION FILE from %s" % dev.name)
                data[:] = []
                ret_lis[:] = []
                ftphandler = ftplib.FTP(ip, usr, pas)
                ftphandler.cwd("/%s" % dev.rpath)
                file_hand = open(dev_mod_file, "wb")
                ftphandler.retrbinary("RETR " + SETTINGS.MODIFICATION_FILE_SERVER, file_hand.write)
                file_hand.close()
                # Una vez descargado el fichero se extrae la lista ficheros y modificaciones
                data = extractdatafromfile(dev_mod_file)
                ret_lis = buildlistfromdata(data, dev)
                self.error.resetall()
                self.error.exit = 1

            except ftplib.all_errors, e:
                self.error.e = e
                self.printerror("FTP")
            except socket.error, e:
                self.error.e = e
                self.printerror("SOCKET")

            except Exception, e:
                self.error.e = e
                self.printerror("GENERAL")

        # Closing ftp connection
        try:
            ftphandler.close()
        except ftplib.all_errors, e:
            self.error.e = e
            self.printerror("FTP.CLOSE")

        return ret_lis

    # Para trazas de error en FTP
    def printerror(self, ref):
        s = 0
        n = 0
        if ref == "FTP":
            n = self.error.nerr_ftp
            s = 1
        elif ref == "SOCKET":
            n = self.error.nerr_soc
            s = 2
        elif ref == "GENERAL":
            n = 1000
            s = 0
        elif ref == "FTP.CLOSE":
            n = 1000
            s = 0

        self.error.exit = 0
        if (n > SETTINGS.MAX_RETRIES) and (str(self.error.e) != self.error.msg):
            self.error.msg = str(self.error.e)
            LOG.error("%s ERROR: %s" % (ref, str(self.error.e)))
            self.error.exit = -1
        if n >= 1000:
            self.error.msg = ""
            self.error.exit = -1

        if ref == "FTP":
            self.error.nerr_ftp += 1
            self.error.exit = -1
        elif ref == "SOCKET":
            self.error.nerr_soc += 1
            self.error.exit = -1
        elif ref == "GENERAL":
            self.error.nerr_gen = 1000
            self.error.exit = -1
        elif ref == "FTP.CLOSE":
            self.error.nerr_cls = 1000
            self.error.exit = -1
        else:
            LOG.info("FTP error no managed")
            self.error.nerr_cls = 1000
            self.error.exit = -1

        LOG.error("%s ERROR: %s" % (ref, str(self.error.e)))
        time.sleep(s)
