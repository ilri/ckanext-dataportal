from .connection import getSession,closeSession
from .dbmodels import adminUsersModel
from .dbmodels import userModel, userdatasetModel, useresourceModel, authgroupModel, usergroupModel, \
    groupdatasetModel, groupresourceModel, tokenrequestModel, tokenModel, datasetokenModel, resourcetokenModel
from sqlalchemy import or_

from sqlalchemy.exc import IntegrityError
import uuid

def userCanAddUsers(userID):
    dbSession = getSession()
    result = dbSession.query(adminUsersModel).filter(adminUsersModel.ckan_user == userID).filter(adminUsersModel.can_adduser == 1).first()
    if result is None:
        closeSession(dbSession)
        return False
    else:
        closeSession(dbSession)
        return True

def userCanManageResources(userID):
    dbSession = getSession()
    result = dbSession.query(adminUsersModel).filter(adminUsersModel.ckan_user == userID).filter(or_(adminUsersModel.can_addresusers == 1,
                                                                                                        adminUsersModel.can_addresgroups==1,
                                                                                                        adminUsersModel.can_addrestokens==1)).first()
    if result is None:
        closeSession(dbSession)
        return False
    else:
        closeSession(dbSession)
        return True

def userResourceAccess(userID,accessID):
    dbSession = getSession()

    if accessID == 1:
        result = dbSession.query(adminUsersModel).filter(adminUsersModel.ckan_user == userID).filter(adminUsersModel.can_addresusers == 1).first()

    if accessID == 2:
        result = dbSession.query(adminUsersModel).filter(adminUsersModel.ckan_user == userID).filter(adminUsersModel.can_addresgroups == 1).first()

    if accessID == 3:
        result = dbSession.query(adminUsersModel).filter(adminUsersModel.ckan_user == userID).filter(adminUsersModel.can_addrestokens == 1).first()

    if result is None:
        closeSession(dbSession)
        return False
    else:
        closeSession(dbSession)
        return True

def isResourceAdmin(userID):
    dbSession = getSession()
    result = dbSession.query(adminUsersModel).filter(adminUsersModel.ckan_user == userID).filter(adminUsersModel.is_resAdmin == 1).first()
    if result is None:
        closeSession(dbSession)
        return False
    else:
        closeSession(dbSession)
        return True


#--------------------------------------Functions that control the management of users --------------------------------

def getUsers():
    dbSession = getSession()
    users = dbSession.query(userModel).order_by(userModel.user_name).all()
    userDetails = []
    for user in users:
        userDetails.append({"id":user.user_id,"name":user.user_name,"email":user.user_email,"org":user.user_org,"active":user.user_active,"date_added":user.date_added,"added_by":user.added_by})
    closeSession(dbSession)
    return userDetails

def getUserData(userID):
    dbSession = getSession()
    userData = dbSession.query(userModel).filter(userModel.user_id == userID).first()
    if userData is not None:
        resData = {"id":userData.user_id,"name":userData.user_name,"email":userData.user_email,"org":userData.user_org,"active":userData.user_active}
        closeSession(dbSession)
        return True,resData
    else:
        closeSession(dbSession)
        return False,{}


def userExists(userID):
    dbSession = getSession()
    users = dbSession.query(userModel).filter(userModel.user_id == userID).first()
    if users is None:
        closeSession(dbSession)
        return False
    else:
        closeSession(dbSession)
        return True

def addUser(userData,added_by):
    dbSession = getSession()
    newUser = userModel(userData["id"],userData["name"],userData["pass1"],userData["email"],userData["org"],added_by)
    try:
        #DBSession.begin()
        dbSession.add(newUser)        
        closeSession(dbSession)
        return True,""
    except Exception, e:        
        closeSession(dbSession)
        return False,str(e)

def getUserPassword(userID):
    res = "!!NOTFOUND"
    dbSession = getSession()
    user = dbSession.query(userModel).filter(userModel.user_id == userID).first()
    if not user is None:
        res = user.user_password
    closeSession(dbSession)
    return res

def updateUserPassword(userID,newPassword):
    dbSession = getSession()
    try:
        #DBSession.begin()
        dbSession.query(userModel).filter_by(user_id = userID).update({"user_password": newPassword})        
        closeSession(dbSession)
        return True, ""
    except Exception, e:        
        closeSession(dbSession)
        return False, str(e)

def updateUserData(userID,data):
    dbSession = getSession()
    try:
        ##DBSession.begin()
        dbSession.query(userModel).filter_by(user_id = userID).update({"user_name": data["name"],"user_email": data["email"],
                                                                  "user_org": data["org"],"user_active":data["active"]})
        closeSession(dbSession)
        return True, ""
    except Exception, e:        
        closeSession(dbSession)
        return False, str(e)

def deleteUser(userID):
    dbSession = getSession()
    try:
        #DBSession.begin()
        dbSession.query(userModel).filter_by(user_id = userID).delete()
        closeSession(dbSession)
        return True, ""
    except Exception, e:
        closeSession(dbSession)
        return False, str(e)


def addDataSetToUser(userID,datasetID,grantedBy):
    dbSession = getSession()
    newDataset = userdatasetModel(datasetID,userID,grantedBy)
    try:
        #DBSession.begin()
        dbSession.add(newDataset)        
        closeSession(dbSession)
        return True,""
    except IntegrityError as e:        
        closeSession(dbSession)
        return False,str(e.message)

def removeDataSetFromUser(userID,datasetID):
    dbSession = getSession()
    try:
        #DBSession.begin()
        dbSession.query(userdatasetModel).filter_by(user_id = userID).filter_by(dataset_id = datasetID).delete()        
        closeSession(dbSession)
        return True, ""
    except Exception, e:        
        closeSession(dbSession)
        return False, str(e)

def getDatasetsFromUser(userID,ckanToolkit):
    dbSession = getSession()
    datasets = dbSession.query(userdatasetModel).filter(userdatasetModel.user_id == userID).order_by(userdatasetModel.grant_date).all()
    datasetDetails = []
    for dataset in datasets:
        try:
            datasetInfo = ckanToolkit.get_action('package_show')({}, {'id': dataset.dataset_id})
            datsetName = datasetInfo["title"]
        except:
            datsetName = ""
        datasetDetails.append({"dataset_id":dataset.dataset_id,"grant_date":dataset.grant_date,"grant_by":dataset.grant_by,"dataset_name":datsetName})
    closeSession(dbSession)
    return datasetDetails

def addResourceToUser(userID,datasetID,resourceID,grantedBy):
    dbSession = getSession()
    newResource = useresourceModel(datasetID,resourceID,userID,grantedBy)
    try:
        #DBSession.begin()
        dbSession.add(newResource)        
        closeSession(dbSession)
        return True,""
    except IntegrityError as e:
        closeSession(dbSession)
        return False,str(e.message)

def removeResourceFromUser(userID,resourceID):
    #Only the resource ID is needed as it is a UUID4 Id
    dbSession = getSession()
    try:
        #DBSession.begin()
        dbSession.query(useresourceModel).filter_by(user_id = userID).filter_by(resource_id = resourceID).delete()
        closeSession(dbSession)
        return True, ""
    except Exception, e:
        closeSession(dbSession)
        return False, str(e)

def getResourcesFromUser(userID,ckanToolkit):
    dbSession = getSession()
    resources = dbSession.query(useresourceModel).filter(useresourceModel.user_id == userID).order_by(useresourceModel.grant_date).all()
    resourceDetails = []
    for resource in resources:
        try:
            datasetInfo = ckanToolkit.get_action('package_show')({}, {'id': resource.dataset_id})
            datasetName = datasetInfo["title"]
        except:
            datasetName = ""

        try:
            resourceInfo = ckanToolkit.get_action('resource_show')({}, {'id': resource.resource_id})
            resourceName = resourceInfo["name"]
        except:
            resourceName = ""


        resourceDetails.append({"dataset_id":resource.dataset_id,"dataset_name":datasetName,"resource_id":resource.resource_id,"resource_name":resourceName,"grant_date":resource.grant_date,"grant_by":resource.grant_by})
    closeSession(dbSession)
    return resourceDetails

#------------------------------Functions that control the management of groups------------------------------------------

def getGroups():
    dbSession = getSession()
    groups = dbSession.query(authgroupModel).order_by(authgroupModel.group_name).all()
    groupDetails = []
    for group in groups:
        groupDetails.append({"id":group.group_id,"name":group.group_name,"date_added":group.date_added,"added_by":group.added_by})
    closeSession(dbSession)
    return groupDetails

def addGroup(groupData,added_by):
    dbSession = getSession()
    newUser = authgroupModel(groupData["name"],added_by)
    try:
        dbSession.add(newUser)
        closeSession(dbSession)
        return True,""
    except Exception, e:
        closeSession(dbSession)
        return False,str(e)

def updateGroupData(groupID,data):
    dbSession = getSession()
    try:
        dbSession.query(authgroupModel).filter_by(group_id = groupID).update({"group_name": data["name"]})
        closeSession(dbSession)
        return True, ""
    except Exception, e:
        closeSession(dbSession)
        return False, str(e)

def deleteGroup(groupID):
    dbSession = getSession()
    try:
        dbSession.query(authgroupModel).filter_by(group_id = groupID).delete()
        closeSession(dbSession)
        return True, ""
    except Exception, e:
        closeSession(dbSession)
        return False, str(e)

def getGroupData(groupID):
    dbSession = getSession()
    groupData = dbSession.query(authgroupModel).filter(authgroupModel.group_id == groupID).first()
    if groupData is not None:
        resData = {"id":groupData.group_id,"name":groupData.group_name}
        closeSession(dbSession)
        return True,resData
    else:
        closeSession(dbSession)
        return False,{}

def getGroupMembers(groupID):
    dbSession = getSession()

    sql = "SELECT user.user_id,user.user_name,usergroup.join_date,usergroup.joined_by " \
          "FROM user,usergroup " \
          "WHERE usergroup.user_id = user.user_id AND usergroup.group_id = '" + groupID + "' ORDER BY usergroup.join_date"

    results = dbSession.execute(sql)

    groupMembers = []
    for result in results:
        groupMembers.append({"user_id":result[0],"user_name":result[1],"join_date":result[2],"joined_by":result[3]})    
    closeSession(dbSession)
    return groupMembers


def addUserToGroup(groupId,userId,joinedBy):
    dbSession = getSession()
    newUser = usergroupModel(userId,groupId,joinedBy)
    try:
        dbSession.add(newUser)
        closeSession(dbSession)
        return True,""
    except Exception, e:
        closeSession(dbSession)
        return False,str(e)

def removeUserFromGroup(groupID,userId):
    dbSession = getSession()
    try:
        dbSession.query(usergroupModel).filter_by(group_id = groupID).filter_by(user_id = userId).delete()
        closeSession(dbSession)
        return True, ""
    except Exception, e:
        closeSession(dbSession)
        return False, str(e)

def addDataSetToGroup(groupID,datasetID,grantedBy):
    dbSession = getSession()
    newDataset = groupdatasetModel(datasetID,groupID,grantedBy)
    try:
        dbSession.add(newDataset)
        closeSession(dbSession)
        return True,""
    except IntegrityError as e:
        closeSession(dbSession)
        return False,str(e.message)

def removeDataSetFromGroup(groupID,datasetID):
    dbSession = getSession()
    try:
        dbSession.query(groupdatasetModel).filter_by(group_id = groupID).filter_by(dataset_id = datasetID).delete()
        
        closeSession(dbSession)
        return True, ""
    except Exception, e:
        
        closeSession(dbSession)
        return False, str(e)

def addResourceToGroup(groupID,datasetID,resourceID,grantedBy):
    dbSession = getSession()
    newResource = groupresourceModel(datasetID,resourceID,groupID,grantedBy)
    try:
        dbSession.add(newResource)
        
        closeSession(dbSession)
        return True,""
    except IntegrityError as e:
        
        closeSession(dbSession)
        return False,str(e.message)

def removeResourceFromGroup(groupID,resourceID):
    #Only the resource ID is needed as it is a UUID4 Id
    dbSession = getSession()
    try:
        dbSession.query(groupresourceModel).filter_by(group_id = groupID).filter_by(resource_id = resourceID).delete()
        
        closeSession(dbSession)
        return True, ""
    except Exception, e:
        
        closeSession(dbSession)
        return False, str(e)

def getDatasetsFromGroup(groupID,ckanToolkit):
    dbSession = getSession()
    datasets = dbSession.query(groupdatasetModel).filter(groupdatasetModel.group_id == groupID).order_by(groupdatasetModel.grant_date).all()
    datasetDetails = []
    for dataset in datasets:
        try:
            datasetInfo = ckanToolkit.get_action('package_show')({}, {'id': dataset.dataset_id})
            datsetName = datasetInfo["title"]
        except:
            datsetName = ""
        datasetDetails.append({"dataset_id":dataset.dataset_id,"grant_date":dataset.grant_date,"grant_by":dataset.grant_by,"dataset_name":datsetName})
    closeSession(dbSession)
    return datasetDetails

def getResourcesFromGroup(groupID,ckanToolkit):
    dbSession = getSession()
    resources = dbSession.query(groupresourceModel).filter(groupresourceModel.group_id == groupID).order_by(groupresourceModel.grant_date).all()
    resourceDetails = []
    for resource in resources:
        try:
            datasetInfo = ckanToolkit.get_action('package_show')({}, {'id': resource.dataset_id})
            datasetName = datasetInfo["title"]
        except:
            datasetName = ""

        try:
            resourceInfo = ckanToolkit.get_action('resource_show')({}, {'id': resource.resource_id})
            resourceName = resourceInfo["name"]
        except:
            resourceName = ""


        resourceDetails.append({"dataset_id":resource.dataset_id,"dataset_name":datasetName,"resource_id":resource.resource_id,"resource_name":resourceName,"grant_date":resource.grant_date,"grant_by":resource.grant_by})
    closeSession(dbSession)
    return resourceDetails

#------------------------------ Functions that control the tokens ------------------------

def getTokenRequests(ckanToolkit):
    dbSession = getSession()
    requests = dbSession.query(tokenrequestModel).order_by(tokenrequestModel.request_date).all()
    requestDetails = []
    for request in requests:

        try:
            datasetInfo = ckanToolkit.get_action('package_show')({}, {'id': request.dataset_id})
            datasetName = datasetInfo["title"]
        except:
            datasetName = ""

        try:
            resourceInfo = ckanToolkit.get_action('resource_show')({}, {'id': request.resource_id})
            resourceName = resourceInfo["name"]
        except:
            resourceName = ""

        requestDetails.append({"request_id":request.request_id,"request_date":request.request_date,"datasetName":datasetName,"resourceName":resourceName,"user_name":request.user_name,"user_email":request.user_email,"user_org":request.user_org,"user_country":request.user_country,"token_given":request.token_given})
    closeSession(dbSession)
    return requestDetails

def deleteToken(tokenID):
    dbSession = getSession()
    try:
        dbSession.query(tokenrequestModel).filter_by(token_given = tokenID).update({"token_given": None})
        
    except Exception, e:
        
        closeSession(dbSession)
        return False, str(e)

    try:
        dbSession.query(tokenModel).filter_by(token_id = tokenID).delete()
        
    except:
        
        try:
            dbSession.query(tokenModel).filter_by(token_id = tokenID).update({"token_active": 0})
            
        except Exception, e:
            
            closeSession(dbSession)
            return False, str(e)

    closeSession(dbSession)
    return True,""

def createToken(added_by):
    dbSession = getSession()
    tokenID = uuid.uuid4()
    newToken = tokenModel(tokenID,added_by)
    try:
        dbSession.add(newToken)
        
        closeSession(dbSession)
        return True,tokenID
    except Exception, e:
        
        closeSession(dbSession)
        return False,str(e)

def setTokenToRequest(requestID,tokenID):
    dbSession = getSession()
    try:
        dbSession.query(tokenrequestModel).filter_by(request_id = requestID).update({"token_given": tokenID})
        
    except Exception, e:
        
        closeSession(dbSession)
        return False, str(e)

    closeSession(dbSession)
    return True,""

def getTokenData(tokenID):
    dbSession = getSession()
    tokenData = dbSession.query(tokenModel).filter_by(token_id = tokenID).filter_by(token_active = 1).first()
    if tokenData is not None:
        resData = {"id":tokenData.token_id,"token_givendate":tokenData.token_givendate,"token_givenby":tokenData.token_givenby}
        closeSession(dbSession)
        return True,resData
    else:
        closeSession(dbSession)
        return False,{}

def getDatasetsFromToken(tokenID,ckanToolkit):
    dbSession = getSession()
    datasets = dbSession.query(datasetokenModel).filter_by(token_id = tokenID).order_by(datasetokenModel.grant_date).all()
    datasetDetails = []
    for dataset in datasets:
        try:
            datasetInfo = ckanToolkit.get_action('package_show')({}, {'id': dataset.dataset_id})
            datsetName = datasetInfo["title"]
        except:
            datsetName = ""
        datasetDetails.append({"dataset_id":dataset.dataset_id,"grant_date":dataset.grant_date,"grant_by":dataset.grant_by,"dataset_name":datsetName})
    closeSession(dbSession)
    return datasetDetails

def getResourcesFromToken(tokenID,ckanToolkit):
    dbSession = getSession()
    resources = dbSession.query(resourcetokenModel).filter_by(token_id = tokenID).order_by(resourcetokenModel.grant_date).all()
    resourceDetails = []
    for resource in resources:
        try:
            datasetInfo = ckanToolkit.get_action('package_show')({}, {'id': resource.dataset_id})
            datasetName = datasetInfo["title"]
        except:
            datasetName = ""

        try:
            resourceInfo = ckanToolkit.get_action('resource_show')({}, {'id': resource.resource_id})
            resourceName = resourceInfo["name"]
        except:
            resourceName = ""


        resourceDetails.append({"dataset_id":resource.dataset_id,"dataset_name":datasetName,"resource_id":resource.resource_id,"resource_name":resourceName,"grant_date":resource.grant_date,"grant_by":resource.grant_by})
    closeSession(dbSession)
    return resourceDetails

def addDataSetToToken(tokenID,datasetID,grantedBy):
    dbSession = getSession()
    newDataset = datasetokenModel(datasetID,tokenID,grantedBy)
    try:
        dbSession.add(newDataset)
        
        closeSession(dbSession)
        return True,""
    except IntegrityError as e:
        
        closeSession(dbSession)
        return False,str(e.message)

def removeDataSetFromToken(tokenID,datasetID):
    dbSession = getSession()
    try:
        dbSession.query(datasetokenModel).filter_by(token_id = tokenID).filter_by(dataset_id = datasetID).delete()
        
        closeSession(dbSession)
        return True, ""
    except Exception, e:
        
        closeSession(dbSession)
        return False, str(e)

def addResourceToToken(tokenID,datasetID,resourceID,grantedBy):
    dbSession = getSession()
    newResource = resourcetokenModel(datasetID,resourceID,tokenID,grantedBy)
    try:
        dbSession.add(newResource)
        
        closeSession(dbSession)
        return True,""
    except IntegrityError as e:
        
        closeSession(dbSession)
        return False,str(e.message)

def removeResourceFromToken(tokenID,resourceID):
    #Only the resource ID is needed as it is a UUID4 Id
    dbSession = getSession()
    try:
        dbSession.query(resourcetokenModel).filter_by(token_id = tokenID).filter_by(resource_id = resourceID).delete()
        
        closeSession(dbSession)
        return True, ""
    except Exception, e:
        
        closeSession(dbSession)
        return False, str(e)

def getRequestData(requestID,ckanToolkit):
    dbSession = getSession()
    requestData = dbSession.query(tokenrequestModel).filter_by(request_id = requestID).first()
    if requestData is not None:

        try:
            datasetInfo = ckanToolkit.get_action('package_show')({}, {'id': requestData.dataset_id})
            datasetName = datasetInfo["title"]
        except:
            datasetName = ""

        try:
            resourceInfo = ckanToolkit.get_action('resource_show')({}, {'id': requestData.resource_id})
            resourceName = resourceInfo["name"]
        except:
            resourceName = ""

        resData = {"request_id":requestData.request_id,"request_date":requestData.request_date,"request_ip":requestData.request_ip,"datasetName":datasetName,"resourceName":resourceName,"user_name":requestData.user_name,"user_email":requestData.user_email,"user_org":requestData.user_org,"user_orgtype":requestData.user_orgtype,"user_country":requestData.user_country,"user_datausage":requestData.user_datausage,"user_otherdata":requestData.user_otherdata,"user_hearfrom":requestData.user_hearfrom,"token_given":requestData.token_given}
        closeSession(dbSession)
        return True,resData
    else:
        closeSession(dbSession)
        return False,{}