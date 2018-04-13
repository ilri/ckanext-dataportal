import pprint

from .dbmodels import userModel
from .dbmodels import resourcestatsModel
from .dbmodels import tokenrequestModel
from .dbmodels import datasetokenModel
from .dbmodels import resourcetokenModel
from .dbmodels import useresourceModel
from .dbmodels import userdatasetModel
from .dbmodels import usergroupModel
from .dbmodels import groupresourceModel
from .dbmodels import groupdatasetModel
from .dbmodels import tokenModel
from .connection import getSession,closeSession

import datetime

from pylons import config
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import Utils
from ckan.common import _
from time import time
import logging

import ckan.plugins.toolkit as toolkit

def add_msg_niceties(recipient_name, body, sender_name, sender_url):
    return _(u"Dear %s,") % recipient_name \
           + u"\r\n\r\n%s\r\n\r\n" % body \
           + u"--\r\n%s (%s)" % (sender_name, sender_url)

def sendTokenRequestMail(body,targetName,targetEmail):
    print "Sending email!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    targetEmail = "cquiros@qlands.com"
    mail_from = config.get('smtp.mail_from')
    body = add_msg_niceties(targetName, body, "ILRI Datasets Portal", "http://data.ilri.org/portal")
    msg = MIMEText(body.encode('utf-8'), 'plain', 'utf-8')
    ssubject = "New token request for confidential data"
    subject = Header(ssubject.encode('utf-8'), 'utf-8')
    msg['Subject'] = subject
    msg['From'] = _("%s <%s>") % ("CKAN Portal", mail_from)
    recipient = u"%s <%s>" % (targetName, targetEmail)
    msg['To'] = Header(recipient, 'utf-8')
    msg['Date'] = Utils.formatdate(time())

    try:
        smtp_connection = smtplib.SMTP()
        smtp_server = config.get('smtp.server', 'localhost')
        smtp_user = config.get('smtp.user')
        smtp_password = config.get('smtp.password')

        smtp_connection.connect(smtp_server)
        smtp_connection.login(smtp_user, smtp_password)
        smtp_connection.sendmail(mail_from, [targetEmail], msg.as_string())
        logging.debug("Token Email sent to " + targetEmail)

    except Exception,e:
        print str(e)
        logging.debug("Token Sendmail error: " + str(e))



def processToken(requestID,ipAddress,datasetID,resourceID,token,format):

    dbSession = getSession()

    #Check if the token is active
    result = dbSession.query(tokenModel).filter_by(token_id = token).filter_by(token_active = 1).first()
    if result is None:
        closeSession(dbSession)
        return False

    #Check if the token has access to the resource
    result = dbSession.query(resourcetokenModel).filter_by(resource_id = resourceID).filter_by(token_id = token).first()
    if result is None:
        #If not then check if the token as access to the dataset of the resource
        result = dbSession.query(datasetokenModel).filter_by(dataset_id = datasetID).filter_by(token_id = token).first()

    if result is None:
        closeSession(dbSession)
        return False
    else:
        #If the token is valid then we add the request to the Book
        try:
            newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,token,None,"","","","","","","")
            dbSession.add(newGuestBookRecord)
            closeSession(dbSession)
        except:
            closeSession(dbSession)
        return True

def processUser(requestID,ipAddress,datasetID,resourceID,user,password,format):
    dbSession = getSession()

    #Check if the user and password are correct and if the user is active
    result = dbSession.query(userModel).filter_by(user_id = user).filter_by(user_password = password).filter_by(user_active = 1).first()
    if result is None:
        closeSession(dbSession)
        return False
    else:
        #Checks if the user has access to the resource
        result = dbSession.query(useresourceModel).filter_by(user_id = user).filter_by(resource_id = resourceID).first()
        if result is None:
            #Check if the user has access to the dataset of the resource
            result = dbSession.query(userdatasetModel).filter_by(user_id = user).filter_by(dataset_id = datasetID).first()
            if result is None:
                #Get all the groups of the user
                groupAccess = False
                for row in dbSession.query(usergroupModel).filter_by(user_id = user).all():
                    #Check if the group has access to the resource
                    result =  dbSession.query(groupresourceModel).filter_by(group_id = row.group_id).filter_by(resource_id = resourceID).first()
                    if result == None:
                        #Check if the group has access to the dataset of the resource
                        result =  dbSession.query(groupdatasetModel).filter_by(group_id = row.group_id).filter_by(dataset_id = datasetID).first()
                        if result != None:
                            groupAccess = True
                            break
                    else:
                        groupAccess = True
                        break
                if groupAccess == True:
                    #If the user is valid then we add the request to the Book
                    try:
                        newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,None,user,"","","","","","","")
                        dbSession.add(newGuestBookRecord)
                        closeSession(dbSession)
                        return True
                    except:
                        closeSession(dbSession)
                        return False
                else:
                    closeSession(dbSession)
                    return False
            else:
                #If the user is valid then we add the request to the Book
                try:
                    newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,None,user,"","","","","","","")
                    dbSession.add(newGuestBookRecord)
                    closeSession(dbSession)
                    return True
                except:
                    closeSession(dbSession)
                    return False
        else:
            #If the user is valid then we add the request to the Book
            try:
                newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,None,user,"","","","","","","")
                dbSession.add(newGuestBookRecord)
                closeSession(dbSession)
                return True
            except:
                closeSession(dbSession)
                return False

def processGuest(requestID,ipAddress,resourceID,data,format):

    errors = {}

    if data["field_name"] == "":
        data["field_name"] = "Left empty"

    if data["field_email"] == "":
        data["field_email"] = "Left empty"

    if data["field_organization"] == "":
        data["field_organization"] = "Left empty"

    if data["field_organizationType"] == "":
        data["field_organizationType"] = "Left empty"

    if data["field_country"] == "":
        data["field_country"] = "Left empty"

    if data["field_notes"] == "":
        data["field_notes"] = "Left empty"

    if data["field_hearfrom"] == "":
        data["field_hearfrom"] = "Left empty"

    if data["field_aggrement"] == 'no':
        errors["Agreement"] = "You need to accept the public license."

    if len(errors) > 0:
        return False,errors
    else:
        dbSession = getSession()
        try:
            #If there are no errors in the data try to add the new Guest Book Record
            newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,None,None,data["field_name"],data["field_email"],data["field_organization"],data["field_organizationType"],data["field_country"],data["field_notes"],data["field_hearfrom"])
            dbSession.add(newGuestBookRecord)
            closeSession(dbSession)
        except Exception,e:
            closeSession(dbSession)
            return False, {'Portal Error':str(e)}

        return True, {}

def processRequestToken(requestID,ipAddress,data,datasetID,resourceID):
    errors = {}

    if data["field_name"] == "":
        errors["Name"] = "Name is required"

    if data["field_email"] == "":
        errors["Email"] = "Email is required."

    if data["field_organization"] == "":
        errors["Organization"] = "Organization is required"

    if data["field_organizationType"] == "Select one":
        errors["Organization Type"] = "Organization Type is required"

    if data["field_country"] == "NA":
        errors["Country"] = "Country is required"

    if data["field_notes"] == "":
        errors["Data usage"] = "Data usage is required"

    if data["field_hearfrom"] == "Select one":
        errors["Hear from"] = "Indicate how you hear about this dataset/resource"

    if data["field_aggrement"] == "no":
        errors["Agreement"] = "You need to accept the Confidentiality Agreement"

    if len(errors) > 0:
        return False,errors
    else:
        dbSession = getSession()
        try:
            #If there are no errors in the data try to add the new token request
            newTokenRequest = tokenrequestModel(requestID,datetime.datetime.now(),ipAddress,datasetID,resourceID,data["field_name"],data["field_email"],data["field_organization"],data["field_organizationType"],data["field_country"],data["field_notes"],data["field_otherdatasets"],data["field_hearfrom"])

            dbSession.add(newTokenRequest)
            closeSession(dbSession)

            pkg = toolkit.get_action('package_show')({}, {'id': datasetID})
            res = toolkit.get_action('resource_show')({}, {'id': resourceID})

            try:
                contact = pkg["ILRI_actycontactperson"]
                contactemail = pkg["ILRI_actycontactemail"]
            except:
                contact = ""
                contactemail = ""

            message = "We have received a confidential application with the following details: \n\n";
            message = message + "Request ID: " + str(requestID) + "\n"
            message = message + "Dataset: " + pkg["title"] + "\n"
            message = message + "Resource: " + res["name"] + "\n"
            message = message + "The custodian for this dataset is: " + pkg["ILRI_actycustodian"] + "\n"
            message = message + "Custodian email: " + pkg["ILRI_actycustodianemail"] + "\n\n"
            message = message + "*******************Details of the request*****************" + "\n\n"
            message = message + "IP Address: " + ipAddress + "\n"
            message = message + "Name: " + data["field_name"] + "\n"
            message = message + "Email: " + data["field_email"] + "\n"
            message = message + "Organization: " + data["field_organization"] + "\n"
            message = message + "Organization Type: " + data["field_organizationType"] + "\n"
            message = message + "Country: " + data["field_country"] + "\n"
            message = message + "Data usage: " + data["field_notes"] + "\n"
            message = message + "Hear from: " + data["field_hearfrom"] + "\n"
            message = message + "Other datasets: " + data["field_otherdatasets"] + "\n\n"

            message = message + "Please contact the custodian for approval of this application\n"

            if contactemail != "":
                sendTokenRequestMail(message,contact,contactemail)
            else:
                logging.debug("Cannot send email. The contact person is empty")

        except Exception,e:
            closeSession(dbSession)
            return False, {'Portal Error':str(e)}

        return True, {}