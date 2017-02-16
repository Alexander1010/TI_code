#!/usr/bin/python
# -*- coding: latin-1 -*-
import datetime

from GeneralClass import *
import FilesManager
from GeneralFunctions import keepperiod,zipnewfiles,movezipfiles
import DatesManager
def Downloader(ut,EXECPERIOD,FILE_SRVS=None,MLSD_SRVS=None):

    #Definición de objetos globales
    dm = DatesManager.DatesManager()
    #Bucle con llamada a metodos de descarga. Se ejecuta con la periodicidad que se defina en EXECPERIOD
    while True:
        try:
            start_time = datetime.datetime.utcnow()
            GLOBAL.NEW_FILES = 0
            GLOBAL.NUM_FILES = 0
            GLOBAL.DOW_FILES = 0
            GLOBAL.NOW_STR = start_time.strftime('%Y%m%d%H%M%S')
            GLOBAL.NOW_SEC = dm.date2secs(start_time)
            # ------------------------------------------------------------------------------
            # Descarga de últimos ficheros
            # ------------------------------------------------------------------------------
            # Descarga los ficheros de fecha posterior a la fecha más actualizada
            # en la carpeta de descarga
            # files = getallfiles(SETTINGS.LSRV, ut)
            files = FilesManager.FilesManager()

            # ------------------------------------------------------------------------------
            # Se consigue lista de ficheros a descargar de los servidores FTP
            # ------------------------------------------------------------------------------
            #Descarga de ficheros del servidores ftp con MLSD
            if MLSD_SRVS != None:
                files.getallfiles_MLSD(MLSD_SRVS, ut)
            # Descarga de ficheros del servidores ftp con fichero de modificaciones
            if FILE_SRVS != None:
                files.getallfiles(FILE_SRVS, ut)

            LOG.info("TOTAL CHECKED FILES: %s\tTOTAL NEW FILES: %s\tTOTAL DOWNLOADED FILES: %s" %
                     (str(GLOBAL.NUM_FILES), str(GLOBAL.NEW_FILES), str(GLOBAL.DOW_FILES)))
            # ------------------------------------------------------------------------------
            # Compresión de últimos ficheros
            # ------------------------------------------------------------------------------
            # De forma secuencial al punto anterior, una vez descargados los ficheros
            # se comprimen los nuevos y se guardan en la carpeta de comprimidos
            # La nueva lista de ficheros sólo contiene info útil de las rutas zip y upload
            files = zipnewfiles(files)
            # ------------------------------------------------------------------------------
            # Encolado de ficheros nuevos
            # ------------------------------------------------------------------------------
            # Mover los comprimidos a la carpeta de cola para salida
            files = movezipfiles(files)
        except Exception as e:
            LOG.error("ERROR IN DOWNLOADER--> %s" % e)
            pass
        # ------------------------------------------------------------------------------
        # Mantener periodicidad
        # ------------------------------------------------------------------------------
        keepperiod(EXECPERIOD,start_time,)