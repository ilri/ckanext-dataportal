import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import routes.mapper as r

import logging
import json,os

import ckan.model as model
import ckan.logic.validators as validators
import ckan.lib.navl.dictization_functions as df
from ckan.common import _

from .connection import getSession,closeSession
from .dbmodels import resourcestatsModel

FeaturedGroups = []

#This function generates counts of datasets, resources and downloads by group
def addFesturedCount(downloadData,group,groupInfo):
    groupData = {}
    total = 0
    for dasatet in groupInfo["packages"]:
        total = total + 1
        for resource in dasatet["resources"]:
            total = total + 1
            for row in downloadData:
                if row["resource_id"] == resource["id"]:
                    total = total + row["total"]
    groupData["group_id"] = group
    groupData["total"] = total
    FeaturedGroups.append(groupData)

def string_contains(variable,value):
    try:
        variable.index(value)
        return True
    except:
        return False

def getFeaturedGroups(max = 1):

    dbSession = getSession()
    try:
        #Get the number of download per resource


        rescount = dbSession.execute("select resource_id,count(resource_id) as total FROM resourcestats")

        #Move the data to an array
        resources = []
        data = {}
        for row in rescount:
            data["resource_id"] = row.resource_id
            data["total"] = row.total
            resources.append(data)

        closeSession(dbSession)

        #Get the list of groups
        group_list = toolkit.get_action('group_list')({}, {})
        for group in group_list:
            #Get the details of each group
            group_info = toolkit.get_action('group_show')({}, {'id': group})
            #Count the features of the group
            addFesturedCount(resources,group,group_info)

        #Order the FeaturedGroups by total
        FeaturedGroups.sort(key=lambda x: x["total"],reverse=True)

        #print FeaturedGroups
        #Move the data of the group to the result array.
        result = []
        count = 0
        for group in FeaturedGroups:
            group_info = toolkit.get_action('group_show')({}, {'id': group["group_id"]})
            result.append(group_info)
            count = count +1
            if count == max:
                break

        return result
    except:
        closeSession(dbSession)
        return []



#This helper function retrives the number of download for a resource
def getResourceStats(resourceID):
    dbSession = getSession()
    try:
        res = dbSession.query(resourcestatsModel).filter_by(resource_id = resourceID).count()
        closeSession(dbSession)
        return res
    except:
        closeSession(dbSession)
        return 0



# Reads data from a textFile and converts it to an array
# Used by the vocabulary fuctions
def getArrayFromFile(filename):
    try:
        logging.info("Loading file: " + filename)
        dataFile = open(filename,"r")
        dataArray = []
        for data in dataFile:
            dataArray.append( data.replace("\n","") )
        dataFile.close()
        return dataArray
    except Exception as e:
        logging.info(str(e))
        return []


# This helper function checks if a dataset is added as new or is edited.
# Used to show/hide the option of copying the project and study information from another dataset
def isDatasetNew(url):
    if "/new" in url:
        return True
    else:
        return False

# This helper function checks if the template is showing the list of datasets
# Used to control snippets/package_list.html
def isListDatasets(url):
    if "/dataset" in url or "/organization" in url or "/group" in url:
        return True
    else:
        return False

#This fuction removes unhandled characters from the list of tags
def fixTag(tag):
    res = tag
    res = res.replace(",","_")
    res = res.replace("'","")
    res = res.replace('"',"")
    res = res.replace('(',"")
    res = res.replace(')',"")

    return res


def deleteVocab(vocName,vocListFile):

    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}

    data = {'id': vocName}
    data2 = {'id': vocName}

    for tag in getArrayFromFile(vocListFile):
        data = {'id': fixTag(tag), 'vocabulary_id': vocName}
        try:
            toolkit.get_action('tag_delete')(context, data)
            logging.info("Tag {0} deleted".format(tag))
        except:
            print "Tag " + tag + " Does not exists"


    toolkit.get_action('vocabulary_delete')(context, data2)
    print vocName + " vocabulary deleted."

#This function creates a vocabulary if it does not exists and add the tags from a source file.
def createVocabulary(vocID,sourceFile):
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
        data = {'id': vocID}
        vocab = toolkit.get_action('vocabulary_show')(context, data)
        print vocID + " vocabulary already exists. Loading list for update"
        for tag in getArrayFromFile(sourceFile):
            data = {'name': fixTag(tag), 'vocabulary_id': vocab['id']}
            try:
                toolkit.get_action('tag_create')(context, data)
                print "Tag {0} added to vocab '{1}'".format(tag,vocID)
            except Exception as e:
                print str(e)
                pass

    except toolkit.ObjectNotFound:
        logging.info("Creating vocab '{0}'".format(vocID))
        data = {'name': vocID}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        try:
            for tag in getArrayFromFile(sourceFile):
                logging.info("Adding tag {0} to vocab '{1}'".format(tag,vocID))
                data = {'name': fixTag(tag), 'vocabulary_id': vocab['id']}
                toolkit.get_action('tag_create')(context, data)
                logging.info("Tag {0} added to vocab '{1}'".format(tag,vocID))
        except Exception as e:
            logging.info(str(e))
            pass

    return True

PATH = os.path.dirname(os.path.abspath(__file__))

# This Helper function creates the region vocabulary from a text file
def createRegionsVocab():
    return createVocabulary("ILRI_vocregions",os.path.join(PATH, "sourcetxt/ilri-regions.txt"))


# This Helper function creates the countries vocabulary from a text file
def createCountriesVocab():
    return createVocabulary("ILRI_voccountries",os.path.join(PATH, "sourcetxt/ilri-countries.txt"))

def createProductsVocab():
    return createVocabulary("ILRI_vocproduct",os.path.join(PATH, "sourcetxt/products.txt"))

# This Helper function creates the species vocabulary from a text file
def createSpeciesVocab():
    return createVocabulary("ILRI_vocspecies",os.path.join(PATH, "sourcetxt/ilri-commodities.txt"))


# This Helper function creates the subjects vocabulary from a text file
def createSubjectsVocab():
    return createVocabulary("ILRI_vocsubjects",os.path.join(PATH, "sourcetxt/ilri-subjects.txt"))


#A helper fuction that returs the countries. Used in the request_info.html
def getCountries():
    return getArrayFromFile(os.path.join(PATH, "sourcetxt/ilri-countries.txt"))

def getProducts():
    return getArrayFromFile(os.path.join(PATH, "sourcetxt/products.txt"))

#This helper function returs the current list of datasets.
#Used to populate the combo of source datasets
def getPackageList():
    res = {}

    pkglist = toolkit.get_action('package_list')({},{})
    for package in pkglist:
        pkginfo = toolkit.get_action('package_show')({}, {'id': package})
        res[package] = pkginfo['title']
    return res

#Converts an JSON String into a JSON object.
#Used in the resources to retreive more than url,name and description
def stringToDict(dataString):
    try:
        return json.loads(dataString)
    except:
        return {}

#Return the number of resources
#Used by resource snippets to minimize the number of resources show to two
def getResourceCount(resource_dict):
    return len(resource_dict);

#Return an array of Tags
#Used by dataset snippets to show the different tags
def splitTagsToList(tags,separator):
    return tags.split(separator);

#Return an array of different resource types
#Used by resources where we overwrote the way CKAN gets this list
def getResourceTypes():
    return ['GetDATA','RDF','PDF','ZIP','XLS','CSV','TXT','XML','JSON','HTML','DOC','DOCX','XLSX','PPT','PPTX','Other']

#Return an array of different GetData types
#Used by resources where the resource type is GetDATA
def listGetDataTypes():
    return ['CSV','STATA','SPSS','XML','JSON','SQL']

#This is almost the same as CKAN but instead of passing key we pass the new tag
def convertToTags(vocab,newtag,data,error,context):

    new_tags = newtag

    if not new_tags:
        return
    if isinstance(new_tags, basestring):
        new_tags = [new_tags]

    # get current number of tags
    n = 0
    for k in data.keys():
        if k[0] == 'tags':
            n = max(n, k[1] + 1)

    v = model.Vocabulary.get(vocab)
    if not v:
        raise df.Invalid(_('Tag vocabulary "%s" does not exist') % vocab)
    context['vocabulary'] = v

    for tag in new_tags:
        validators.tag_in_vocabulary_validator(tag, context)

    for num, tag in enumerate(new_tags):
        data[('tags', num + n, 'name')] = tag
        data[('tags', num + n, 'vocabulary_id')] = v.id


#Separate a string of tags into individual tags using separator and then adds each tag using convertToTags
#Used in datasets to store Countries, Regions and Species as vocabulary tags
def stringToTags(key,data,error,context):

    tag_string = data.get(key)

    vocab = "None"
    separator = ","

    #Project Vocabularies

    if key[0] == "ILRI_prjsubjects":
        vocab = "ILRI_vocsubjects"

    #Study Vocabularies
    if key[0] == "ILRI_actyregions":
        vocab = "ILRI_vocregions"

    if key[0] == "ILRI_actycountries":
        vocab = "ILRI_voccountries"
        separator = "+"

    if key[0] == "ILRI_actyspecies":
        vocab = "ILRI_vocspecies"


    #At a certain point in the creation of the dataset tagString is an array. So we test for it
    if type(tag_string) is list:
        tags = tag_string;
    else:
        tags = tag_string.split(separator)


    if vocab == "None":
        raise df.Invalid(_('Tag vocabulary for key "%s" does not exist') % key[0])

    for tag in tags:
        convertToTags(vocab,fixTag(tag),data,error,context)


#This fuction replaces _ characters to , in tags.
#Used by tagsToString
def underscoreToComa(tag):
    return tag.replace("_",",")

# Combines a series of tags into a string of tags separated by separator
# Used in dataset to show the tags properly with tagsManager.js
def tagsToString(tags,separator):
    tag_string = ""
    for tag in tags:
        tag_string = tag_string + underscoreToComa(tag) + separator
    tag_string = tag_string[:len(tag_string)-1]

    return tag_string

def arrayToString(tags):
    if type(tags) is list:
        tag_string = ""
        for tag in tags:
            tag_string = tag_string + tag + ","
        tag_string = tag_string[:len(tag_string)-1]

        return tag_string
    else:
        return tags

class IlrimetadataPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.IFacets)

    def dataset_facets(self,facets_dict, package_type):
        facets_dict['vocab_ILRI_vocregions'] = 'Regions' #We use vocab_ because ILRI_prjregions is a vocabulary
        facets_dict['vocab_ILRI_voccountries'] = 'Countries'
        facets_dict['vocab_ILRI_vocspecies'] = 'Commodities'
        facets_dict['vocab_ILRI_vocsubjects'] = 'Subjects'
        facets_dict['vocab_ILRI_vocproduct'] = 'Product'
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        facets_dict['vocab_ILRI_vocregions'] = 'Regions' #We use vocab_ because ILRI_prjregions is a vocabulary
        facets_dict['vocab_ILRI_voccountries'] = 'Countries'
        facets_dict['vocab_ILRI_vocspecies'] = 'Commodities'
        facets_dict['vocab_ILRI_vocsubjects'] = 'Subjects'
        facets_dict['vocab_ILRI_vocproduct'] = 'Product'
        return facets_dict

    def organization_facets(self,facets_dict, organization_type, package_type):
        facets_dict['vocab_ILRI_vocregions'] = 'Regions' #We use vocab_ because ILRI_prjregions is a vocabulary
        facets_dict['vocab_ILRI_voccountries'] = 'Countries'
        facets_dict['vocab_ILRI_vocspecies'] = 'Commodities'
        facets_dict['vocab_ILRI_vocsubjects'] = 'Subjects'
        facets_dict['vocab_ILRI_vocproduct'] = 'Product'
        return facets_dict



    # These record how many times methods that this plugin's methods are
    # called, for testing purposes.
    num_times_new_template_called = 0
    num_times_read_template_called = 0
    num_times_edit_template_called = 0
    num_times_search_template_called = 0
    num_times_history_template_called = 0
    num_times_package_form_called = 0
    num_times_check_data_dict_called = 0
    num_times_setup_template_variables_called = 0

    #IRoutes
    def before_map(self, map):
        #*********Some bits from CKAN internals to patch the API****************
        GET_POST = dict(method=['GET', 'POST'])
        GET = dict(method=['GET'])

        # CKAN API versioned.
        register_list = [
            'package',
            'dataset',
            'resource',
            'tag',
            'group',
            'related',
            'revision',
            'licenses',
            'rating',
            'user',
            'activity'
        ]
        register_list_str = '|'.join(register_list)


        #************************************************************************


        #This is a better function because in the connect if defines an item for example ilri_policy that then we can use in build_nav_main helper function
        with r.SubMapper(map,  controller='ckanext.ilrimetadata.controller:ILRIMetadataDDIController') as getMetadataDDI:
            getMetadataDDI.connect('getMetadataDDI','/dataset/{id}/metadataddi',action='getMetadataDDI')

        with r.SubMapper(map,  controller='ckanext.ilrimetadata.controller:ILRIMetadataRequestInfoController') as requestInfo:
            requestInfo.connect('requestInfo','/dataset/{id}/resource/{resource_id}/request',action='requestInfo')

        with r.SubMapper(map,  controller='ckanext.ilrimetadata.controller:ILRIMetadataNDAController') as confAggrement:
            confAggrement.connect('displayAgreement','/dataset/{id}/resource/{resource_id}/nda',action='displayAgreement')
            confAggrement.connect('displayAgreement2', '/nda',action='displayAgreement2')

        with r.SubMapper(map,  controller='ckanext.ilrimetadata.controller:ILRIMetadataNDAController') as downloadLicense:
            downloadLicense.connect('downloadLicense','/dataset/{id}/resource/{resource_id}/license',action='displayLicense')

        with r.SubMapper(map,  controller='ckanext.ilrimetadata.controller:ILRIMetadataGetDatabaseController') as GetDatabase:
            GetDatabase.connect('GetDatabase','/getdata/{database}.{format}',action='GetDatabase')

        with r.SubMapper(map,  controller='ckanext.ilrimetadata.controller:ILRIMetadataGetTableController') as GetTable:
            GetTable.connect('GetTable','/getdata/{database}/{table}.{format}',action='GetTable')

        #We override the CKAN 3 API so we can protect the resource URLs
        with r.SubMapper(map, controller='ckanext.ilrimetadata.api:ILRIMetadataAPIOverride', path_prefix='/api{ver:/3|}',ver='/3') as m:
            m.connect('/action/{logic_function}', action='action', conditions=GET_POST)

        #We override the CKAN 2 API so we can protect the resource URLs
        with r.SubMapper(map, controller='ckanext.ilrimetadata.api:ILRIMetadataAPI2Override', path_prefix='/api{ver:/1|/2|}',ver='/1', requirements=dict(register=register_list_str)) as m:
            m.connect('/rest/{register}/{id}', action='show', conditions=GET)

        return map

    def after_map(self, map):
        return map


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ILRIMetadataResDir')

    # Implement  get_helpers of ITemplateHelpers
    def get_helpers(self):
        return {'ILRIMetadata_getResourceCount': getResourceCount,
                'ILRIMetadata_tagsToList': splitTagsToList,
                'ILRIMetadata_getResourceTypes': getResourceTypes,
                'ILRIMetadata_listGetDataTypes': listGetDataTypes,
                'ILRIMetadata_createRegionsVocab': createRegionsVocab,
                'ILRIMetadata_createCountriesVocab': createCountriesVocab,
                'ILRIMetadata_createProductsVocab': createProductsVocab,
                'ILRIMetadata_createSpeciesVocab': createSpeciesVocab,
                'ILRIMetadata_createSubjectsVocab': createSubjectsVocab,
                'ILRIMetadata_stringToDict': stringToDict,
                'ILRIMetadata_getPackageList': getPackageList,
                'ILRIMetadata_isDatasetNew': isDatasetNew,
                'ILRIMetadata_tagsToString': tagsToString,
                'ILRIMetadata_arrayToString': arrayToString,
                'ILRIMetadata_underscoreToComa': underscoreToComa,
                'ILRIMetadata_getCountries': getCountries,
                'ILRIMetadata_getProducts': getProducts,
                'ILRIMetadata_isListDatasets': isListDatasets,
                'ILRIMetadata_getResourceStats': getResourceStats,
                'ILRIMetadata_getFeaturedGroups': getFeaturedGroups,
                'ILRIMetadata_stringContains': string_contains}


    def _add_custom_metadata_to_schema(self, schema):
        # Add our custom_test metadata field to the schema, this one will use
        # convert_to_extras instead of convert_to_tags.
        # Basically it recived the data from the screen the pass it to a series of fuctions. For example
        # ignore_missing then to convert_to_extras

        # Project Level metadata
        schema.update({'ILRI_prjtitle': [toolkit.get_validator('ignore_missing'),
                                         toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjabstract': [toolkit.get_validator('ignore_missing'),
                                            toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_crpandprogram': [toolkit.get_validator('ignore_missing'),
                                              toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjwebsite': [toolkit.get_validator('ignore_missing'),
                                           toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjgrant': [toolkit.get_validator('ignore_missing'),
                                         toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjdonor': [toolkit.get_validator('ignore_missing'),
                                         toolkit.get_converter('convert_to_extras')]})
        schema.update(
            {'ILRI_prjpi': [toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjpiemail': [toolkit.get_validator('ignore_missing'),
                                           toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjstaff': [toolkit.get_validator('ignore_missing'),
                                         toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjpartners': [toolkit.get_validator('ignore_missing'),
                                            toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjsdate': [toolkit.get_validator('ignore_missing'),
                                         toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjedate': [toolkit.get_validator('ignore_missing'),
                                         toolkit.get_converter('convert_to_extras')]})

        schema.update({'ILRI_prjregions': [toolkit.get_validator('ignore_missing'),
                                           toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjcountries': [toolkit.get_validator('ignore_missing'),
                                             toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_prjspecies': [toolkit.get_validator('ignore_missing'),
                                           toolkit.get_converter('convert_to_extras')]})

        # Project Vocabularies
        schema.update({'ILRI_prjsubjects': [toolkit.get_validator('ignore_missing'), stringToTags]})

        # Study Level metadata
        schema.update({'ILRI_actytitle': [toolkit.get_validator('ignore_missing'),
                                          toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actyabstract': [toolkit.get_validator('ignore_missing'),
                                             toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actyotheruse': [toolkit.get_validator('ignore_missing'),
                                             toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actycontactperson': [toolkit.get_validator('ignore_missing'),
                                                  toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actycontactemail': [toolkit.get_validator('ignore_missing'),
                                                 toolkit.get_converter('convert_to_extras')]})

        schema.update({'ILRI_actycustodian': [toolkit.get_validator('ignore_missing'),
                                              toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actycustodianemail': [toolkit.get_validator('ignore_missing'),
                                                   toolkit.get_converter('convert_to_extras')]})

        schema.update(
            {'ILRI_actypi': [toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actypiemail': [toolkit.get_validator('ignore_missing'),
                                            toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actystaff': [toolkit.get_validator('ignore_missing'),
                                          toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actypartners': [toolkit.get_validator('ignore_missing'),
                                             toolkit.get_converter('convert_to_extras')]})

        # Study Vocabularies
        schema.update({'ILRI_actyregions': [toolkit.get_validator('ignore_missing'), stringToTags]})
        schema.update({'ILRI_actycountries': [toolkit.get_validator('ignore_missing'), stringToTags]})
        schema.update({'ILRI_actyspecies': [toolkit.get_validator('ignore_missing'), stringToTags]})

        schema.update({'ILRI_actycountries': [toolkit.get_validator('ignore_missing'), stringToTags]})

        schema.update({'ILRI_actyproduct': [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_tags')('ILRI_vocproduct')]})

        schema.update({'ILRI_actyprojection': [toolkit.get_validator('ignore_missing'),
                                                  toolkit.get_converter('convert_to_extras')]})

        schema.update({'ILRI_actyresolution': [toolkit.get_validator('ignore_missing'),
                                               toolkit.get_converter('convert_to_extras')]})


        schema.update({'ILRI_actynatlevel': [toolkit.get_validator('ignore_missing'),
                                             toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actymapextent': [toolkit.get_validator('ignore_missing'),
                                              toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actymapzoom': [toolkit.get_validator('ignore_missing'),
                                            toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actyboundbox': [toolkit.get_validator('ignore_missing'),
                                             toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actyboundboxcenter': [toolkit.get_validator('ignore_missing'),
                                                   toolkit.get_converter('convert_to_extras')]})

        schema.update({'ILRI_actydatecollected': [toolkit.get_validator('ignore_missing'),
                                                  toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actydatecollectedend': [toolkit.get_validator('ignore_missing'),
                                                     toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actydatavailable': [toolkit.get_validator('ignore_missing'),
                                                 toolkit.get_converter('convert_to_extras')]})

        schema.update({'ILRI_actyrelconfdata': [toolkit.get_validator('ignore_missing'),
                                                toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actyfarmconsent': [toolkit.get_validator('ignore_missing'),
                                                toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actyipownership': [toolkit.get_validator('ignore_missing'),
                                                toolkit.get_converter('convert_to_extras')]})

        # schema.update({'ILRI_actydataowner': [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras')]})
        # schema.update({'ILRI_actysharingagreement': [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras')]})
        # schema.update({'ILRI_actyconfideclaration': [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras')]})
        # schema.update({'ILRI_actyusageconditions': [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actycitation': [toolkit.get_validator('ignore_missing'),
                                             toolkit.get_converter('convert_to_extras')]})
        schema.update({'ILRI_actycitationacknowledge': [toolkit.get_validator('ignore_missing'),
                                                        toolkit.get_converter('convert_to_extras')]})

        return schema

    def create_package_schema(self):
        schema = super(IlrimetadataPlugin, self).create_package_schema()
        schema = self._add_custom_metadata_to_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(IlrimetadataPlugin, self).update_package_schema()
        schema = self._add_custom_metadata_to_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(IlrimetadataPlugin, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)

        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))

        # Add our custom_text field to the dataset schema.
        # Basically the value is passes to a series of functions like convert_from_extras then ignore_missing. You can add
        # custom functions to it

        # Project Level metadata
        schema.update({'ILRI_prjtitle': [toolkit.get_converter('convert_from_extras'),
                                         toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjabstract': [toolkit.get_converter('convert_from_extras'),
                                            toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_crpandprogram': [toolkit.get_converter('convert_from_extras'),
                                              toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjwebsite': [toolkit.get_converter('convert_from_extras'),
                                           toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjgrant': [toolkit.get_converter('convert_from_extras'),
                                         toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjdonor': [toolkit.get_converter('convert_from_extras'),
                                         toolkit.get_validator('ignore_missing')]})
        schema.update(
            {'ILRI_prjpi': [toolkit.get_converter('convert_from_extras'), toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjpiemail': [toolkit.get_converter('convert_from_extras'),
                                           toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjstaff': [toolkit.get_converter('convert_from_extras'),
                                         toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjpartners': [toolkit.get_converter('convert_from_extras'),
                                            toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjsdate': [toolkit.get_converter('convert_from_extras'),
                                         toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjedate': [toolkit.get_converter('convert_from_extras'),
                                         toolkit.get_validator('ignore_missing')]})

        schema.update({'ILRI_prjregions': [toolkit.get_converter('convert_from_extras'),
                                           toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjcountries': [toolkit.get_converter('convert_from_extras'),
                                             toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_prjspecies': [toolkit.get_converter('convert_from_extras'),
                                           toolkit.get_validator('ignore_missing')]})

        # Project vocabularies
        schema.update({'ILRI_prjsubjects': [toolkit.get_converter('convert_from_tags')("ILRI_vocsubjects"),
                                            toolkit.get_validator('ignore_missing')]})

        # Study Level metadata
        schema.update({'ILRI_actytitle': [toolkit.get_converter('convert_from_extras'),
                                          toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actyabstract': [toolkit.get_converter('convert_from_extras'),
                                             toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actyotheruse': [toolkit.get_converter('convert_from_extras'),
                                             toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actycontactperson': [toolkit.get_converter('convert_from_extras'),
                                                  toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actycontactemail': [toolkit.get_converter('convert_from_extras'),
                                                 toolkit.get_validator('ignore_missing')]})

        schema.update({'ILRI_actycustodian': [toolkit.get_converter('convert_from_extras'),
                                              toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actycustodianemail': [toolkit.get_converter('convert_from_extras'),
                                                   toolkit.get_validator('ignore_missing')]})

        schema.update({'ILRI_actypi': [toolkit.get_converter('convert_from_extras'),
                                       toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actypiemail': [toolkit.get_converter('convert_from_extras'),
                                            toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actystaff': [toolkit.get_converter('convert_from_extras'),
                                          toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actypartners': [toolkit.get_converter('convert_from_extras'),
                                             toolkit.get_validator('ignore_missing')]})

        # Study Vocabularies
        schema.update({'ILRI_actyregions': [toolkit.get_converter('convert_from_tags')("ILRI_vocregions"),
                                            toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actycountries': [toolkit.get_converter('convert_from_tags')("ILRI_voccountries"),
                                              toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actyspecies': [toolkit.get_converter('convert_from_tags')("ILRI_vocspecies"),
                                            toolkit.get_validator('ignore_missing')]})

        schema.update({'ILRI_actyproduct': [toolkit.get_converter('convert_from_tags')("ILRI_vocproduct"),
                                        toolkit.get_validator('ignore_missing')]})

        schema.update({'ILRI_actyprojection': [toolkit.get_converter('convert_from_extras'),
                                                  toolkit.get_validator('ignore_missing')]})

        schema.update({'ILRI_actyresolution': [toolkit.get_converter('convert_from_extras'),
                                               toolkit.get_validator('ignore_missing')]})

        schema.update({'ILRI_actynatlevel': [toolkit.get_converter('convert_from_extras'),
                                             toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actymapextent': [toolkit.get_converter('convert_from_extras'),
                                              toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actymapzoom': [toolkit.get_converter('convert_from_extras'),
                                            toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actyboundbox': [toolkit.get_converter('convert_from_extras'),
                                             toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actyboundboxcenter': [toolkit.get_converter('convert_from_extras'),
                                                   toolkit.get_validator('ignore_missing')]})

        schema.update({'ILRI_actydatecollected': [toolkit.get_converter('convert_from_extras'),
                                                  toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actydatecollectedend': [toolkit.get_converter('convert_from_extras'),
                                                     toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actydatavailable': [toolkit.get_converter('convert_from_extras'),
                                                 toolkit.get_validator('ignore_missing')]})

        schema.update({'ILRI_actyrelconfdata': [toolkit.get_converter('convert_from_extras'),
                                                toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actyfarmconsent': [toolkit.get_converter('convert_from_extras'),
                                                toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actyipownership': [toolkit.get_converter('convert_from_extras'),
                                                toolkit.get_validator('ignore_missing')]})

        # schema.update({'ILRI_actydataowner': [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]})
        # schema.update({'ILRI_actysharingagreement': [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]})
        # schema.update({'ILRI_actyconfideclaration': [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]})
        # schema.update({'ILRI_actyusageconditions': [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actycitation': [toolkit.get_converter('convert_from_extras'),
                                             toolkit.get_validator('ignore_missing')]})
        schema.update({'ILRI_actycitationacknowledge': [toolkit.get_converter('convert_from_extras'),
                                                        toolkit.get_validator('ignore_missing')]})

        return schema



    # The following functions are implemented to satistfy the odkinterface but they don't need changes
    def new_template(self):
        IlrimetadataPlugin.num_times_new_template_called += 1
        return super(IlrimetadataPlugin, self).new_template()

    def read_template(self):
        IlrimetadataPlugin.num_times_read_template_called += 1
        return super(IlrimetadataPlugin, self).read_template()

    def edit_template(self):
        IlrimetadataPlugin.num_times_edit_template_called += 1
        return super(IlrimetadataPlugin, self).edit_template()

    def search_template(self):
        IlrimetadataPlugin.num_times_search_template_called += 1
        return super(IlrimetadataPlugin, self).search_template()

    def history_template(self):
        IlrimetadataPlugin.num_times_history_template_called += 1
        return super(IlrimetadataPlugin, self).history_template()

    def package_form(self):
        IlrimetadataPlugin.num_times_package_form_called += 1
        return super(IlrimetadataPlugin, self).package_form()

    # check_data_dict() is deprecated, this method is only here to test that
    # legacy support for the deprecated method works.
    def check_data_dict(self, data_dict, schema=None):
        IlrimetadataPlugin.num_times_check_data_dict_called += 1

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []