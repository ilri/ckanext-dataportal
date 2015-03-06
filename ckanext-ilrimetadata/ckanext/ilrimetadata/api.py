import ckan.plugins.toolkit as toolkit
import json
from ckan.controllers.api import ApiController as CKANApiController

# Recursively goes through the JSON patching url
def findall(v):
  if type(v) == type({}):
     for k1 in v:
         if k1 == "url":
            v[k1] = "http://data.ilri.org/portal/"
         findall(v[k1])
  if type(v) == type([]):
      for x in v:
          findall(x)

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
