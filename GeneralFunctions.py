#!/usr/bin/python
# -*- coding: latin-1 -*-
import os
import zipfile
import time
import heapq
import requests
import datetime

from GeneralClass import SETTINGS,GLOBAL,LOG
import ftplib
import FtpManager
import FilesManager
import DatesManager
import DevManager


from ETHPD import *
################################################################################
# FUNCTIONS
################################################################################
# Devuelve versión indicada en settings.py
def get_version():
    return "{:02d}.{:02d}".format(SETTINGS.MAJOR, SETTINGS.MINOR)

def get_ut():
    pd = ETHPD()
    # ------------------------------------------------------------------------------
    # Get ETHPD values
    # ------------------------------------------------------------------------------
    pd.readvars()
    err, v, q = pd.value('ETH_PLC_UNS8PERS1')
    if (not err) and q:
        ut = "UT%s" % str(int(v))
    else:
        ut = "UTx"

    return ut

# Comprueba que existen los paths y si no los crea
def checkpaths():
    paths = (SETTINGS.TPATH, SETTINGS.ZPATH, SETTINGS.UPATH, SETTINGS.NPATH559, SETTINGS.ZPATH559, SETTINGS.UEDPATH,
             SETTINGS.MOD_PATH)
    for p in paths:
        folder = p.split('/')
        temp = '/'
        for f in folder:
            try:
                temp += str(f)
                os.makedirs(temp)
            except OSError:
                pass
            temp += '/'


# Utilizada para crear una lista python de los ficheros nuevos incluidos en data
def buildlistfromdata_MLSD(data, dev):
    dm = DatesManager.DatesManager()

    datelist = []
    filelist = []
    last = dev.getlocallastdatesecs()
    for line in data:
        col = line.split(';')

        mod_str = col[1].replace("modify=", "").strip()
        mod_sec = dm.str2secs(mod_str)
        ld_str = dm.secs2str(dev.last)

        filename = col[3].strip()
        if mod_sec > dev.last:
            filename = col[3].strip()
            filesize = col[2].replace("size=", "").strip()
            filelist.append("%s;%s;%s" % (filename, filesize, mod_str))
            datelist.append(mod_str)

        ################################################################################
        # Debug info
        GLOBAL.NUM_FILES += 1
        if mod_sec > dev.last:
            GLOBAL.NEW_FILES += 1
        LOG.info("DEVICE=%-6s : NAME=%-22s : MOD=%-14s - REF=%-14s : NOW=%-14s ::: OLD=%-5s ::: AGE=%d" %
                 (dev.name, filename, mod_str, ld_str, GLOBAL.NOW_STR, (mod_sec <= dev.last),
                  int(GLOBAL.NOW_SEC - mod_sec)))
        ################################################################################

    return zip(datelist, filelist)


def buildlistfromdata(data, dev):
   #LOG.info("COMPARING MODIFIED FILES")
    dm = DatesManager.DatesManager()
    datelist = []
    filelist = []
    i = 0
    # Emparejamos la lista y si  no coinciden las longitudes rellenamos con default
    nfiles_data = len(data)
    nfiles_dev = len(dev.list)


    # En caso de que haya mayor numero de  ficheros en el servidor que en el fichero local
    # significaria que se ha anadido alguno por lo que pongo un default
    while nfiles_data > nfiles_dev:
        LOG.info("New file in the server")
        dev.list.append('default;0000000000000')
        nfiles_dev = len(dev.list)

    # En caso de que haya mas ficheros en local que en el servidor (algun cambio de tcu o tcu nueva)
    # solo se compararan los que tenga el servidor ya que parte de la lista data sera null y el zip truncara
    for line_data, line_dev in zip(data, dev.list):
        if line_dev == None:
            line_dev.list.append('default;0000000000000')  # Se añade a dev un default file hasta completar la lista
        col_data = line_data.split(';')
        col_dev = line_dev.split(';')
        # Guardamos la segunda columna para quedarnos con la fecha de modificacion de lo descargado
        mod_str_col = col_data[1].strip()
        # Guardamos la segunda columna de lo que teníamos en la lista de dev
        mod_str_dev = col_dev[1].strip()
        # Se guarda el nombre del fichero descargado
        filename = col_data[0].strip()
        # Si las fechas de modificacion de ambas listas no coincidense anade el fichero a la lista
        if mod_str_col != mod_str_dev:
            filelist.append("%s;%s" % (filename, mod_str_col))  # Se anade el nombre del fichero
            datelist.append(mod_str_col)  # Se anade la fecha de mod

        ################################################################################
        # Debug info
        GLOBAL.NUM_FILES += 1
        if mod_str_col != mod_str_dev:
            GLOBAL.NEW_FILES += 1

        #LOG.info("DEVICE=%-6s : NAME=%-22s : MOD=%-14s - PREV=%-14s : NOW=%-14s ::: CHANGE=%-5s " %
        #         (dev.name, filename, mod_str_col, mod_str_dev, GLOBAL.NOW_STR, (mod_str_col != mod_str_dev),
        #          ))
        #################################################################################
        i += 1

    return zip(datelist, filelist)


# Utilizada para crear una lista python a raiz de la comparacion de los ficheros
def extractdatafromfile(file):
    # Definimos la lista data donde almacenamos lo leido del fichero
    data = []
    # Abrimos el fichero y lo leemos linea a linea guardando su contenido en la lista data
    infile = open(file, 'r')
    for line in infile:
        data.append(line)
    # Cerramos el fichero.
    infile.close()
    return data


# Para trazas de error en FTP
def printerror(ref, ftp):
    s = 0
    n = 0
    if ref == "FTP":
        n = ftp.error.nerr_ftp
        s = 1
    elif ref == "SOCKET":
        n = ftp.error.nerr_soc
        s = 2
    elif ref == "GENERAL":
        n = 1000
        s = 0
    elif ref == "FTP.CLOSE":
        n = 1000
        s = 0

    ftp.error.exit = 0
    if (n > SETTINGS.MAX_RETRIES) and (str(ftp.error.e) != ftp.error.msg):
        ftp.error.msg = str(ftp.error.e)
        LOG.error("%s ERROR: %s" % (ref, str(ftp.error.e)))
        ftp.error.exit = -1
    if n >= 1000:
        ftp.error.msg = ""
        ftp.error.exit = -1

    if ref == "FTP":
        ftp.error.nerr_ftp += 1
        ftp.error.exit = -1
    elif ref == "SOCKET":
        ftp.error.nerr_soc += 1
        ftp.error.exit = -1
    elif ref == "GENERAL":
        ftp.error.nerr_gen = 1000
        ftp.error.exit = -1
    elif ref == "FTP.CLOSE":
        ftp.error.nerr_cls = 1000
        ftp.error.exit = -1

    LOG.error("%s ERROR: %s" % (ref, str(ftp.error.e)))
    time.sleep(s)
    return ftp


# Se conecta a ftp y retorna ficheros nuevos
def getnewfileslist(ftp, dev):
    ip = ftp.ip
    usr = ftp.usr
    pas = ftp.pas
    ret_lis = []
    data = []
    ftphandler = ftplib.FTP()
    ftp.error.resetall()
    while ftp.error.exit == 0:
        try:
            data[:] = []
            ret_lis[:] = []
            ftphandler = ftplib.FTP(ip, usr, pas)
            ftphandler.cwd("/%s" % dev.rpath)
            ftphandler.retrlines('MLSD', data.append)

            ret_lis = buildlistfromdata(data, dev)
            ftp.error.resetall()
            ftp.error.exit = 1

        except ftplib.all_errors, e:
            ftp.error.e = e
            ftp = printerror("FTP", ftp)
        except socket.error, e:
            ftp.error.e = e
            ftp = printerror("SOCKET", ftp)
        except Exception, e:
            ftp.error.e = e
            ftp = printerror("GENERAL", ftp)

    # Closing ftp connection
    try:
        ftphandler.close()
    except ftplib.all_errors, e:
        ftp.error.e = e
        ftp = printerror("FTP.CLOSE", ftp)

    return ftp, ret_lis


# Descarga de FTP los ficheros incluidos
def getftp_MLSD(ftp, files):
    dm = DatesManager.DatesManager()
    for f in files.list:
        ftp.error.resetall()
        while ftp.error.exit == 0:
            ftp.connect()
            ftp.getbinary(f)
            if ftp.error.exit == 1:
                LOG.info("File %s downloaded" % (f['name']))
                GLOBAL.DOW_FILES += 1
                seconds = dm.str2secs(str(f['mod']))
                os.utime(f['flname'], (seconds, seconds))
                LOG.info("Date of %s changed" % (f['name']))
                # END WHILE
    # END FOR

    ftp.disconnect()
    return ftp


# Descarga de FTP los ficheros incluidos
def getftp(ftp, files):
    dm = DatesManager.DatesManager()
    for f in files.list:
        ftp.error.resetall()
        while ftp.error.exit == 0:
            ftp.connect()
            ftp.getbinary(f)
            if ftp.error.exit == 1:
                LOG.info("File %s downloaded" % (f['name']))
                GLOBAL.DOW_FILES += 1
                LOG.info("Date of %s changed" % (f['name']))
                # END WHILE
    # END FOR

    ftp.disconnect()
    return ftp


# Se conecta a todos los equipos embarcados y construye lista de ficheros nuevos
def getallfiles(lsrv, ut):
    LOG.info("-" * GLOBAL.NCHAR)
    files_all = FilesManager()
    for lsrv in lsrv:
        arr = lsrv.split(';')
        dev = DevManager.DevManager(arr[3].strip(), arr[4].strip(), arr[0].strip(), ut)
        ftp = FtpManager.FtpManager(arr[0].strip(), arr[1].strip(), arr[2].strip())
        ftp.error.resetall()
        files = FilesManager.FilesManager()
        (ftp, lst) = getnewfileslist(ftp, dev)

        if ftp.error.exit != 0:
            files.addfilesfromlist(lst, dev)
            if files.count > 0:
                ftp = getftp(ftp, files)
                files_all.extendlist(files.list)
            ftp.error.resetall()
        else:
            LOG.error("ERROR getting the list of files ::: Device=%s" % dev.name)
    LOG.info("-" * GLOBAL.NCHAR)
    return files_all


# Comprime ficheros nuevos
def zipnewfiles(files):
    files_new = FilesManager.FilesManager()
    if files.count > 0:
        lastdev = 'XXX'
        for f in files.list:
            zip_name = "%s_%s_%s.zip" % (f['ut'], f['devname'], GLOBAL.NOW_STR)
            zip_fname = "%s/%s" % (SETTINGS.ZPATH, zip_name)
            zf = zipfile.ZipFile(zip_fname, 'a')
            zf.write(f['flname'], f['name'],compress_type=zipfile.ZIP_DEFLATED)
            zf.close()
            files.modzipupname(f['ref'], zip_fname)
            if lastdev not in f['devname']:
                f['zname'] = zip_name
                files_new.addelement(f)
            lastdev = f['devname']

    return files_new


# Mueve ficheros comprimidos a directorio de cola de carga
def movezipfiles(files):
    files_new = FilesManager.FilesManager()
    if files.count > 0:
        for f in files.list:
            LOG.info("ZIP=%s, UP=%s" % (f['zfname'], f['ufname']))
            f['srv'] = SETTINGS.RSRV1.split(';')[0]
            # LOG.info("%s, %s" % (f['zfname'],f['ufname']))
            os.system("mv %s %s" % (f['zfname'], f['ufname']))
            files_new.addelement(f)

    return files_new




# Consulta a restServer para obtener fichero UIC559 con regs nuevos
def getuic559(Rest, file559, first, DEVICE_LID, DEVICE_UID):
    LOG.info("-" * GLOBAL.NCHAR)
    LOG.info("GETTING UIC from %s:%s" % (Rest._ip,Rest._port))
    LOG.info("-" * GLOBAL.NCHAR)
    # Se importan configuraciones del rest segun el device que se pida
    try:
        write = 0  # Variable (1,0) que indica si hay que escribir el uic para no volver a escribir lo mismo
        if (first):
            # The first time we ask for the last 200 events
            response = Rest.getUic()

        else:
            # Once we have the last id we ask from that id to newer events
            response = Rest.getUicfromid(DEVICE_UID)

        DEVICE_NEW_LID = response.headers['X-Cafpa-LowerEventId']
        DEVICE_NEW_UID = response.headers['X-Cafpa-UpperEventId']

        if (DEVICE_NEW_UID > DEVICE_UID):
            write = 1
        else:
            LOG.info("No new events")

        if response.status_code == 200 and write == 1:
            with open(file559, "wb") as f:
                f.write(response.text)
                f.close()
            return response.status_code, False, DEVICE_NEW_LID, DEVICE_NEW_UID
        else:
            return response.status_code, False, DEVICE_NEW_LID, DEVICE_NEW_UID

    except requests.exceptions.RequestException as e:
        LOG.warning("ERROR REQUESTS: %s" % str(e))
        return 0, False, DEVICE_LID, DEVICE_UID


# Obtiene tamaño fichero o conjunto de ficheros en un directorio de forma recursiva
def getarchivesize(archive):
    try:
        total_size = os.path.getsize(archive)
        if os.path.isdir(archive):
            for item in os.listdir(archive):
                itempath = os.path.join(archive, item)
                if os.path.isfile(itempath):
                    total_size += os.path.getsize(itempath)
                elif os.path.isdir(itempath):
                    total_size += getarchivesize(itempath)
        return total_size
    except os.error:
        return 0


# Devuelve los N ficheros más antiguos
def oldestfile(rootfolder, count=1, extension=""):
    return heapq.nsmallest(count,
                           (os.path.join(dirname, filename)
                            for dirname, dirnames, filenames in os.walk(rootfolder)
                            for filename in filenames
                            if filename.endswith(extension)),
                           key=lambda fn: os.stat(fn).st_mtime)




def formatShot(shot,vars_shot):
    if len(shot) !=len(vars_shot):
        LOG.error("Variables and register does not match!")
        return shot
    shot_dict = {}
    #Accedo a cada variable del shot
    #shot=zip(vars_shot,shot)
    for i,vars in enumerate(shot):
        #shot[i] = {vars_shot[i]:vars}
        key = str(vars_shot[i])
        shot_dict[key] = vars
    return shot_dict

def formatLogEntries(logentriesjson,alarm_dict_meta,alarm_dict_snap):
    for i in logentriesjson['src'][0]['log_entries']:

        # Se accede a los metadatos
        try:
            alarmindex = i['alarmid']
            metadata = (i['meta'])
            #Formateamos solo en caso de que meta este lleno
            if str(i['meta']) != "":
                var_shot_meta = alarm_dict_meta[alarmindex]
                for j, shot in enumerate(metadata):
                    i['meta'][j] = formatShot(shot, var_shot_meta)
        except KeyError:
            pass

        try:
            snapshot = (i['snapshot'])
            alarmid = (i['alarmid'])
            # Accedo al diccionario de alarmas-snapshots para extraer las variables asociadas al snapshot
            vars_shot_snap = alarm_dict_snap[alarmid]
            # Extraemos los shots de los metadatos y formateamos cada shot introduciendo variable asociada
            for j, shot in enumerate(snapshot):
                i['snapshot'][j] = formatShot(shot, vars_shot_snap)
        except KeyError:
            pass

    return logentriesjson


def ZipandMovetoUpload(filename,filenamefull,ORIGIN_PATH,ZIPDESTINATION_PATH,):

    LOG.info("ZIPPING FILE %s" %(filenamefull))
    zip_fname = ("%s.zip" % filenamefull).replace(ORIGIN_PATH, ZIPDESTINATION_PATH)
    zf = zipfile.ZipFile(zip_fname, 'a')
    zf.write(filenamefull, filename,compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
    # ------------------------------------------------------------------------------
    # Mover ZIP HMI a cola de envío
    # ------------------------------------------------------------------------------
    LOG.info("MOVING %s TO UPLOAD FOLDER" % (filenamefull))
    os.system("mv %s %s" % (zip_fname, zip_fname.replace(SETTINGS.ZPATH559, SETTINGS.UPATH)))
    # ------------------------------------------------------------------------------
    # BORRAR UIC559 Propio sin comprimir
    # ------------------------------------------------------------------------------
    try:
        LOG.info("DELETING UNCOMPRESSED FILES: %s" % filenamefull)
        os.remove(filenamefull)
    except OSError:
        pass

def keepperiod(period,start_time):
    time_consumed = datetime.datetime.utcnow() - start_time
    time_to_wait = (datetime.timedelta(seconds=period) - time_consumed).total_seconds()
    LOG.info("Last cycle duration was: %s secs." % time_consumed.total_seconds())
    LOG.info("Waiting for %s secs." % time_to_wait)
    if time_to_wait > 0:
        time.sleep(time_to_wait)