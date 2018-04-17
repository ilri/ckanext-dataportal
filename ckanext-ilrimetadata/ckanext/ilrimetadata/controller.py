import ckan.plugins.toolkit as toolkit

from ddi import createDDIXML

from procrequest import processToken
from procrequest import processRequestToken
from procrequest import processGuest
from procrequest import processUser

from ckan.lib.base import c, abort
from ckan.model import Package
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns

import uuid
import datetime

from .responsefile import getCKANFile
from .responsefile import getDataFile

from .enddecdata import encodeData,decodeData

import ast
#from .config import loadConfigVar
from pylons import config

tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

NotFound = logic.NotFound

#This handles a GetDATA request
def getDataRequest(request,database,table,format):
    params = request.GET
    if "data" in params.keys():
        try:
            #Replace back the + and / characters from the base64
            encdata = params['data']
            encdata = encdata.replace("[","+")
            encdata = encdata.replace("]","/")
            encdata = encdata.replace("}","=")

            #Decode the data
            data = decodeData(encdata)
        except Exception,e:
            abort(404, 'You do not have access to this resource. Decode error ' + str(e))
        try:
            jdata = ast.literal_eval(data)

            if jdata["key"] == config['ilriextensions.getdata.key']:

                requestID = jdata["requestID"]
                confidential = jdata["confidential"]

                now = datetime.datetime.now()
                reqTime = datetime.datetime.strptime(jdata["datetime"],'%Y-%m-%d %H:%M:%S.%f')
                #Check if the request is not more than 1 minutes old
                tMinutes = 55
                try:
                    tMinutes = (now-reqTime).total_seconds()/60
                except:
                    #For Python 2.6.X
                    tMinutes = (now-reqTime).days * 1440 + (now-reqTime).seconds / 60

                print tMinutes
                if tMinutes <= 5:
                    return getDataFile(requestID,toolkit.response,database,table,format,confidential)
                else:
                    abort(404, 'This request has expired')
            else:
                abort(404, 'You do not have access to this resource')

        except Exception,e:
            abort(404, 'You do not have access to this resource.' + str(e))
    else:
        abort(404, 'You do not have access to this resource')


class ILRIMetadataDDIController(toolkit.BaseController):
    def getMetadataDDI(self,id):
        toolkit.response.content_type = 'application/xml'
        c.pkg = Package.get(id)
        if c.pkg is None:
            abort(404, 'Dataset not found')
        pkginfo = toolkit.get_action('package_show')({}, {'id': id})
        try:
            return createDDIXML(pkginfo,toolkit.request.url)
        except Exception,e:
            print str(e)
            return "[]"

#This is the GetData controller for databases
class ILRIMetadataGetDatabaseController(toolkit.BaseController):
    def GetDatabase(self,database,format):
        return getDataRequest(toolkit.request,database,None,format)



class ILRIMetadataGetTableController(toolkit.BaseController):
    def GetTable(self,database,table,format):
        return getDataRequest(toolkit.request,database,table,format)


#Controler to show the non-disclaimer agreement
class ILRIMetadataNDAController(toolkit.BaseController):
    def displayAgreement(self, id, resource_id):
        try:
            package_dict = toolkit.get_action('package_show')({}, {'id': id})
        except NotFound:
            abort(404, 'Dataset not found')
        try:
            resource_dict = toolkit.get_action('resource_show')({}, {'id': resource_id})
        except NotFound:
            abort(404, 'Resource not found')

        vars = {'package': package_dict,  'resource': resource_dict}
        return toolkit.render('ilripages/nda.html',extra_vars=vars)

    def displayAgreement2(self):
        return toolkit.render('ilripages/nda2.html')

    def displayLicense(self, id, resource_id):
        try:
            package_dict = toolkit.get_action('package_show')({}, {'id': id})
        except NotFound:
            abort(404, 'Dataset not found')
        try:
            resource_dict = toolkit.get_action('resource_show')({}, {'id': resource_id})
        except NotFound:
            abort(404, 'Resource not found')

        vars = {'package': package_dict,  'resource': resource_dict}
        return toolkit.render('ilripages/public.html',extra_vars=vars)

#Controllet that handles the request of resources
class ILRIMetadataRequestInfoController(toolkit.BaseController):
    def requestInfo(self, id, resource_id, data = None):


        #Dict that contain validation errors. Used to display error in form
        error_summary = {}
        #Dict that contains the form data
        data = {}

        #Request data is passed encrypted to the GetDataService as HTTP request variable
        requestData = {}
        #Key is to authenticate that the request of GetData comes from this plugin only
        requestData["key"] = config['ilriextensions.getdata.key']
        #DateTime of the request to GeData
        requestData["datetime"] = str(datetime.datetime.now())

        #Initialize the form data
        data["field_user"] = ""
        data["field_name"] = ""
        data["field_email"] = ""
        data["field_organization"] = ""
        data["field_organizationType"] = ""
        data["field_country"] = ""
        data["field_notes"] = ""
        data["field_otherdatasets"] = ""
        data["field_hearfrom"] = ""
        data["field_aggrement"] = ""

        try:
            package_dict = toolkit.get_action('package_show')({}, {'id': id})
        except NotFound:
            abort(404, 'Dataset not found')

        try:
            resource_dict = toolkit.get_action('resource_show')({}, {'id': resource_id})
        except NotFound:
            abort(404, 'Resource not found')

        if toolkit.request.method == 'POST':
            #Get the data from the POST request
            formdata = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(toolkit.request.POST))))

            #If the post is a submitted token
            if "submittoken" in formdata.keys():
                requestID = uuid.uuid4()
                if processToken(requestID,toolkit.request.remote_addr,package_dict["id"],resource_id,formdata["field_token"],formdata["field_resourceFormat"]):
                    if resource_dict['format'].lower() != 'getdata':
                        #Get the resource if its not getDATA just return the file
                        return getCKANFile(toolkit.response,resource_dict)
                    else:
                        #For a getDATA resource we encrypt the request data and pass it to the request form with
                        #content type = downloadstart. This content type creates a DIV that Javascript catches to
                        #request the resource. This because GetDAtA needs to process the request and generate the output
                        #which might take few seconds so its better to show the page informing this delay and then
                        #get the data

                        requestData["requestID"] = str(requestID)
                        requestData["confidential"] = "true"

                        #We replace the + and / in base64 so it does not conflict with url
                        encdata = encodeData(str(requestData))
                        encdata = encdata.replace("+","[")
                        encdata = encdata.replace("/","]")
                        encdata = encdata.replace("=","}")

                        vars = {'package': package_dict,  'resource': resource_dict, 'contentType': "downloadstart", 'format': formdata["field_resourceFormat"], 'requestData': encdata}
                        return toolkit.render('ilripages/request_info.html',extra_vars=vars)
                else:
                    error_summary["token"] = "Invalid token or this token does not give you confidential access to this resource"
                    vars = {'package': package_dict,  'resource': resource_dict, 'contentType': "request",'confidential': "true", 'format': formdata["field_resourceFormat"], 'error_summary': error_summary, 'data': data}
                    return toolkit.render('ilripages/request_info.html',extra_vars=vars)

            #If the post is a request for token
            if "requesttoken" in formdata.keys():
                data["field_name"] = formdata["field_name"]
                data["field_email"] = formdata["field_email"]
                data["field_organization"] = formdata["field_organization"]
                data["field_organizationType"] = formdata["field_organizationType"]
                data["field_country"] = formdata["field_country"]
                data["field_notes"] = formdata["field_notes"]
                data["field_hearfrom"] = formdata["field_hearfrom"]
                data["field_otherdatasets"] = formdata["field_otherdatasets"]
                if "field_aggrement" in formdata.keys():
                    data["field_aggrement"] = 'yes'
                else:
                    data["field_aggrement"] = 'no'


                result, error_summary = processRequestToken(uuid.uuid4(),toolkit.request.remote_addr,data,package_dict["id"],resource_id)
                if result == True:
                    vars = {'package': package_dict,  'resource': resource_dict, 'contentType': "tokenrequestsent",'confidential': "true", 'format': formdata["field_resourceFormat"], 'error_summary': error_summary, 'data': data }
                    return toolkit.render('ilripages/request_info.html',extra_vars=vars)
                else:
                    vars = {'package': package_dict,  'resource': resource_dict, 'contentType': "request",'confidential': "true", 'format': formdata["field_resourceFormat"], 'error_summary': error_summary, 'data': data }
                    return toolkit.render('ilripages/request_info.html',extra_vars=vars)

            #If the post is a request for download
            if "requestdownload" in formdata.keys():
                data["field_name"] = formdata["field_name"]
                data["field_email"] = formdata["field_email"]
                data["field_organization"] = formdata["field_organization"]
                data["field_organizationType"] = formdata["field_organizationType"]
                data["field_country"] = formdata["field_country"]
                data["field_notes"] = formdata["field_notes"]
                data["field_hearfrom"] = formdata["field_hearfrom"]
                if "field_aggrement" in formdata.keys():
                    data["field_aggrement"] = 'yes'
                else:
                    data["field_aggrement"] = 'no'

                requestID = uuid.uuid4()
                result, error_summary = processGuest(requestID,toolkit.request.remote_addr,resource_id,data,formdata["field_resourceFormat"])
                if result == True:
                    if resource_dict['format'].lower() != 'getdata':
                        #Get the resource if its not getDATA just return the file
                        return getCKANFile(toolkit.response,resource_dict)
                    else:
                        #For a getDATA resource we encrypt the request data and pass it to the request form with
                        #content type = downloadstart. This content type creates a DIV that Javascript catches to
                        #request the resource. This because GetDAtA needs to process the request and generate the output
                        #which might take few seconds so its better to show the page informing this delay and then
                        #get the data

                        requestData["requestID"] = str(requestID)
                        requestData["confidential"] = "false"

                        #We replace the + and / in base64 so it does not conflict with url
                        encdata = encodeData(str(requestData))
                        encdata = encdata.replace("+","[")
                        encdata = encdata.replace("/","]")
                        encdata = encdata.replace("=","}")

                        vars = {'package': package_dict,  'resource': resource_dict, 'contentType': "downloadstart", 'confidential': "false", 'format': formdata["field_resourceFormat"], 'requestData': encdata}
                        return toolkit.render('ilripages/request_info.html',extra_vars=vars)
                else:
                    vars = {'package': package_dict,  'resource': resource_dict, 'contentType': "request",'confidential': "false", 'format': formdata["field_resourceFormat"], 'error_summary': error_summary, 'data': data }
                    return toolkit.render('ilripages/request_info.html',extra_vars=vars)

            #If the post is a login request
            if "privatelogin" in formdata.keys():
                data["field_user"] = formdata["field_user"]

                requestID = uuid.uuid4()
                if processUser(requestID,toolkit.request.remote_addr,package_dict["id"],resource_id,formdata["field_user"],formdata["field_password"],formdata["field_resourceFormat"]):
                    if resource_dict['format'].lower() != 'getdata':
                        #Get the resource if its not getDATA just return the file
                        return getCKANFile(toolkit.response,resource_dict)
                    else:
                        #For a getDATA resource we encrypt the request data and pass it to the request form with
                        #content type = downloadstart. This content type creates a DIV that Javascript catches to
                        #request the resource. This because GetDAtA needs to process the request and generate the output
                        #which might take few seconds so its better to show the page informing this delay and then
                        #get the data

                        requestData["requestID"] = str(requestID)
                        requestData["confidential"] = "true"

                        #We replace the + and / in base64 so it does not conflict with url
                        encdata = encodeData(str(requestData))
                        encdata = encdata.replace("+","[")
                        encdata = encdata.replace("/","]")
                        encdata = encdata.replace("=","}")

                        vars = {'package': package_dict,  'resource': resource_dict, 'contentType': "downloadstart", 'format': formdata["field_resourceFormat"], 'requestData':  encdata}
                        return toolkit.render('ilripages/request_info.html',extra_vars=vars)
                else:
                    error_summary["Invalid credentials"] = "Invalid user or password. Or your user cannot access this resource"
                    vars = {'package': package_dict,  'resource': resource_dict, 'contentType': "request",'confidential': "true", 'format': formdata["field_resourceFormat"], 'error_summary': error_summary, 'data': data }
                    return toolkit.render('ilripages/request_info.html',extra_vars=vars)

        else:
            #The request is a GET so we show the form
            #The form gets the resource dict so Jinja can draw the Form depending of the resource type:
            #Public, Confidential or Private
            params = toolkit.request.GET

            confParam = "false"
            if "confidential" in params.keys():
                confParam = params['confidential']

            formatParam = "csv"
            if "outputFormat" in params.keys():
                formatParam = params['outputFormat']

            vars = {'package': package_dict,  'resource': resource_dict, 'contentType': 'request','confidential': confParam, 'format': formatParam, 'error_summary': error_summary, 'data': data }
            return toolkit.render('ilripages/request_info.html',extra_vars=vars)