#!/usr/bin/python
# -*- coding: latin-1 -*-
import json
import datetime
import requests

from GeneralClass import *
import GeneralFunctions

def get559(ut,Rest,name):
    while True:
        try:
            start_time = datetime.datetime.utcnow()
            # ------------------------------------------------------------------------------
            # Consulta UIC559
            # ------------------------------------------------------------------------------
            file559name = "%s_%s_UIC559_%s.xml" % (ut, name, GLOBAL.NOW_STR)
            file559full = "%s/%s" % (SETTINGS.NPATH559, file559name)

            LOG.info("-" * GLOBAL.NCHAR)
            LOG.info("GETTING UIC from %s:%s" % (Rest._ip, Rest._port))
            LOG.info("-" * GLOBAL.NCHAR)
            # The first time we ask for the last 200 events
            if (Rest._uicid != False):
                # Once we have the last id we ask from that id to newer events
                response = Rest.getUicfromid(Rest._uicid)
            else:
                # The first time we ask for the last 200 events
                response = Rest.getUic()

            if Rest._uicid == False or int(Rest._uicid) < int(response.headers['X-Cafpa-UpperEventId']):
                if response.status_code == 200:
                    #Escribimos el fichero a disco
                    with open(file559full, "wb") as f:
                        f.write(response.text)
                        f.close()
                        #Actualizamos la cabecera
                        Rest._uicid = response.headers['X-Cafpa-UpperEventId']
                    #Movemos el fichero a la carpeta de salida
                    if GeneralFunctions.getarchivesize(file559full) > 0:
                        GeneralFunctions.ZipandMovetoUpload(file559name, file559full, SETTINGS.NPATH559,
                                                            SETTINGS.ZPATH559)
            else:
                LOG.info("No new events")

        except requests.exceptions.RequestException as e:
            LOG.warning("ERROR REQUESTS: %s" % str(e))
            pass

        except Exception as e:
            LOG.error("ERROR getting UIC 559 -->%s" % e)
            pass
        # ------------------------------------------------------------------------------
        # Mantener periodicidad
        # ------------------------------------------------------------------------------
        GeneralFunctions.keepperiod(10, start_time)






def getLogEntriesWithoutFormatting(ut,Rest,name):
    while True:

        try:
            start_time = datetime.datetime.utcnow()
            #------------------GETTING CFGAlarms-----------------------
            alarmsFilename = "%s_%s_CFG_ALARMS%s.json" % (ut, name, GLOBAL.NOW_STR)
            alarmsFilenamenamefull = "%s/%s" % (SETTINGS.NPATH559, alarmsFilename)
            # Pido el log entries sin meta ni data para coger el upper id
            logentries = Rest.getLogEntries().text
            logentriesjson = json.loads(logentries)

            #----Getting log entries with meta and snap---------------

            filelogentries = "%s_%s_LogEntries_%s" % (ut, name, GLOBAL.NOW_STR)
            filelogentriesfull = "%s/%s" % (SETTINGS.NPATH559, filelogentries)

            #Es la 1 vez que pido
            if (Rest._entriesid == False ):
                # Pido los ultimos 100 eventos desde el upper evnt id recibido
                LOG.info("FIRST TIME ASKING, 200 EVENTS LOGENTRIES OFFSET")
                #la consulta de abajo para las 100 ultimas! cuidado si es inicio y hay solo 4 o asi!
                #logEntriesresponse = Rest.getLogEntriesfromid(int(logentriesjson['src'][0]['upper_evnt_id'])-100)
                logEntriesresponse = Rest.getLogEntries()
                #Escribiendo a fichero
                if (logEntriesresponse.status_code == 200):
                    logentries = logEntriesresponse.text
                    logentriesjson = json.loads(logentries)

                    # Formateamos el logentries
                    # Escribiendo a fichero
                    with open(filelogentriesfull, 'w') as outfile:
                        json.dump(logentriesjson, outfile)
                        # Actualizamos la cabecera
                        Rest._entriesid = int(logentriesjson['src'][0]['upper_evnt_id'])


                    alarmsCFG = Rest.getAlarmsCfg().text
                    alarmsjson = json.loads(alarmsCFG)
                    with open(alarmsFilenamenamefull, 'w') as outfile:
                        json.dump(alarmsjson, outfile)
                    GeneralFunctions.ZipandMovetoUpload(alarmsFilename, alarmsFilenamenamefull, SETTINGS.NPATH559,
                                                        SETTINGS.ZPATH559)
                    GeneralFunctions.ZipandMovetoUpload(filelogentries, filelogentriesfull, SETTINGS.NPATH559,
                                                        SETTINGS.ZPATH559)

            else:
                #Compruebo que la cabecera ha cambiado para pedir
                if (int(logentriesjson['src'][0]['upper_evnt_id'])!=Rest._entriesid):
                    #Pido desde el upper event id
                    LOG.info("THERE ARE NEW EVENTS, LOGENTRIES OFFSET %s" % Rest._entriesid)
                    logEntriesresponse = Rest.getLogEntriesfromid(Rest._entriesid)
                    Rest._entriesid = int(logentriesjson['src'][0]['upper_evnt_id'])

                    if (logEntriesresponse.status_code == 200):
                        logentries = logEntriesresponse.text
                        logentriesjson = json.loads(logentries)
                        # Actualizamos la cabecera
                        Rest._entriesid = int(logentriesjson['src'][0]['upper_evnt_id'])
                        # Formateamos el logentries
                        # Escribiendo a fichero
                        with open(filelogentriesfull, 'w') as outfile:
                            json.dump(logentriesjson, outfile)
                            # Actualizamos la cabecera
                            Rest._entriesid = int(logentriesjson['src'][0]['upper_evnt_id'])

                        alarmsCFG = Rest.getAlarmsCfg().text
                        alarmsjson = json.loads(alarmsCFG)
                        with open(alarmsFilenamenamefull, 'w') as outfile:
                            json.dump(alarmsjson, outfile)
                        GeneralFunctions.ZipandMovetoUpload(alarmsFilename, alarmsFilenamenamefull, SETTINGS.NPATH559,
                                                            SETTINGS.ZPATH559)

                        GeneralFunctions.ZipandMovetoUpload(filelogentries, filelogentriesfull, SETTINGS.NPATH559,
                                                            SETTINGS.ZPATH559)
                else:
                    LOG.info("NO NEW LOG ENTRIES")

        except requests.exceptions.RequestException as e:
            LOG.warning("ERROR REQUESTS: %s" % str(e))
            pass

        except Exception as e:
            LOG.error("ERROR getting logentries -->%s" % e)
            pass
        GeneralFunctions.keepperiod(10,start_time)


def getCounters(ut,Rest,name):
    while True:
        try:
            # ------------------------------------------------------------------------------
            # Consulta UIC559
            # ------------------------------------------------------------------------------
            LOG.info("#" * GLOBAL.NCHAR)
            LOG.info("GETTING  COUNTERS")
            LOG.info("#" * GLOBAL.NCHAR)

            start_time = datetime.datetime.utcnow()

            COUNTER_VG="COUNTERS"

            try:
                counters = Rest.getVarGroupsValue(COUNTER_VG).text
                fileCountersname = "%s_%s_COUNTERS_%s.json" % (ut, name , GLOBAL.NOW_STR)
                fileCountersnamefull = "%s/%s" % (SETTINGS.NPATH559, fileCountersname)
                if counters.status_code == 200:
                    with open(fileCountersnamefull, "wb") as f:
                        f.write(counters.text)
                        f.close()
                # ------------------------------------------------------------------------------
                # ZIP counters
                # ------------------------------------------------------------------------------
                if counters.status_code == 200 and GeneralFunctions.getarchivesize(fileCountersnamefull) > 0:
                    GeneralFunctions.ZipandMovetoUpload(fileCountersname, fileCountersnamefull, SETTINGS.NPATH559, SETTINGS.ZPATH559)

            except requests.exceptions.RequestException as e:
                LOG.warning("ERROR REQUESTS: %s" % str(e))
                raise
            except Exception:
                LOG.error("ERROR getting counters")
                raise
        except:
            pass
        # ------------------------------------------------------------------------------
        # Mantener periodicidad
        # ------------------------------------------------------------------------------
        GeneralFunctions.keepperiod(10, start_time)



#FUNCION que formatea el log entries metiendo variables a los meta/snap. POR DEPURAR DE FORMA GENERICA!
def getLogEntries(ut,RestHMI):
    while True:

        try:
            start_time = datetime.datetime.utcnow()
            # ------------------------------------------------------------------------------
            # Consulta y formatea el LOG_ENTRIES del HMI
            # ------------------------------------------------------------------------------
            # ---------getting the alarm configuration of the restSrv
            # ---------Building a dictionary for snapshots and metadata of alarms-variables with alarmid as key of the dict solo la 1 vez--------
            try:
                ALARMS_DICT_HMI_SNAPSHOT
                ALARMS_DICT_HMI_METADATA
            except NameError:
                global ALARMS_DICT_HMI_SNAPSHOT
                global ALARMS_DICT_HMI_METADATA
                #Inicializo diccionarios
                ALARMS_DICT_HMI_SNAPSHOT = {}
                ALARMS_DICT_HMI_METADATA = {}
                pass

            if (ALARMS_DICT_HMI_METADATA == {} and ALARMS_DICT_HMI_SNAPSHOT == {}):
                try:
                    alarmsCFG = RestHMI.getAlarmsCfg().text
                except requests.exceptions.RequestException as e:
                    LOG.warning("ERROR REQUESTS: %s" % str(e))
                    raise
                alarmsjson = json.loads(alarmsCFG)
                ALARMS_DICT_HMI_METADATA = RestHMI.buildAlarmDictMeta(alarmsjson)
                ALARMS_DICT_HMI_SNAPSHOT = RestHMI.buildAlarmDictSnap(alarmsjson)

            # --------Getting the log entries without meta and snapshot para upperid------
            try:
                #Variable que almacena el upper event id. Si no existe porque es la 1 vez la inicializo a 100 por debajo
                HMI_upper_evnt_id
                HMI_logentries_first
            except NameError:
                global HMI_upper_evnt_id
                global HMI_logentries_first
                HMI_logentries_first = True
                HMI_upper_evnt_id=0
                pass


            # Pido el log entries sin meta ni data para coger el upper id
            logentries = RestHMI.getLogEntries().text
            logentriesjson = json.loads(logentries)
            #Ponemos a 0 el flag ya que ya hemos pedido una vez

            #----Getting log entries with meta and snap

            #Es la 1 vez que pido
            if (HMI_logentries_first):
                # Pido los ultimos 100 eventos desde el upper evnt id recibido
                LOG.info("FIRST TIME ASKING, 100 EVENTS LOGENTRIES OFFSET %s" % HMI_upper_evnt_id)
                logEntriesresponse = RestHMI.getLogEntriesfromid(int(logentriesjson['src'][0]['upper_evnt_id'])-100)
                HMI_logentries_first = 0
                new_entries = 1
            else:
                #Compruebo que la cabecera ha cambiado para pedir
                if (int(logentriesjson['src'][0]['upper_evnt_id'])!=HMI_upper_evnt_id):
                    #Pido desde el upper event id
                    LOG.info("THERE ARE NEW EVENTS, LOGENTRIES OFFSET %s" % HMI_upper_evnt_id)
                    new_entries = True
                    logEntriesresponse = RestHMI.getLogEntriesfromid(HMI_upper_evnt_id)
                else:
                    LOG.info("NO NEW LOG ENTRIES")
                    new_entries = False
            #Si la respuesta es correcta formateo el log entries
            if (logEntriesresponse.status_code == 200 and new_entries):
                logentries = logEntriesresponse.text
                logentriesjson = json.loads(logentries)
                #Actualizamos la cabecera
                HMI_upper_evnt_id = int(logentriesjson['src'][0]['upper_evnt_id'])

                        #Formateamos el logentries
                logentries_formated = GeneralFunctions.formatLogEntries(logentriesjson, ALARMS_DICT_HMI_METADATA,
                                                       ALARMS_DICT_HMI_SNAPSHOT)
                # Escribiendo a fichero
                filelogentries = "%s_%s_LogEntries_%s" % (ut, 'HMI', GLOBAL.NOW_STR)
                filelogentriesfull = "%s/%s" % (SETTINGS.NPATH559, filelogentries)

                with open(filelogentriesfull, 'w') as outfile:
                    json.dump(logentries_formated, outfile)

                GeneralFunctions.ZipandMovetoUpload(filelogentries, filelogentriesfull, SETTINGS.NPATH559, SETTINGS.ZPATH559)

        except requests.exceptions.RequestException as e:
            LOG.warning("ERROR REQUESTS: %s" % str(e))
            pass
        except:
            pass
        # ------------------------------------------------------------------------------
        # Mantener periodicidad
        # ------------------------------------------------------------------------------
        GeneralFunctions.keepperiod(10, start_time)
