#!/usr/bin/python
# -*- coding: latin-1 -*-
import os
import datetime

import FilesManager
from GeneralClass import *
import DatesManager
from GeneralFunctions import keepperiod

def uploader(ut,EXECPERIOD,UPLOAD_PATH,REMOTE_PATH):
    # ------------------------------------------------------------------------------
    # Carga a Tierra con periodicidad EXECPERIOD. Origen path UPLOAD_PATH-->REMOTE_PATH
    # ------------------------------------------------------------------------------
    while True:
        try:
            start_time = datetime.datetime.utcnow()
            # ------------------------------------------------------------------------------
            # 	    #AÃ±adiendo ficheros  del directorio de cola de carga
            #  ------------------------------------------------------------------------------
            filesupload = FilesManager.FilesManager()
            if os.path.isdir(UPLOAD_PATH):
                for f in os.listdir(UPLOAD_PATH):
                    filesupload.addfilesnouploaded(f, REMOTE_PATH, (ut, UPLOAD_PATH))

            # Se suben los ficheros que están en la carpeta de carga
            filesupload.putallfiles(REMOTE_PATH)

            # ------------------------------------------------------------------------------
            # Borrar los ficheros cargados a tierra y se mueven a la carpeta uploaded donde se mira la cuota
            # ------------------------------------------------------------------------------
            filesupload.backupuploadedfiles()
            LOG.info("TOTAL UPLOADED FILES: %s" % str(GLOBAL.UP_FILES))
            LOG.info("-" * GLOBAL.NCHAR)
        except Exception as e:
            LOG.error("ERROR IN UPLOADER--> %s" % e)
            pass

            # ------------------------------------------------------------------------------
            # Mantener periodicidad
            # ------------------------------------------------------------------------------
        keepperiod(EXECPERIOD, start_time)