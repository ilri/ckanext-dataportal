import json

def loadConfigVar(variable):
    #Load the resources database configuration file
    json_data=open('/opt/ckan/lib/default/src/ckanext-ilrimetadata/ckanext/ilrimetadata/resourcedb/config.json')
    #Load the data as JSON
    config = json.load(json_data)
    try:
        return config[variable]
    except:
        return None