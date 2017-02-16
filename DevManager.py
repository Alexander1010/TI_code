#!/usr/bin/python
# -*- coding: latin-1 -*-
import os
import sys
import glob
from GeneralClass import LOG,SETTINGS,GLOBAL
class DevManager():
    def __init__(self, rpath, dev, srv, ut, setMLSD = 0):
        # ------------------
        self.name = dev
        self.ip = srv
        self.ut = ut
        self.rpath = rpath
        # ------------------
        self.lpath = self.getlocalpath()
        #list es una propiedad que almacena la lista de ficheros extraidos del fichero de modificacion
        # ------------------
        #Parametro opcional para indicar descarga por MLSD, por defecto busca fichero
        if setMLSD:
            self.last = self.getlocallastdatesecs()
        else:
            #Parametro que se define para almacenar la lista. Solo se inicializa cuando no es MLSD
            self.list = self.getlistfromfile()

    def getlocalpath(self):
        path = SETTINGS.TPATH
        try:
            os.makedirs(path)
        except OSError:
            pass

        try:
            path = "%s/%s" % (path, self.name)
            os.makedirs(path)
        except OSError:
            pass

        return path

    def getlocallastdatesecs(self):
        #Funcion que lista los ficheros que hay en el path del device y los ordena.
        #Pilla el tiempo del más nuevo
        files = filter(os.path.isfile, glob.glob("%s/*" % self.lpath))
        if len(files) > 0:
            files.sort(key=lambda x: os.path.getmtime(x))
            last = os.path.getmtime(files[len(files) - 1])
        else:
            last = 0
        return last

    def getlistfromfile(self):
        try:

            dev_mod_file = "%s/%s" % (SETTINGS.MOD_PATH, SETTINGS.MODIFICATION_FILE_LOCAL + "_" + self.name)
            dev_data = []
            infile = open("%s/%s" % (SETTINGS.MOD_PATH, SETTINGS.MODIFICATION_FILE_LOCAL + "_" + self.name), 'r')
            for line in infile:
                dev_data.append(line)
            # Cerramos el fichero.
            infile.close()
        except IOError as (errno, strerror):
            LOG.error("I/O error with modification file %s --> %s %s " % (dev_mod_file,errno,strerror))
            pass
        except:
            LOG.error("ERROR getting data from local MODIFICATION file: %s" % dev_mod_file)
            LOG.error("The content of data is: %s" % dev_data)
            error = sys.exc_info()[0]
            LOG.error ("The error is %s" % error)
            dev_data = []
            pass
        return dev_data

