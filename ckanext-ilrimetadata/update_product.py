import urllib, json, urllib2
import pprint
url = "https://data.ilri.org/portal/api/3/action/package_list"
#url = "http://127.0.0.1:5000/api/3/action/package_list"
response = urllib.urlopen(url)
data = json.loads(response.read())
for dataset in data["result"]:
    print dataset
    try:
        url = "https://data.ilri.org/portal/api/3/action/package_show?id="+dataset
        #url = "http://127.0.0.1:5000/api/3/action/package_show?id=" + dataset
        response = urllib.urlopen(url)
        content = json.loads(response.read())
        currentData = content["result"]
        currentData["ILRI_actyproduct"] = ["Non-spatial"]


        request = urllib2.Request('https://data.ilri.org/portal/api/action/package_update')
        #request = urllib2.Request('http://127.0.0.1:5000/api/action/package_update')

        authorization = ''
        data_string = urllib2.quote(json.dumps(currentData))
        # request = urllib2.Request(
        #    'http://ec2-54-93-187-255.eu-central-1.compute.amazonaws.com/api/action/package_create')

        # Creating a dataset requires an authorization header.
        # Replace *** with your API key, from your user account on the CKAN site
        # that you're creating the dataset on.
        request.add_header('Authorization', authorization)

        # Make the HTTP request.

        #Uncomment the below lines to run the update
        #response = urllib2.urlopen(request, data_string)
        #if response.code == 200:
        #    print "Done for " + dataset
    except:
        print "Error"
