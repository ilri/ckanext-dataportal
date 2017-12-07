import ckan.lib.uploader as uploader
import ckan.lib.base as base
from ckan.common import _
import ckan.lib.helpers as h
import mimetypes
import os
from subprocess import call
from pylons import config

abort = base.abort


#Creates an file download iterator of 4096 bytes. So a massive file is not loaded into memory
class FileIterator(object):
     chunk_size = 4096
     def __init__(self, filename):
         self.filename = filename
         self.fileobj = open(self.filename, 'rb')
     def __iter__(self):
         return self
     def next(self):
         chunk = self.fileobj.read(self.chunk_size)
         if not chunk:
             raise StopIteration
         return chunk
     __next__ = next # py3 compat

#An Object containing the file download iterator
class FileIterable(object):
     def __init__(self, filename):
         self.filename = filename
     def __iter__(self):
         return FileIterator(self.filename)

#This fuction gets the file stored in the server and response it to the request.
def getCKANFile(response,resourceInfo):
    if resourceInfo.get('url_type') == 'upload':
        upload = uploader.ResourceUpload(resourceInfo)
        filepath = upload.get_path(resourceInfo['id'])

        if not os.path.isfile(filepath):
            abort(404, _('Resource data not found'))

        content_type, content_enc = mimetypes.guess_type(resourceInfo.get('url',''))

        #Retrives the filename
        fileName = resourceInfo.get('url','')
        index = fileName.rfind('/')
        fileName = fileName[-(len(fileName)-index-1):]

        response.headers['Content-Type'] = content_type
        response.content_disposition = 'attachment; filename="' + fileName + '"'

        response.app_iter = FileIterable(filepath)
        response.content_length = os.path.getsize(filepath)

        return response
    else:
        print "CKAN link"
        h.redirect_to(resourceInfo['url'])

#Process a GetData Request
def getDataFile(requestID,response,database,table,format,confidential):


    #Load configuration variables
    getDataDir = config["ilriextensions.tempdir"]
    getDataHost = config["ilriextensions.getdata.host"]
    getDataPort = config["ilriextensions.getdata.port"]
    getDataUser = config["ilriextensions.getdata.user"]
    getDataPassword = config["ilriextensions.getdata.password"]
    mySQLToFileBin = config["ilriextensions.getdata.mysqltofilebin"]

    #Check first if the file exists. Meaning was requested and is less than 5 minute old
    if os.path.isfile(getDataDir + "/" + requestID + ".zip"):
        filepath = getDataDir + "/" + requestID + ".zip"
        content_type, content_enc = mimetypes.guess_type(filepath)
        response.headers['Content-Type'] = content_type
        if table is None:
            response.content_disposition = 'attachment; filename="' + database + '.zip"'
        else:
            response.content_disposition = 'attachment; filename="' + database + '-' + table + '.zip"'
        response.app_iter = FileIterable(filepath)
        response.content_length = os.path.getsize(filepath)
        return response

    #Creates a directory in the GetDATA repository using the request ID
    if not os.path.isdir(getDataDir + "/" + requestID):
        os.makedirs(getDataDir + "/" + requestID)

    #Runs mySQLToFile
    args = []
    args.append(mySQLToFileBin)
    args.append("-H " + getDataHost)
    args.append("-P " + getDataPort)
    args.append("-u " + getDataUser)
    args.append("-p " + getDataPassword)
    args.append("-o " + format.upper())
    #if format.upper() == "STATA" or format.upper() == "SPSS":
    #    args.append('-n " "')
    args.append("-d " + getDataDir + "/" + requestID + "/")
    args.append("-s " + database)
    if table is not None:
        args.append("-t " + table)

    if confidential == "true":
        args.append("-T")
    result = call(args)
    print args

    #If MySQLToFile returned 0 = OK
    if result == 0:
        #Run Linux Zip to compress the directory
        zipargs = []
        zipargs.append("/usr/bin/zip")
        zipargs.append("-r")
        zipargs.append("-j")
        zipargs.append(getDataDir + "/" + requestID + ".zip")
        zipargs.append(getDataDir + "/" + requestID)
        result = call(zipargs)

        #If Linux Zip returned 0 = OK then return the file as a response
        if result == 0:
            filepath = getDataDir + "/" + requestID + ".zip"
            if not os.path.isfile(filepath):
                abort(404, _('Resource data not found'))

            content_type, content_enc = mimetypes.guess_type(filepath)
            response.headers['Content-Type'] = content_type
            if table is None:
                response.content_disposition = 'attachment; filename="' + database + '.zip"'
            else:
                response.content_disposition = 'attachment; filename="' + database + '-' + table + '.zip"'
            response.app_iter = FileIterable(filepath)
            response.content_length = os.path.getsize(filepath)
            return response

        else:
            abort(404, _('GetDATA Error running linux ZIP. Your request was: ' + requestID + ". Contact RMG at ILRI"))
    else:
        abort(404, _('GetDATA Error running MySQLToFile. Your request was: ' + requestID + ". Contact RMG at ILRI"))









