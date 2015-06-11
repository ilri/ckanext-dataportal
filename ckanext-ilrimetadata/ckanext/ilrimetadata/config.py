import json

def loadConfigVar(variable):
    #Load the resources database configuration file
    json_data=open('/opt/ckan-ilri2.2/src/ckanext-ilrimetadata/ckanext/ilrimetadata/resourcedb/config-local.json')
    #Load the data as JSON
    config = json.load(json_data)
    try:
        return config[variable]
    except:
        return None