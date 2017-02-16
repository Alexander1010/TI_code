#!/usr/bin/python
# -*- coding: latin-1 -*-
from GeneralClass import LOG
import requests
import json
class RestManager():
    def __init__(self, ip, port):
        # ------------------Initializing RestManager object-------------
        self._ip = ip
        self._port = port
        self._url = self._buildurl()
        self._headers = self._buildHeaders()
        self._session = self._buildSession()
        self._timeout = 30

        #Atributos modificables para el control a la hora de pedir
        self._uicid = 0
        self._entriesid = 0
        # ------------------Metodos "privados" de inicialización de variables-----------------

    def _buildurl(self):
        url = "{0}://{1}:{2}".format("http", self._ip, self._port)
        return url

    def _buildSession(self):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount("{0}://".format("http"), adapter)
        return session

    def _buildHeaders(self):
        headers = {'Accept-Encoding': 'gzip',
                   'Accept-Language': 'es_ES',
                   'User-Agent': 'Mozilla/5.0'}
        return headers

    def _getrequest(self, url):
        LOG.info("GET REQUEST %s" % url)
        response = requests.get(url, timeout=self._timeout, headers=self._headers)
        return response

    def _postrequest(self, url, data):
        LOG.info("POST REQUEST %s , json-> %s" % (url,data))
        response = requests.post(url, data=json.dumps(data), headers=self._headers)
        return response


    # ------------------Metodos "publicos" para acesso a funcionalidades de Rest-----------------
    def getAlarmsCfg(self):
        url_alarmsCfg = self._url + "/cfg/alarms"
        response = self._getrequest(url_alarmsCfg)
        return response

    def getLogEntries(self):
        logentries = self._url + "/logentries?sort=desc"
        response = self._getrequest(logentries)
        return response

    def getLogEntriesMetaSnap(self):
        logentries = self._url + "/logentries?fields=meta,snapshot"
        response = self._getrequest(logentries)
        return response

    def getLogEntriesfromid(self,evntid):
        logentriesfromid = self._url + "/logentries?fields=meta,snapshot&direction=newer&offset="+str(evntid)
        response = self._getrequest(logentriesfromid)
        return response

    def getAlarms(self):
        alarms = self._url + "/alarms"
        response = self._getrequest(alarms)
        return response

    def getAlarmJournal(self):
        alarmjournal = self._url + "/alarmjournal"
        response = self._getrequest(alarmjournal)
        return response

    def getVars(self):
        vars = self.url + "/vars"
        response = self._getrequest(vars)
        return response

    def getVarValue(self, var):
        varvalue = self._url + "/vars/" + var
        response = self._getrequest(varvalue)
        return response

    def getVarGroupsValue(self,vargroupvalue):
        vargroupvalue = self._url + "/vargroups/" + vargroupvalue
        response = self._getrequest(vargroupvalue)
        return response

    def getVarGroups(self):
        vargroups = self._url + "/vargroups"
        response = self._getrequest(vargroups)
        return response

    def getUic(self):
        #uic = self._url + "/reports/1?sort=desc"
        uic = self._url +"/reports/1?direction=newer"
        response = self._getrequest(uic)
        return response

    def getUicfromid(self, uid):
        uicid = self._url + "/reports/1?direction=newer&offset="+str(uid)
        response = self._getrequest(uicid)
        return response


    def createMonitor(self,monitor_json):
        monitor_config = {"vargroupname": "COUNTERS", "cadence": 1024, "numshots": 400}
        monitor_url = self._url + "/monitors"
        response = self._postrequest(monitor_url,monitor_config)
        LOG.info("calling buildmonitor")
        return response




    def getMonitor(self, monitorId):
        monitor = self._url + "/monitors/" + monitorId
        response = self._getrequest(monitor)
        return response

    def getVersions(self):
        versions = self._url + "/versions"
        response = self._getrequest(versions)
        return response

    def formatLogEntries(self):
        print("Get log entries and format")

    def buildAlarmDictSnap(self,cfgalarmsjson):
        alarm_dict = {}
        for i in cfgalarmsjson['src'][0]['alarms']:
            alarmid = i['alarmid']
            snapshot = i['snapshot']
            if str(snapshot) != '[]' and str(snapshot) != '""':
                alarm_dict[alarmid] = snapshot
        return alarm_dict

    def buildAlarmDictMeta(self,cfgalarmsjson):
        alarm_dict = {}
        for i in cfgalarmsjson['src'][0]['alarms']:
            alarmid = i['alarmid']
            meta = i['metadata']
            if str(meta) != '[]' and str(meta) != '""':
                alarm_dict[alarmid] = meta
        return alarm_dict
