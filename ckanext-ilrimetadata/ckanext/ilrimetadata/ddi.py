from xml.etree.ElementTree import Element, ElementTree as ET, tostring
import json


#This fuction add each resource to the DDI XML
def getFileDscr(resource,url):
    fileTxt = Element("fileTxt")

    fileTxt.attrib["URI"] = url + "/resource/" + resource["id"] + "/request"

    node = Element("fileName")
    node.text = resource["name"]
    fileTxt.append(node);

    node = Element("fileCont")
    node.text = resource["resource_description"]
    fileTxt.append(node);

    node = Element("fileType")
    if resource["format"] == "getdata":
        node.text = "GetData Service: Multiple formats available"
    else:
        node.text = resource["format"];
    fileTxt.append(node);

    return fileTxt

def arraytoSring(data):
    res = ""
    for value in data:
        res = res + value + ","

    res = res[:len(res)-1]

    return res;

#Creates a DDI 2.5 XML
def createDDIXML(pkginfo,url):

    codeBook = Element("codeBook")
    docDscr = Element("docDscr")
    stdyDscr = Element("stdyDscr")
    fileDscr = Element("fileDscr")


    codeBook.append(docDscr)
    codeBook.append(stdyDscr)
    codeBook.append(fileDscr)

    codeBook.attrib["schemaLocation"] = "http://www.ddialliance.org/Specification/DDI-Codebook/2.5/XMLSchema/codebook.xsd"
    codeBook.attrib["version"] = "2.5"

    #*******************************************Project Metadata******************************************************

    node = Element("citation")
    docDscr.append(node);

    #Citatation from Study
    #Subjects
    node2 = Element("biblCit")
    node.append(node2)
    node2.text = pkginfo['ILRI_actycitation']

    #Subjects
    node2 = Element("notes")
    node.append(node2)
    node2.attrib["subject"] = "Citation acknowledgments"
    node2.text = pkginfo['ILRI_actycitationacknowledge']

    #Subjects
    node2 = Element("notes")
    node.append(node2)
    node2.attrib["subject"] = "Thematic area"
    node2.text = arraytoSring(pkginfo['ILRI_prjsubjects'])

    #Project Start Date
    node2 = Element("notes")
    node.append(node2)
    node2.attrib["subject"] = "Project start date"
    node2.text = pkginfo['ILRI_prjsdate']

    #Project End Date
    node2 = Element("notes")
    node.append(node2)
    node2.attrib["subject"] = "Project end date"
    node2.text = pkginfo['ILRI_prjedate']

    #Regions covered
    node2 = Element("notes")
    node.append(node2)
    node2.attrib["subject"] = "Regions covered by project"
    node2.text = pkginfo['ILRI_prjregions']

    #Countries covered
    node2 = Element("notes")
    node.append(node2)
    node2.attrib["subject"] = "Countries covered by project"
    node2.text = pkginfo['ILRI_prjcountries'].replace("+",",")

    #Species
    node2 = Element("notes")
    node.append(node2)
    node2.attrib["subject"] = "Species"
    node2.text = pkginfo['ILRI_prjspecies']

    #Website
    node2 = Element("holdings")
    node.append(node2)
    node2.attrib["URI"] = pkginfo['ILRI_prjwebsite']

    node2 = Element("prodStmt")
    node.append(node2)

    groups = ""
    for grp in pkginfo['groups']:
        groups = groups + grp['description'] + ","

    groups = groups[:len(groups)-1]

    #CRP and programs
    node3 = Element("producer")
    node2.append(node3)
    node3.text = groups

    #Grant code
    node3 = Element("grantNo")
    node2.append(node3)
    node3.text = pkginfo['ILRI_prjgrant']

    #Donor
    node3 = Element("fundAg")
    node2.append(node3)
    node3.text = pkginfo['ILRI_prjdonor']

    node2 = Element("rspStmt")
    node.append(node2)

    #PI
    node3 = Element("authEnty")
    node2.append(node3)
    node3.text = pkginfo['ILRI_prjpi']

    #Other staff
    node3 = Element("othld")
    node2.append(node3)
    node3.text = pkginfo['ILRI_prjstaff']

    #Partners
    node3 = Element("othld")
    node2.append(node3)
    node3.text = pkginfo['ILRI_prjpartners']

    node2 = Element("titlStmt")
    node.append(node2)

    #Project Title
    node3 = Element("titl")
    node2.append(node3)
    node3.text = pkginfo['ILRI_prjtitle']

    #Abstract
    node3 = Element("parTitl")
    node2.append(node3)
    node3.text = pkginfo['ILRI_prjabstract']

    node3 = Element("IDNo")
    node2.append(node3)
    node3.attrib["agency"] = "URL"
    node3.text = url.replace("/metadataddi","")


    #***************************************** Study Metadata ********************************************************

    node = Element("citation")
    stdyDscr.append(node);



    #Species
    node2 = Element("notes")
    node2.attrib["subject"] = "Species"
    node2.text = arraytoSring(pkginfo['ILRI_actyspecies'])
    node.append(node2)


    #CopyRight
    node2 = Element("prodStmt")
    node.append(node2)

    node3 = Element("copyright")
    node2.append(node3)
    node3.text = pkginfo['license_title']


    #Data Owner
    node2 = Element("distStmt")
    node.append(node2)

    node3 = Element("distrbtr")
    node2.append(node3)
    try:
        node3.text = pkginfo['ILRI_actyipownership']
    except:
        node3.text = ""



    #Title
    node2 = Element("titlStmt")
    node.append(node2)

    node3 = Element("titl")
    node2.append(node3)
    node3.text = pkginfo['title']

    #Main researcher
    node2 = Element("rspStmt")
    node.append(node2)

    node3 = Element("authenty")
    node2.append(node3)
    node3.text = pkginfo['ILRI_actypi']

    node3 = Element("othld")
    node2.append(node3)
    node3.text = pkginfo['ILRI_actystaff']
    node3.attrib["role"] = "Other staff involved"

    node3 = Element("othld")
    node2.append(node3)
    node3.text = pkginfo['ILRI_actypartners']
    node3.attrib["role"] = "Partners"


    #Abstract
    node = Element("stdyInfo")
    stdyDscr.append(node);

    node2 = Element("abstract")
    node.append(node2)
    node2.text = pkginfo['notes']

    #Regions and countries and national level
    node = Element("stdyInfo")
    stdyDscr.append(node);

    node2 = Element("sumDscr")
    node.append(node2)

    #Collection data
    node3 = Element("collDate")
    node2.append(node3)
    node3.text = pkginfo['ILRI_actydatecollected']

    #Regions
    node3 = Element("geogCover")
    node2.append(node3)
    node3.text = arraytoSring(pkginfo['ILRI_actyregions'])

    node4 = Element("concept")
    node3.append(node4)
    node4.text = "Regions covered"

    #Regions
    node3 = Element("geogCover")
    node2.append(node3)

    node4 = Element("concept")
    node3.append(node4)
    node4.text = "Countries covered"

    #National level
    node3 = Element("geogCover")
    node2.append(node3)
    node3.text = pkginfo['ILRI_actynatlevel']

    node4 = Element("concept")
    node3.append(node4)
    node4.text = "National level areas covered"

    #Bouding box

    node3 = Element("geoBndBox")
    node2.append(node3)

    try:
        jbox = json.loads(pkginfo['ILRI_actymapextent'])
        node4 = Element("westBL")
        node3.append(node4)
        node4.text = str(jbox['southWestLong'])

        node4 = Element("eastBL")
        node3.append(node4)
        node4.text = str(jbox['northEastLong'])

        node4 = Element("southBL")
        node3.append(node4)
        node4.text = str(jbox['southWestLat'])

        node4 = Element("northBL")
        node3.append(node4)
        node4.text = str(jbox['northEastLat'])
    except:
        node4 = Element("westBL")
        node3.append(node4)
        node4.text = ""

        node4 = Element("eastBL")
        node3.append(node4)
        node4.text = ""

        node4 = Element("southBL")
        node3.append(node4)
        node4.text = ""

        node4 = Element("northBL")
        node3.append(node4)
        node4.text = ""

    #Data accessibility
    node = Element("dataAccs")
    stdyDscr.append(node);

    #Availability date
    node2 = Element("setAvail")
    node.append(node2)

    node3 = Element("avlStatus")
    node2.append(node3)
    node3.text = pkginfo['ILRI_actydatavailable']

    #Usage conditions
    node2 = Element("useStmt")
    node.append(node2)


    node3 = Element("specPerm")
    node2.append(node3)
    try:
        if pkginfo['ILRI_actyrelconfdata'] == "on":
            node3.text = "Usage onf confidential data could be granted with a signed NDA"
        else:
            node3.text = "Confidential data is not accessible"
    except:
        node3.text = "Confidential data is not accessible"

    node3 = Element("contact")
    node2.append(node3)
    node3.text = pkginfo['ILRI_actycontactperson']

    if pkginfo['resources']:
        for resource in pkginfo['resources']:
            fileDscr.append(getFileDscr(resource,url.replace("/metadataddi","")))

    return tostring(codeBook, encoding='utf8')