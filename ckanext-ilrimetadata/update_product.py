import urllib, json, urllib2
import pprint
url = "http://data.ilri.org/portal/api/3/action/package_list"
response = urllib.urlopen(url)
data = json.loads(response.read())
for dataset in data["result"]:
    print dataset
    try:
        url = "http://data.ilri.org/portal/api/3/action/package_show?id="+dataset
        response = urllib.urlopen(url)
        content = json.loads(response.read())
        currentData = content["result"]
        currentData["ILRI_actyproduct"] = ["Not GIS product"]


        request = urllib2.Request(
            'http://data.ilri.org/portal/api/action/package_update')

        authorization = 'secret!'
        data_string = urllib2.quote(json.dumps(currentData))
        # request = urllib2.Request(
        #    'http://ec2-54-93-187-255.eu-central-1.compute.amazonaws.com/api/action/package_create')

        # Creating a dataset requires an authorization header.
        # Replace *** with your API key, from your user account on the CKAN site
        # that you're creating the dataset on.
        request.add_header('Authorization', authorization)

        # Make the HTTP request.
        response = urllib2.urlopen(request, data_string)
        if response.code == 200:
            print "Done for " + dataset
    except:
        print "Error"
