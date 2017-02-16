#!/usr/bin/python
# -*- coding: latin-1 -*-
from settings import *
import logging
import logging.handlers

################################################################################
# GLOBAL INFO
################################################################################
# Parámetros para utilizar en la carga del script
class PRELOAD():
    def __init__(self):
        pass

    ERR_FILE = "/var/traintic/log/python.log"
    MAX_LINES = 100
    CHARS_LINE = 80




# Variables globales utilizadas para logs
class GLOBAL():
    def __init__(self):
        pass

    NEW_FILES = 0
    NUM_FILES = 0
    DOW_FILES = 0
    UP_FILES = 0
    NOW_STR = ""
    NOW_SEC = 0
    NCHAR = PRELOAD.CHARS_LINE


# Variables globales auxiliares para su uso en control de flujo entre ejecuciones
class AUX():
    def __init__(self):
        pass
    #Indica si se ha pedido al SDIAG por 1 vez
    SDIAG_FIRST = True
    HMI_FIRST = True
    SDIAG_LENTRIES_FIRST = True
    SDIAG_LENTRIES_FIRST = True
    SDIAG_LID=0
    SDIAG_UID=0
    HMI_LID=0
    HMI_UID=0


# Copia propia de parámetros indicados en el fichero settings.py
class SETTINGS():
    def __init__(self):
        pass

    PROG = PROGNAME
    RSRV1 = RSRV1_CFG
    TPATH = TPATH_CFG
    ZPATH = ZPATH_CFG
    UPATH = UPATH_CFG
    UEDPATH = UEDPATH_CFG
    NPATH559 = NPATH559_CFG
    ZPATH559 = ZPATH559_CFG
    #list of servers to download via mod file
    LSRV = LSRV_CFG
    #list of servers to download via mlsd command
    LSRV_MLSD = MLSD_LSRV_CFG

    #PERIODOS DEL DOWNLOADER Y UPLOADER
    DOWNLOADER_PERIOD = DOWNLOADER_EXECPERIOD
    UPLOADER_PERIOD = UPLOADER_EXECPERIOD


    MAX_RETRIES = MAX_FTP_RETRIES
    MAJOR = MAJOR_CFG
    MINOR = MINOR_CFG
    VARS = VARS_CFG
    MAX_SIZE = UPLOADED_SIZE
    REST_SDIAG = RESTSRV_CFG
    REST_SDIAG_PORT = RESTSRV_PORT_CFG
    RESTSRV_HMI= RESTSRV_HMI_CFG
    RESTSRV_HMI_PORT = RESTSRV_HMI_PORT_CFG
    MODIFICATION_FILE_LOCAL = MODIFICATION_FILE_LOCAL_NAME
    MODIFICATION_FILE_SERVER = MODIFICATION_FILE_SERVER_NAME
    MOD_PATH = MODIFICATION_FILE_PATH


# Manejador propio del sistema de log ciclico importado
class LOG():
    def __init__(self):
        pass

    @staticmethod
    def error(_str):
        logging.getLogger(SETTINGS.PROG).error(_str)

    @staticmethod
    def info(_str):
        logging.getLogger(SETTINGS.PROG).info(_str)

    @staticmethod
    def warning(_str):
        logging.getLogger(SETTINGS.PROG).warning(_str)

