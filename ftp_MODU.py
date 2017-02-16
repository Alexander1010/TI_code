#!/usr/bin/python
# -*- coding: latin-1 -*-

while True:
    try:

        #General modules of the system
        import datetime
        import zipfile
        import json
        import signal
        import time
        import sys
        import logging
        import logging.handlers
        from logger import *
        import threading

        #Created Classes for main function execution
        from GeneralClass import *
        from FilesManager import *
        from Error import *
        from DevManager import *
        from settings import *
        from RestManager import *
        from FtpManager import *
        import DatesManager
        import GeneralFunctions
        import Uploader
        import Downloader
        import GetEvents
        break
    except Exception, ex:
        global PRELOAD  # Parámetros para registro de sistema
        lines = open(PRELOAD.ERR_FILE).readlines()
        lines.append("%s\n" % ex)
        num_lines = lines.count
        if num_lines > PRELOAD.MAX_LINES:
            open(PRELOAD.ERR_FILE, 'w').writelines(lines[1:])
        else:
            open(PRELOAD.ERR_FILE, 'w').writelines(lines)
        time.sleep(1)


# Se instancia para poder ser utilizada en la carga
PRELOAD = PRELOAD()



################################################################################
# MAIN function with initialize 3 different threads
################################################################################
def main():

    GLOBAL.NCHAR = 136
    LOG.info("#" * GLOBAL.NCHAR)
    LOG.info("# STARTING %-123s #" % PROGNAME)
    LOG.info("# VERSION %-124s #" % get_version())
    LOG.info("#" * GLOBAL.NCHAR)
    ut = GeneralFunctions.get_ut()

    while True:

        #Instancio 2 threads diferentes (Downloader, uploader). El uploader primero para que suba lo ultimo que habia


        upload_thread = threading.Thread(name = 'Uploader', target=Uploader.uploader,
                                         args=(ut,SETTINGS.UPLOADER_PERIOD,SETTINGS.UPATH,SETTINGS.RSRV1))
        upload_thread.daemon = True
        upload_thread.start()


        download_thread = threading.Thread(name = 'Downloader', target=Downloader.Downloader,args=(ut,SETTINGS.DOWNLOADER_PERIOD,SETTINGS.LSRV))
        download_thread.daemon = True
        download_thread.start()

        #Instancio threads para descarga de recursos del SDIAG
        RestSDIAG = RestManager(SETTINGS.REST_SDIAG, SETTINGS.REST_SDIAG_PORT)

        # UIC559 thread
        SDIAG_UIC_thread = threading.Thread(name = 'SDIAG_UIC',
                                            target=GetEvents.get559,args=(ut,RestSDIAG,'SDIAG'))
        SDIAG_UIC_thread.daemon = True
        SDIAG_UIC_thread.start()

        # LogEntries and cfgalarms without formatting thread
        SDIAG_LogEntriesWF_thread = threading.Thread(name = 'LogEntriesWF',
                                                     target=GetEvents.getLogEntriesWithoutFormatting,
                                                     args=(ut,RestSDIAG,'SDIAG'))
        SDIAG_LogEntriesWF_thread.daemon = True
        SDIAG_LogEntriesWF_thread.start()

        # GetCounters thread
        SDIAG_Counters_thread = threading.Thread(name='LogEntriesWF',
                                                     target=GetEvents.getCounters,
                                                     args=(ut,RestSDIAG,'SDIAG'))
        SDIAG_Counters_thread.daemon = True
        SDIAG_Counters_thread.start()




        #Instancio threads para descarga de recursos del SDIAG
        RestHMI = RestManager(SETTINGS.RESTSRV_HMI, SETTINGS.RESTSRV_HMI_PORT)
       # UIC559 thread
        HMI_UIC_thread = threading.Thread(name = 'HMI_UIC',
                                            target=GetEvents.get559,args=(ut,RestHMI,'HMI'))
        HMI_UIC_thread.daemon = True
        HMI_UIC_thread.start()

        # LogEntries and cfgAlarms without formatting thread
        HMI_LogEntriesWF_thread = threading.Thread(name = 'HMI_LogEntriesWF',
                                                     target=GetEvents.getLogEntriesWithoutFormatting,
                                                     args=(ut,RestHMI,'HMI'))
        HMI_LogEntriesWF_thread.daemon = True
        HMI_LogEntriesWF_thread.start()

        # GetCounters thread
        HMI_Counters_thread = threading.Thread(name='HMI_LogEntriesWF',
                                                     target=GetEvents.getCounters,
                                                     args=(ut,RestHMI,'HMI'))
        HMI_Counters_thread.daemon = True
        HMI_Counters_thread.start()


        #Implementar watchdog para los diferentes threads y printeo de funcionamiento del script
        while True:
            LOG.info("#" * GLOBAL.NCHAR)
            LOG.info("MAIN THREAD SLEEPING")
            time.sleep(10)



    """
    GLOBAL.NCHAR = 136
    LOG.info("#" * GLOBAL.NCHAR)
    LOG.info("# STARTING %-123s #" % PROGNAME)
    LOG.info("# VERSION %-124s #" % get_version())
    LOG.info("#" * GLOBAL.NCHAR)
    pd = ETHPD()
    dm = DatesManager.DatesManager()
    GeneralFunctions.checkpaths()
    while True:
        start_time = datetime.datetime.utcnow()
        GLOBAL.NEW_FILES = 0
        GLOBAL.NUM_FILES = 0
        GLOBAL.DOW_FILES = 0
        GLOBAL.NOW_STR = start_time.strftime('%Y%m%d%H%M%S')
        GLOBAL.NOW_SEC = dm.date2secs(start_time)
        # ------------------------------------------------------------------------------
        # Getting ut value
        # ------------------------------------------------------------------------------
        ut = GeneralFunctions.get_ut()

        # ------------------------------------------------------------------------------
        #Calling downloader
        # ------------------------------------------------------------------------------
        Downloader.Downloader(ut,SETTINGS.LSRV,SETTINGS.VIESCAS_SRV)
        # ------------------------------------------------------------------------------
        #Getting events and counters of SDIAG
        # ------------------------------------------------------------------------------
        RestSDIAG = RestManager(SETTINGS.REST_SDIAG, SETTINGS.REST_SDIAG_PORT)

        GetSDIAGEvents.get559(RestSDIAG,ut)
        GetSDIAGEvents.getLogEntries(RestSDIAG,ut)
        GetSDIAGEvents.getLogEntriesWithoutFormatting(RestSDIAG,ut)
        GetSDIAGEvents.getCounters(RestSDIAG,ut)

        # ------------------------------------------------------------------------------
        #Getting events and counters of HMI
        # ------------------------------------------------------------------------------
        RestHMI = RestManager(SETTINGS.RESTSRV_HMI, SETTINGS.RESTSRV_HMI_PORT)
        GetHMIEvents.get559(RestHMI,ut)
        GetHMIEvents.getLogEntries(RestHMI,ut)
        GetHMIEvents.getCounters(RestHMI,ut)






        # ------------------------------------------------------------------------------
        # Carga a Tierra
        # ------------------------------------------------------------------------------
        Uploader.uploader(ut,SETTINGS.UPATH,SETTINGS.RSRV1)
        # ------------------------------------------------------------------------------
        # Mantener periodicidad
        # ------------------------------------------------------------------------------
        time_consumed = datetime.datetime.utcnow() - start_time
        time_to_wait = (datetime.timedelta(seconds=SETTINGS.PERIOD) - time_consumed).total_seconds()
        LOG.info("Last cycle duration was: %s secs." % time_consumed.total_seconds())
        LOG.info("Waiting for %s secs." % time_to_wait)
        if time_to_wait > 0:
            time.sleep(time_to_wait)

    """



def exit_gracefully(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    try:
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


signal.signal(signal.SIGINT, exit_gracefully)

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    main()
