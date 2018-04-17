import ckan.plugins.toolkit as toolkit
from ckan.common import c
from .dbfunctions import userCanAddUsers
from .dbfunctions import getUsers, userExists, addUser, updateUserPassword, \
    updateUserData, deleteUser, getUserData, userResourceAccess ,addDataSetToUser, \
    getDatasetsFromUser, removeDataSetFromUser, addResourceToUser, getResourcesFromUser, removeResourceFromUser, \
    getGroups, addGroup, updateGroupData, deleteGroup, getGroupData, getGroupMembers, addUserToGroup, removeUserFromGroup, addDataSetToGroup, removeDataSetFromGroup, \
    addResourceToGroup, removeResourceFromGroup, getDatasetsFromGroup, getResourcesFromGroup, \
    getTokenRequests, deleteToken, createToken, setTokenToRequest, getTokenData, getDatasetsFromToken, \
    getResourcesFromToken, addDataSetToToken, removeDataSetFromToken, addResourceToToken, removeResourceFromToken, \
    getRequestData, getRequestStats
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.lib.helpers as h
from ckan.common import _
from ckan.lib.base import abort

import pprint

tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params


class statisticsController(toolkit.BaseController):
    def display_stats(self):
        data = {}
        errors = {}
        vars = {'data': data, 'errors': errors}
        return toolkit.render('ilriuser/stats.html',extra_vars=vars)

    def request_stats(self):
        toolkit.response.content_type = 'application/json'
        toolkit.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        if toolkit.request.method == 'POST':
            postdata = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(toolkit.request.POST))))
            draw = int(postdata['draw'])
            fields = []
            start = 0
            length = 0
            orderIndex = 0
            orderDirection = ''
            searchValue = ""
            for key in postdata.keys():
                if key.find("columns[") >= 0 and key.find("[data]") >= 0:
                    fields.append(postdata[key])
                if key == "start":
                    start = int(postdata[key])
                if key == "length":
                    length = int(postdata[key])
                if key.find("order[") >= 0 and key.find("[column]") >= 0:
                    orderIndex = int(postdata[key])
                if key.find("order[") >= 0 and key.find("[dir]") >= 0:
                    orderDirection = postdata[key]
                if key.find("search[") == 0 and key.find("[value]") >= 0:
                    searchValue = postdata[key]
            result = getRequestStats(draw, fields, start, length, orderIndex,orderDirection, searchValue)
            return result

        else:
            abort(404, 'Page not found')


class addNewUserController(toolkit.BaseController):
    def display_addNewUser(self):

        #If the user cannot add new users then redirect to home
        if userCanAddUsers(c.user) == False:
            toolkit.redirect_to(controller='home', action='index')

        data = {}
        errors = {}
        vars = {'data': data, 'errors': errors}
        return toolkit.render('ilriuser/new.html',extra_vars=vars)

class resourceAuthController(toolkit.BaseController):
    def manageUsers(self):
        if userResourceAccess(c.user,1) == False:
            abort(404, 'Page not found')

        data = {}
        errors = {}
        return_action = ""
        if toolkit.request.method == 'POST':
            formdata = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(toolkit.request.POST))))
            if "addUser" in formdata.keys():
                data["id"] = formdata['id']
                data["name"] = formdata['name']
                data["email"] = formdata['email']
                data["org"] = formdata['org']
                data["pass1"] = formdata['pass1']
                data["pass2"] = formdata['pass2']
                if userExists(formdata['id']) == False:
                    added,message = addUser(data,c.userobj.name)
                    if not added:
                        return_action = "addUser"
                        errors["DBError"] = message
                    else:
                        h.flash_success(_("User added successfully"))
                else:
                    return_action = "addUser"
                    errors["userExists"] = "The user already exists"
            if "updateUser" in formdata.keys():
                data["id"] = formdata['id']
                data["name"] = formdata['name']
                data["email"] = formdata['email']
                data["org"] = formdata['org']
                data["pass1"] = formdata['pass1']
                data["pass2"] = formdata['pass2']

                data["active"] = toolkit.request.POST.get('active', '')

                if data["active"] == "on":
                    data["active"] = 1
                else:
                    data["active"] = 0

                if data["pass1"] != "" and data["pass2"] != "":
                    if data["pass1"] == data["pass2"]:
                        updated,message = updateUserPassword(data["id"],data["pass1"])
                        if updated:
                            updated,message = updateUserData(data["id"],data)
                            if updated:
                                h.flash_success(_("User successfully updated"))
                            else:
                                return_action = "updateUser"
                                errors["DBError"] = message
                        else:
                            return_action = "updateUser"
                            errors["DBError"] = message
                    else:
                        return_action = "updateUser"
                        errors["OldPassError"] = "The new password and the confirmation are not the same"
                else:
                    updated,message = updateUserData(data["id"],data)
                    if updated:
                        h.flash_success(_("User successfully updated"))
                    else:
                        return_action = "updateUser"
                        errors["DBError"] = message
            if "deleteUser" in formdata.keys():
                data["id"] = formdata['id']
                deleted,message = deleteUser(data["id"])
                if deleted:
                    h.flash_success(_("User successfully deleted"))
                else:
                    if message.index("foreign key") > 0:
                        h.flash_error("This user has linked information to it and cannot be deleted. You can deactivate it though")
                    else:
                        h.flash_error(message)

        vars = {'data': data, 'error_summary': errors,'action_type':'manageUsers','users':getUsers(),'return_action':return_action,'action_group':'users'}
        return toolkit.render('ilriuser/resource_edit.html',extra_vars=vars)


    def manageOneUser(self,userID):
        if userResourceAccess(c.user,1) == False:
            abort(404, 'Page not found')
        data = {}
        errors = {}
        datasetArray = []
        resourceArray = []

        exists,userData = getUserData(userID)
        if exists == False:
            abort(404, 'User not found')
        else:
            datasets = toolkit.get_action('package_list')({}, {})
            for dataset in datasets:
                try:
                    datasetInfo = toolkit.get_action('package_show')({}, {'id': dataset})
                    datasetArray.append({"id":datasetInfo["id"],"title":datasetInfo["title"]})
                    try:
                        for resource in datasetInfo["resources"]:
                            resourceArray.append({"id":datasetInfo["id"],"title":datasetInfo["title"],"resid":resource["id"],"resname":resource["name"]})
                    except:
                        pass
                except:
                    pass

            if toolkit.request.method == 'POST':
                formdata = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(toolkit.request.POST))))
                if "addDataset" in formdata.keys():
                    data["datasetName"] = formdata['datasetName']
                    added,message = addDataSetToUser(userID,data["datasetName"],c.userobj.name)
                    if added:
                        h.flash_success(_("Successfully added the dataset"))
                    else:
                        if message.index("Duplicate") > 0:
                            h.flash_error("This user already has such dataset assigned")
                        else:
                            h.flash_error(message)
                if "removeDataset" in formdata.keys():
                    data["datasetID"] = formdata['datasetID']
                    removed,message = removeDataSetFromUser(userID,data["datasetID"])
                    if removed:
                        h.flash_success(_("Successfully removed the dataset"))
                    else:
                        h.flash_error(message)

                if "addResource" in formdata.keys():
                    resource = formdata['resourceID'].split("|")
                    data["datasetID"] = resource[0]
                    data["resourceID"] = resource[1]
                    added,message = addResourceToUser(userID,data["datasetID"],data["resourceID"],c.userobj.name)
                    if added:
                        h.flash_success(_("Successfully added the resource"))
                    else:
                        if message.index("Duplicate") > 0:
                            h.flash_error("This user already has such resource assigned")
                        else:
                            h.flash_error(message)

                if "removeResource" in formdata.keys():
                    data["datasetID"] = formdata['removeDatasetID']
                    data["resourceID"] = formdata['removeResourceID']

                    removed,message = removeResourceFromUser(userID,data["resourceID"])
                    if removed:
                        h.flash_success(_("Successfully removed the resource"))
                    else:
                        h.flash_error(message)



            userDatasets = getDatasetsFromUser(userID,toolkit);
            userResources = getResourcesFromUser(userID,toolkit)

            vars = {'userDatasets': userDatasets, 'error_summary': errors,'action_type':'manageOneUser','action_group':'users','userData':userData,'datasetArray':datasetArray,'resourceArray':resourceArray,'userResources':userResources}
            return toolkit.render('ilriuser/resource_edit.html',extra_vars=vars)

    def manageGroups(self):
        if userResourceAccess(c.user,2) == False:
            abort(404, 'Page not found')
        data = {}
        errors = {}
        return_action = ""

        if toolkit.request.method == 'POST':
            formdata = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(toolkit.request.POST))))

            if "addGroup" in formdata.keys():
                    data["name"] = formdata['name']
                    added,message = addGroup(data,c.userobj.name)
                    if not added:
                        return_action = "addGroup"
                        errors["DBError"] = message
                    else:
                        h.flash_success(_("Group added successfully"))
            if "updateGroup" in formdata.keys():
                data["id"] = formdata['id']
                data["name"] = formdata['name']
                updated,message = updateGroupData(data["id"],data)
                if updated:
                    h.flash_success(_("Group successfully updated"))
                else:
                    return_action = "updateGroup"
                    errors["DBError"] = message

            if "deleteGroup" in formdata.keys():
                data["id"] = formdata['id']
                deleted,message = deleteGroup(data["id"])
                if deleted:
                    h.flash_success(_("Group successfully deleted"))
                else:
                    if message.index("foreign key") > 0:
                        h.flash_error("This group has linked information to it and cannot be deleted.")
                    else:
                        h.flash_error(message)


        vars = {'data': data, 'error_summary': errors,'action_type':'manageGroups','action_group':'groups','groups':getGroups(),'return_action':return_action}
        return toolkit.render('ilriuser/resource_edit.html',extra_vars=vars)

    def manageGroupMembers(self,groupID):
        if userResourceAccess(c.user,2) == False:
            abort(404, 'Page not found')

        errors = {}
        data = {}

        if toolkit.request.method == 'POST':
            formdata = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(toolkit.request.POST))))

            if "addUser" in formdata.keys():
                data["userID"] = formdata['userID']
                added,message = addUserToGroup(groupID,data["userID"],c.userobj.name)
                if added:
                    h.flash_success(_("User successfully added to the group"))
                else:
                    h.flash_error(message)

            if "removeUser" in formdata.keys():
                data["userID"] = formdata['memberID']
                deleted,message = removeUserFromGroup(groupID,data["userID"])
                if deleted:
                    h.flash_success(_("User successfully removed from the group"))
                else:
                    h.flash_error(message)
                

        exists,groupData = getGroupData(groupID)
        if exists == False:
            abort(404, 'Group not found')
        else:
            members = getGroupMembers(groupID)

        vars = {'groupData':groupData, 'error_summary': errors,'action_type':'manageGroupMembers','action_group':'groups','members':members,'users':getUsers()}
        return toolkit.render('ilriuser/resource_edit.html',extra_vars=vars)


    def manageOneGroup(self,groupID):
        if userResourceAccess(c.user,2) == False:
            abort(404, 'Page not found')
        data = {}
        errors = {}
        datasetArray = []
        resourceArray = []

        exists,groupData = getGroupData(groupID)
        if exists == False:
            abort(404, 'Group not found')
        else:
            datasets = toolkit.get_action('package_list')({}, {})
            for dataset in datasets:
                try:
                    datasetInfo = toolkit.get_action('package_show')({}, {'id': dataset})
                    datasetArray.append({"id":datasetInfo["id"],"title":datasetInfo["title"]})
                    try:
                        for resource in datasetInfo["resources"]:
                            resourceArray.append({"id":datasetInfo["id"],"title":datasetInfo["title"],"resid":resource["id"],"resname":resource["name"]})
                    except:
                        pass
                except:
                    pass

            if toolkit.request.method == 'POST':
                formdata = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(toolkit.request.POST))))
                if "addDataset" in formdata.keys():
                    data["datasetName"] = formdata['datasetName']
                    added,message = addDataSetToGroup(groupID,data["datasetName"],c.userobj.name)
                    if added:
                        h.flash_success(_("Successfully added the dataset"))
                    else:
                        if message.index("Duplicate") > 0:
                            h.flash_error("This group already has such dataset assigned")
                        else:
                            h.flash_error(message)
                if "removeDataset" in formdata.keys():
                    data["datasetID"] = formdata['datasetID']
                    removed,message = removeDataSetFromGroup(groupID,data["datasetID"])
                    if removed:
                        h.flash_success(_("Successfully removed the dataset"))
                    else:
                        h.flash_error(message)

                if "addResource" in formdata.keys():
                    resource = formdata['resourceID'].split("|")
                    data["datasetID"] = resource[0]
                    data["resourceID"] = resource[1]
                    added,message = addResourceToGroup(groupID,data["datasetID"],data["resourceID"],c.userobj.name)
                    if added:
                        h.flash_success(_("Successfully added the resource"))
                    else:
                        if message.index("Duplicate") > 0:
                            h.flash_error("This group already has such resource assigned")
                        else:
                            h.flash_error(message)

                if "removeResource" in formdata.keys():
                    data["datasetID"] = formdata['removeDatasetID']
                    data["resourceID"] = formdata['removeResourceID']

                    removed,message = removeResourceFromGroup(groupID,data["resourceID"])
                    if removed:
                        h.flash_success(_("Successfully removed the resource"))
                    else:
                        h.flash_error(message)



            groupDatasets = getDatasetsFromGroup(groupID,toolkit);
            groupResources = getResourcesFromGroup(groupID,toolkit)

            vars = {'groupDatasets': groupDatasets, 'error_summary': errors,'action_type':'manageOneGroup','action_group':'groups','groupData':groupData,'datasetArray':datasetArray,'resourceArray':resourceArray,'groupResources':groupResources}
            return toolkit.render('ilriuser/resource_edit.html',extra_vars=vars)

    def manageTokens(self):
        if userResourceAccess(c.user,3) == False:
            abort(404, 'Page not found')
        data = {}
        errors = {}

        if toolkit.request.method == 'POST':
            formdata = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(toolkit.request.POST))))
            if "removeToken" in formdata.keys():
                data["tokenID"] = formdata['tokenID']
                print data["tokenID"]
                deleted,message = deleteToken(data["tokenID"])
                if deleted:
                    h.flash_success(_("Successfully removed the token"))
                else:
                     h.flash_error(message)
            if "allocateToken" in formdata.keys():
                data["requestID"] = formdata['requestID']
                added,tokenID = createToken(c.userobj.name)
                if added:
                    updated,message = setTokenToRequest(data["requestID"],tokenID)
                    if updated:
                        h.flash_success(_("Successfully assigned the token. Search for token %s and edit its dataset access") %tokenID)
                    else:
                        h.flash_error(message)
                else:
                    h.flash_error(message)


        requests = getTokenRequests(toolkit)
        vars = {'error_summary': errors,'action_type':'manageRequests','action_group':'tokens','requests':requests}
        return toolkit.render('ilriuser/resource_edit.html',extra_vars=vars)

    def manageOneToken(self,tokenID):
        if userResourceAccess(c.user,3) == False:
            abort(404, 'Page not found')

        errors = {}
        datasetArray = []
        resourceArray = []
        data = {}

        exists,tokenData = getTokenData(tokenID)
        if exists == False:
            abort(404, 'Token not found')
        else:

            datasets = toolkit.get_action('package_list')({}, {})
            for dataset in datasets:
                try:
                    datasetInfo = toolkit.get_action('package_show')({}, {'id': dataset})
                    datasetArray.append({"id":datasetInfo["id"],"title":datasetInfo["title"]})
                    try:
                        for resource in datasetInfo["resources"]:
                            resourceArray.append({"id":datasetInfo["id"],"title":datasetInfo["title"],"resid":resource["id"],"resname":resource["name"]})
                    except:
                        pass
                except:
                    pass

            if toolkit.request.method == 'POST':
                formdata = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(toolkit.request.POST))))
                if "addDataset" in formdata.keys():
                    data["datasetName"] = formdata['datasetName']
                    added,message = addDataSetToToken(tokenID,data["datasetName"],c.userobj.name)
                    if added:
                        h.flash_success(_("Successfully added the dataset"))
                    else:
                        if message.index("Duplicate") > 0:
                            h.flash_error("This token already has such dataset assigned")
                        else:
                            h.flash_error(message)
                if "removeDataset" in formdata.keys():
                    data["datasetID"] = formdata['datasetID']
                    removed,message = removeDataSetFromToken(tokenID,data["datasetID"])
                    if removed:
                        h.flash_success(_("Successfully removed the dataset"))
                    else:
                        h.flash_error(message)

                if "addResource" in formdata.keys():
                    resource = formdata['resourceID'].split("|")
                    data["datasetID"] = resource[0]
                    data["resourceID"] = resource[1]
                    added,message = addResourceToToken(tokenID,data["datasetID"],data["resourceID"],c.userobj.name)
                    if added:
                        h.flash_success(_("Successfully added the resource"))
                    else:
                        if message.index("Duplicate") > 0:
                            h.flash_error("This group already has such resource assigned")
                        else:
                            h.flash_error(message)

                if "removeResource" in formdata.keys():
                    data["datasetID"] = formdata['removeDatasetID']
                    data["resourceID"] = formdata['removeResourceID']

                    removed,message = removeResourceFromToken(tokenID,data["resourceID"])
                    if removed:
                        h.flash_success(_("Successfully removed the resource"))
                    else:
                        h.flash_error(message)

            tokenDatasets = getDatasetsFromToken(tokenID,toolkit);
            tokenResources = getResourcesFromToken(tokenID,toolkit)

            vars = {'error_summary': errors,'action_type':'manageOneToken','action_group':'tokens','tokenData':tokenData,'datasetArray':datasetArray,'resourceArray':resourceArray,'tokenDatasets':tokenDatasets,'tokenResources':tokenResources}
            return toolkit.render('ilriuser/resource_edit.html',extra_vars=vars)

    def showRequestDetails(self,requestID):
        if userResourceAccess(c.user,3) == False:
            abort(404, 'Page not found')

        errors = {}
        exists,requestData = getRequestData(requestID,toolkit)
        if exists == False:
            abort(404, 'Request not found')
        else:
            vars = {'error_summary': errors,'action_type':'showRequestDetails','action_group':'tokens','requestData':requestData}

            return toolkit.render('ilriuser/resource_edit.html',extra_vars=vars)