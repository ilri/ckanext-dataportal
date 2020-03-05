#!/usr/bin/env python
import urllib, json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import Utils
from time import time

def add_msg_niceties(recipient_name, body, sender_name, sender_url):
    return u"Dear %s" % (recipient_name) \
           + u"\r\n\r\n%s\r\n\r\n" % body \
           + u"--\r\n%s (%s)" % (sender_name, sender_url)

def sendMail(body,targetName,targetEmail,targetName2,targetEmail2,dataset):
    print "Sending email!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #targetEmail = "cquiros@qlands.com"
    #targetEmail2 = "c.f.quiros@cgiar.org"
    mail_from = 'ilrirmgdportal@cgiar.org'
    body = add_msg_niceties(targetName, body, "ILRI Datasets Portal", "https://data.ilri.org/portal")
    msg = MIMEText(body.encode('utf-8'), 'plain', 'utf-8')
    ssubject = "The dataset " + '"' + dataset + '"' + " will be made available in next two weeks"
    subject = Header(ssubject.encode('utf-8'), 'utf-8')
    msg['Subject'] = subject
    msg['From'] = u"%s <%s>" % ("CKAN Portal", mail_from)
    recipient = u"%s <%s>" % (targetName, targetEmail) + "," + u"%s <%s>" % (targetName2, targetEmail2)
    msg['To'] = Header(recipient, 'utf-8')
    msg['Date'] = Utils.formatdate(time())

    try:

        smtp_server = 'smtp.office365.com'
        smtp_user = 'ilrirmgdportal@cgiar.org'
        smtp_password = 'super_secret'

        server = smtplib.SMTP(smtp_server,587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.sendmail(mail_from, [targetEmail,targetEmail2], msg.as_string())
        server.quit()
        print("Email sent to " + targetEmail + " and " + targetEmail2)

    except Exception,e:
        print str(e)
        print("Sendmail error: " + str(e))

def main():
    url = "https://data.ilri.org/portal/api/3/action/package_search?q=organization:ilri&rows=2147483647"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    if data["success"] == True:
        for result in data["result"]["results"]:
            if result["ILRI_actydatavailable"] != "" and result["ILRI_actydatavailable"] != "To be defined":
                if result["ILRI_actydatavailable"] == "2014-04-31":
                    result["ILRI_actydatavailable"] = "2014-04-30"

                if result["ILRI_actydatavailable"].find("-") < 0:
                    datetime_object = datetime.strptime(result["ILRI_actydatavailable"], '%d/%m/%Y')
                else:
                    try:
                        datetime_object = datetime.strptime(result["ILRI_actydatavailable"], '%d-%m-%Y')
                    except:
                        datetime_object = datetime.strptime(result["ILRI_actydatavailable"], '%Y-%m-%d')

                now = datetime.now()
                #Available in the next two weeks from now
                numberOfDays = 14
                if datetime_object >= now and datetime_object <= now + timedelta(days=numberOfDays):
                    message = "You are the custodian of " + '"' + result["title"] + '"' + " that will be made available in the next two weeks: \n";
                    message = message + "Availability date: " + result["ILRI_actydatavailable"] + "\n\n"
                    message = message + "Please organize with RMG to check if any confidential fields are locked before release." + "\n\n"
                    sendMail(message,result["ILRI_actycustodian"],result["ILRI_actycustodianemail"],"Harrison Njamba",'h.njamba@cgiar.org',result["title"])
    else:
        print "Bad request"

#Load the main function at start
if __name__ == "__main__":
    main()