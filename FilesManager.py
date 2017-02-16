#!/usr/bin/python
# -*- coding: latin-1 -*-


import DevManager
import FtpManager
from GeneralClass import LOG,GLOBAL,SETTINGS
from GeneralFunctions import *
import os
class FilesManager():
    def __init__(self):
        self.list = []
        self.count = 0

    def addfilesnouploaded(self, name, remote, local):

        rpath = remote.split(';')[3]
        srv = remote.split(';')[0]
        ut = local[0]
        lpath = local[1]
        ufname = "%s/%s" % (lpath, name)
        zfname = ufname
        frname = "%s/%s" % (rpath, name)
        ref = "%s:::%s:::%s/%s" % (ut, '', srv, frname)
        self.list.append({'ref': ref, 'ut': ut, 'devname': '', 'srv': srv, 'name': name, 'size': 0, 'mod': 0,
                          'rpath': rpath, 'frname': frname, 'lpath': lpath, 'flname': '', 'zname': name,
                          'zfname': zfname, 'ufname': ufname})
        self.count = len(self.list)

    def addfile_old(self, name, size, mod, rpath, lpath, ut, devname, srv):
        flname = "%s/%s" % (lpath, name)
        frname = "%s/%s" % (rpath, name)
        ref = "%s:::%s:::%s/%s" % (ut, devname, srv, frname)
        self.list.append({'ref': ref, 'ut': ut, 'devname': devname, 'srv': srv, 'name': name, 'size': size, 'mod': mod,
                          'rpath': rpath, 'frname': frname, 'lpath': lpath, 'flname': flname, 'zname': '',
                          'zfname': '', 'ufname': ''})
        self.count = len(self.list)

    def addfile(self, name, mod, rpath, lpath, ut, devname, srv):
        flname = "%s/%s" % (lpath, name)
        frname = "%s/%s" % (rpath, name)
        ref = "%s:::%s:::%s/%s" % (ut, devname, srv, frname)
        self.list.append({'ref': ref, 'ut': ut, 'devname': devname, 'srv': srv, 'name': name, 'mod': mod,
                          'rpath': rpath, 'frname': frname, 'lpath': lpath, 'flname': flname, 'zname': '',
                          'zfname': '', 'ufname': ''})
        self.count = len(self.list)

    def addfile_MLSD(self, name, size, mod, rpath, lpath, ut, devname, srv):
        flname = "%s/%s" % (lpath, name)
        frname = "%s/%s" % (rpath, name)
        ref = "%s:::%s:::%s/%s" % (ut, devname, srv, frname)
        self.list.append({'ref': ref, 'ut': ut, 'devname': devname, 'srv': srv, 'name': name, 'size': size, 'mod': mod,
                          'rpath': rpath, 'frname': frname, 'lpath': lpath, 'flname': flname, 'zname': '',
                          'zfname': '', 'ufname': ''})
        self.count = len(self.list)

    def add559file(self, name, remote, local):
        rpath = remote.split(';')[3]
        srv = remote.split(';')[0]
        ut = local[0]
        lpath = local[1]
        ufname = "%s/%s" % (lpath, name)
        zfname = ufname
        frname = "%s/%s" % (rpath, name)
        ref = "%s:::%s:::%s/%s" % (ut, '', srv, frname)
        self.list.append({'ref': ref, 'ut': ut, 'devname': '', 'srv': srv, 'name': name, 'size': 0, 'mod': 0,
                          'rpath': rpath, 'frname': frname, 'lpath': lpath, 'flname': '', 'zname': name,
                          'zfname': zfname, 'ufname': ufname})
        self.count = len(self.list)

    def addelement(self, elem):
        self.list.append(elem)
        self.count = len(self.list)

    def deletefile(self, n):
        if n < self.count:
            del self.list[n]
            self.count = len(self.list)

    def addfilesfromlist_MLSD(self, lst, dev):
        for elm in sorted(lst, reverse=True):
            name = elm[1].split(';')[0].strip()
            size = elm[1].split(';')[1].strip()
            mod = elm[1].split(';')[2].strip()
            rpath = dev.rpath
            lpath = dev.lpath
            ut = dev.ut
            srv = dev.ip
            devname = dev.name
            self.addfile_MLSD(name, size, mod, rpath, lpath, ut, devname, srv)

    def addfilesfromlist(self, lst, dev):
        for elm in sorted(lst):
            name = elm[1].split(';')[0].strip()
            mod = elm[1].split(';')[1].strip()
            rpath = dev.rpath
            lpath = dev.lpath
            ut = dev.ut
            srv = dev.ip
            devname = dev.name
            self.addfile(name, mod, rpath, lpath, ut, devname, srv)

    def addfilestoupload(self, lst, rpath, lpath, ut, srv):
        for elm in sorted(lst, reverse=True):
            name = elm[1].split(';')[0].strip()
            size = elm[1].split(';')[1].strip()
            mod = elm[1].split(';')[2].strip()
            self.addfile(name, size, mod, rpath, lpath, ut, '', srv)

    # Se conecta a todos los equipos embarcados y construye lista de ficheros nuevos
    def getallfiles_MLSD(self, lsrv, ut):
        LOG.info("-" * GLOBAL.NCHAR)
        # files_all = FilesManager()
        for lsrv in lsrv:
            arr = lsrv.split(';')
            dev = DevManager.DevManager(arr[3].strip(), arr[4].strip(), arr[0].strip(), ut, setMLSD=True)
            ftp = FtpManager.FtpManager(arr[0].strip(), arr[1].strip(), arr[2].strip())
            # ftp.error.resetall()

            files = FilesManager()
            lst = ftp.getnewfileslist(dev)

            if ftp.error.exit != 0:
                files.addfilesfromlist_MLSD(lst, dev)
                if files.count > 0:
                    ftp = getftp_MLSD(ftp, files)
                    self.extendlist(files.list)
                ftp.error.resetall()
            else:
                LOG.error("ERROR getting the list of files ::: Device=%s" % dev.name)
        LOG.info("-" * GLOBAL.NCHAR)

    def getallfiles(self, lsrv, ut):
        LOG.info("-" * GLOBAL.NCHAR)
        # files_all = FilesManager()
        for lsrv in lsrv:
            arr = lsrv.split(';')
            dev = DevManager.DevManager(arr[3].strip(), arr[4].strip(), arr[0].strip(), ut)
            ftp = FtpManager.FtpManager(arr[0].strip(), arr[1].strip(), arr[2].strip())
            # ftp.error.resetall()

            files = FilesManager()
            # (ftp, lst) = getnewfileslist(ftp, dev)
            lst = ftp.getmodificationfile(dev)
            if ftp.error.exit != 0:
                files.addfilesfromlist(lst, dev)
                if files.count > 0:
                    ftp = getftp(ftp, files)
                    self.extendlist(files.list)
                ftp.error.resetall()
            else:
                LOG.error("ERROR getting the list of files ::: Device=%s" % dev.name)
        LOG.info("-" * GLOBAL.NCHAR)

    def extendlist(self, lst):
        self.list.extend(lst)
        self.count = len(self.list)

    def modzipupname(self, fref, zfname):
        for idx, f in enumerate(self.list):
            if fref in f['ref']:
                self.list[idx]['zfname'] = zfname
                self.list[idx]['ufname'] = zfname.replace(SETTINGS.ZPATH, SETTINGS.UPATH)
                break

    # Recoge cfg servidor remoto e inicia carga ficheros
    def putallfiles(self, rsrv):
        LOG.info("-" * GLOBAL.NCHAR)
        srv = rsrv.split(';')
        rpath = srv[3].strip()
        ftp = FtpManager.FtpManager(srv[0].strip(), srv[1].strip(), srv[2].strip())
        # ftp.error.resetall()
        if self.count > 0:
            # ftp, lst = putftp(ftp, self, rpath)
            self.list = ftp.putftp(self, rpath).list
            self.count = len(self.list)
            if ftp.error.exit != 1:
                LOG.error("ERROR uploading files")
        else:
            LOG.info("There are no files to upload")
            LOG.info("-" * GLOBAL.NCHAR)

    def backupuploadedfiles(self):
        if self.count > 0:
            new_list = []
            for tup in self.list:
                try:
                    os.system("mv %s %s" % (tup['ufname'], tup['ufname'].replace(SETTINGS.UPATH, SETTINGS.UEDPATH)))
                    size = 0
                    while True:
                        size = getarchivesize(SETTINGS.UEDPATH)
                        if size > SETTINGS.MAX_SIZE:
                            oldest = str(oldestfile(SETTINGS.UEDPATH)[0])
                            os.remove("%s" % oldest)
                            LOG.info("%s deleted" % oldest)
                        else:
                            break
                    LOG.info("%s size = %s" % (SETTINGS.UEDPATH, size))
                    LOG.info("-" * GLOBAL.NCHAR)

                except OSError, e:
                    LOG.error("%s" % str(e))
                    new_list.append(tup)

            self.list = list(new_list)
            self.count = len(self.list)
