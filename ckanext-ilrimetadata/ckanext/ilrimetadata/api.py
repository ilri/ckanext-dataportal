import ckan.plugins.toolkit as toolkit
import json
from ckan.controllers.api import ApiController as CKANApiController

# Recursively goes through the JSON patching url
def findall(v,resource = False,dataset=""):
    if type(v) == type({}):
        for k1 in v:
            if k1 == "url":
                if resource:
                    v[k1] = "https://data.ilri.org/portal/dataset/" + dataset + "/resource/" + v["id"]
            if k1 == "resources":
                v["url"] = "https://data.ilri.org/portal/dataset/" + v["name"]
                findall(v[k1],True,v["name"])
            else:
                findall(v[k1], resource,dataset)
    if type(v) == type([]):
        for x in v:
            findall(x,resource,dataset)


#Patch JSON data to override URL entries
def pathJSON(data):
    obj = json.loads(data)
    findall(obj)
    return json.dumps(obj)


#Controllect to patch API 3 so we protect the resources
class ILRIMetadataAPIOverride(toolkit.BaseController):
    def action(self, logic_function, ver=None):
        #Create the normal CKAN API Controller
        apiController = CKANApiController()
        #Calls function "action" of the CKAN controller and gets the result
        res = apiController.action(logic_function,ver)
        #Patch the JSON so we remove the urls
        toolkit.response.content_type = 'application/json'
        return pathJSON(res)

#Controllect to patch API 1,2 so we protect the resources
class ILRIMetadataAPI2Override(toolkit.BaseController):
    def show(self, ver=None, register=None, subregister=None,id=None, id2=None):
        #Create the normal CKAN API Controller
        apiController = CKANApiController()
        #Calls function "show" of the CKAN controller and gets the result
        res = apiController.show(ver,register,subregister,id,id2)
        #Patch the JSON so we remove the urls
        return pathJSON(res)
