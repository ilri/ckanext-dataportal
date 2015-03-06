from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .dbmodels import userModel
from .dbmodels import resourcestatsModel
from .dbmodels import tokenrequestModel
from .dbmodels import datasetokenModel
from .dbmodels import resourcetokenModel
from .dbmodels import DBSession
from .dbmodels import useresourceModel
from .dbmodels import userdatasetModel
from .dbmodels import usergroupModel
from .dbmodels import groupresourceModel
from .dbmodels import groupdatasetModel

import transaction

import datetime

from pylons import config
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import Utils
from ckan.common import _
from time import time
import logging

def add_msg_niceties(recipient_name, body, sender_name, sender_url):
    return _(u"Dear %s,") % recipient_name \
           + u"\r\n\r\n%s\r\n\r\n" % body \
           + u"--\r\n%s (%s)" % (sender_name, sender_url)

def sendTokenRequestMail(body):

    mail_from = config.get('smtp.mail_from')
    body = add_msg_niceties("Carlos", body, "CKAN Portal", "http://data.ilri.org/portal")
    msg = MIMEText(body.encode('utf-8'), 'plain', 'utf-8')
    ssubject = "New token request"
    subject = Header(ssubject.encode('utf-8'), 'utf-8')
    msg['Subject'] = subject
    msg['From'] = _("%s <%s>") % ("CKAN Portal", mail_from)
    recipient = u"%s <%s>" % ("Carlos Quiros", "c.f.quiros@cgiar.org")
    msg['To'] = Header(recipient, 'utf-8')
    msg['Date'] = Utils.formatdate(time())

    try:
        smtp_connection = smtplib.SMTP()
        smtp_server = config.get('smtp.server', 'localhost')
        smtp_user = config.get('smtp.user')
        smtp_password = config.get('smtp.password')

        smtp_connection.connect(smtp_server)
        smtp_connection.login(smtp_user, smtp_password)
        smtp_connection.sendmail(mail_from, ["c.f.quiros@cgiar.org"], msg.as_string())
        logging.info("Token Email sent to c.f.quiros@cgiar.org")

    except Exception,e:
        logging.info("Token Sendmail error: " + str(e))



def processToken(requestID,ipAddress,datasetID,resourceID,token,format):

    mySession = DBSession()


    #Check if the token has access to the resource
    result = mySession.query(resourcetokenModel).filter_by(resource_id = resourceID).filter_by(token_id = token).first()
    if result is None:
        #If not then check if the token as access to the dataset of the resource
        result = mySession.query(datasetokenModel).filter_by(dataset_id = datasetID).filter_by(token_id = token).first()

    if result is None:
        mySession.close()
        return False
    else:

        #If the token is valid then we add the request to the Book
        newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,token,None,"","","","","","","")
        transaction.begin()
        mySession.add(newGuestBookRecord)
        transaction.commit()
        mySession.close()
        return True

def processUser(requestID,ipAddress,datasetID,resourceID,user,password,format):

    mySession = DBSession()

    #Check if the user and password are correct
    result = mySession.query(userModel).filter_by(user_id = user).filter_by(user_password = password).first()
    if result is None:
        mySession.close()
        return False
    else:
        #Checks if the user has access to the resource
        result = mySession.query(useresourceModel).filter_by(user_id = user).filter_by(resource_id = resourceID).first()
        if result is None:
            #Check if the user has access to the dataset of the resource
            result = mySession.query(userdatasetModel).filter_by(user_id = user).filter_by(dataset_id = datasetID).first()
            if result is None:
                #Get all the groups of the user
                groupAccess = False
                for row in mySession.query(usergroupModel).filter_by(user_id = user).all():
                    #Check if the group has access to the resource
                    result =  mySession.query(groupresourceModel).filter_by(group_id = row.group_id).filter_by(resource_id = resourceID).first()
                    if result == None:
                        #Check if the group has access to the dataset of the resource
                        result =  mySession.query(groupdatasetModel).filter_by(group_id = row.group_id).filter_by(dataset_id = datasetID).first()
                        if result != None:
                            groupAccess = True
                            break
                    else:
                        groupAccess = True
                        break
                if groupAccess == True:
                    #If the user is valid then we add the request to the Book
                    newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,None,user,"","","","","","","")
                    transaction.begin()
                    mySession.add(newGuestBookRecord)
                    transaction.commit()
                    mySession.close()
                    return True
                else:
                    mySession.close()
                    return False
            else:
                #If the user is valid then we add the request to the Book
                newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,None,user,"","","","","","","")
                transaction.begin()
                mySession.add(newGuestBookRecord)
                transaction.commit()
                mySession.close()
                return True
        else:
            #If the user is valid then we add the request to the Book
            newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,None,user,"","","","","","","")
            transaction.begin()
            mySession.add(newGuestBookRecord)
            transaction.commit()
            mySession.close()
            return True

def processGuest(requestID,ipAddress,resourceID,data,format):

    errors = {}

    if data["field_name"] == "":
        errors["Name"] = "Name is required"

    if data["field_email"] == "":
        errors["Email"] = "Email is required."

    if data["field_organization"] == "":
        errors["Organization"] = "Organization is required"

    if data["field_organizationType"] == "":
        errors["Organization Type"] = "Organization Type is required"

    if data["field_country"] == "":
        errors["Country"] = "Country is required"

    if data["field_notes"] == "":
        errors["Data usage"] = "Data usage is required"

    if data["field_hearfrom"] == "":
        errors["Hear from"] = "Indicate how you hear about this dataset/resource"


    if len(errors) > 0:
        return False,errors
    else:
        mySession = DBSession()
        try:
            #If there are no errors in the data try to add the new Guest Book Record
            newGuestBookRecord = resourcestatsModel(requestID,datetime.datetime.now(),ipAddress,resourceID,format,None,None,data["field_name"],data["field_email"],data["field_organization"],data["field_organizationType"],data["field_country"],data["field_notes"],data["field_hearfrom"])
            transaction.begin()
            mySession.add(newGuestBookRecord)
            transaction.commit()
            mySession.close()
        except Exception,e:
            transaction.abort()
            mySession.close()
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

    if data["field_organizationType"] == "":
        errors["Organization Type"] = "Organization Type is required"

    if data["field_country"] == "":
        errors["Country"] = "Country is required"

    if data["field_notes"] == "":
        errors["Data usage"] = "Data usage is required"

    if data["field_hearfrom"] == "":
        errors["Hear from"] = "Indicate how you hear about this dataset/resource"

    if data["field_aggrement"] == "no":
        errors["Agreement"] = "You need to accept the Confidentiality Agreement"

    if len(errors) > 0:
        return False,errors
    else:
        mySession = DBSession()
        try:
            #If there are no errors in the data try to add the new token request
            newTokenRequest = tokenrequestModel(requestID,datetime.datetime.now(),ipAddress,datasetID,resourceID,data["field_name"],data["field_email"],data["field_organization"],data["field_organizationType"],data["field_country"],data["field_notes"],data["field_otherdatasets"],data["field_hearfrom"])
            transaction.begin()
            mySession.add(newTokenRequest)
            transaction.commit()
            mySession.close()

            message = "We have received a confidential application with the following details: \n\n";

            message = message + "Request ID: " + str(requestID) + "\n"
            message = message + "Dataset ID: " + datasetID + "\n"
            message = message + "Resource ID: " + resourceID + "\n"
            message = message + "IP Address: " + ipAddress + "\n\n"
            message = message + "Name: " + data["field_name"] + "\n"
            message = message + "Email: " + data["field_email"] + "\n"
            message = message + "Organization: " + data["field_organization"] + "\n"
            message = message + "Organization Type: " + data["field_organizationType"] + "\n"
            message = message + "Country: " + data["field_country"] + "\n"
            message = message + "Data usage: " + data["field_notes"] + "\n"
            message = message + "Hear from: " + data["field_hearfrom"] + "\n"
            message = message + "Other datasets: " + data["field_otherdatasets"] + "\n"

            sendTokenRequestMail(message)

        except Exception,e:
            transaction.abort()
            mySession.close()
            return False, {'Portal Error':str(e)}

        return True, {}