import ckan.plugins.toolkit as toolkit
import json

import pprint

def fixData(data):
    res = data
    res = res.replace("\n","")
    res = res.replace("'","")
    res = res.replace('"',"")

    return res

def getJSONFromFile(filename):
    dataFile = open(filename,"r")
    dataArray = []
    for data in dataFile:
        dataArray.append( fixData(data) )
    dataFile.close();
    return json.dumps(dataArray)

class ILRIAPI_list_Controller(toolkit.BaseController):
    def list_countries(self):
        toolkit.response.content_type = 'application/json'
        return getJSONFromFile("/opt/ckan/lib/default/src/ckanext-ilriapi/ckanext/sourcetxt/ilri-countries.txt")

    def list_regions(self):
        toolkit.response.content_type = 'application/json'
        return getJSONFromFile("/opt/ckan/lib/default/src/ckanext-ilriapi/ckanext/sourcetxt/ilri-regions.txt")

    def list_subjects(self):
        toolkit.response.content_type = 'application/json'
        return getJSONFromFile("/opt/ckan/lib/default/src/ckanext-ilriapi/ckanext/sourcetxt/ilri-subjects.txt")

    def list_species(self):
        toolkit.response.content_type = 'application/json'
        return getJSONFromFile("/opt/ckan/lib/default/src/ckanext-ilriapi/ckanext/sourcetxt/ilri-commodities.txt")

    def list_structure(self):
        toolkit.response.content_type = 'application/json'
        toolkit.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        return getJSONFromFile("/opt/ckan/lib/default/src/ckanext-ilriapi/ckanext/sourcetxt/ilri-structure.txt")

    def list_tags(self):
        toolkit.response.content_type = 'application/json'
        toolkit.response.headerlist.append(('Access-Control-Allow-Origin', '*'))

        try:
            tags = toolkit.get_action('tag_list')({}, {})
            return json.dumps(tags)
        except:
            return "{}"

