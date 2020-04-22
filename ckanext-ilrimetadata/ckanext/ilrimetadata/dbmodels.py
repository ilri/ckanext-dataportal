
#Basic SQLAlchemy types
from sqlalchemy import (
    Column,
    Text,
    DateTime,
    Integer,
    ForeignKey
    )


from .meta import Base

import datetime


#Model/class of users
class userModel(Base):
    __tablename__ = 'user'
    user_id = Column(Text, primary_key=True)
    user_name = Column(Text)
    user_password = Column(Text)
    user_email = Column(Text)
    user_org = Column(Text)
    user_active = Column(Integer)
    date_added = Column(DateTime, nullable=False)
    added_by = Column(Text, nullable=False)

    def __init__(self, user_id, user_name, user_password, user_email, user_org, added_by):
        self.user_id = user_id
        self.user_password = user_password
        self.user_name = user_name
        self.user_email = user_email
        self.user_org = user_org
        self.user_active = 1
        self.date_added = datetime.datetime.now()
        self.added_by = added_by


#Model/class of tokens
class tokenModel(Base):
    __tablename__ = "token"
    token_id = Column(Text, primary_key=True)
    token_givendate = Column(DateTime, nullable=False)
    token_givenby = Column(Text, nullable=False)
    token_active = Column(Integer)

    def __init__(self,token_id,token_givenby):
        self.token_id = token_id
        self.token_givendate = datetime.datetime.now()
        self.token_givenby = token_givenby
        self.token_active = 1

#Model/class of resourceStats. Each downloaded resource either public, confidential or private stores a record in this table
class resourcestatsModel(Base):
    __tablename__ = "resourcestats"
    request_id = Column(Text, primary_key=True)
    request_date = Column(DateTime, nullable=False)
    request_ip = Column(Text, nullable=False)
    resource_id = Column(Text, nullable=False)
    resource_format = Column(Text, nullable=False)
    token_id = Column(Text, ForeignKey("token.token_id"))
    user_id = Column(Text, ForeignKey("user.user_id"))
    request_name = Column(Text)
    request_email = Column(Text)
    request_org = Column(Text)
    request_orgtype = Column(Text)
    request_country = Column(Text)
    request_datausage = Column(Text)
    request_hearfrom = Column(Text)

    def __init__(self,request_id, request_date, request_ip, resource_id, resource_format, token_id, user_id, request_name, request_email, request_org, request_orgtype, request_country, request_datausage, request_hearfrom):
        self.request_id = request_id
        self.request_date = request_date
        self.request_ip = request_ip
        self.resource_id = resource_id
        self.resource_format = resource_format
        if user_id is None:
            self.token_id = token_id
        if token_id is None:
            self.user_id = user_id
        if token_id is None and user_id is None:
            self.request_name = request_name
            self.request_email = request_email
            self.request_org = request_org
            self.request_orgtype = request_orgtype
            self.request_country = request_country
            self.request_datausage = request_datausage
            self.request_hearfrom = request_hearfrom

#Model/class of Token requests.
class tokenrequestModel(Base):
    __tablename__ = "tokenrequest"
    request_id = Column(Text, primary_key=True)
    request_date = Column(DateTime, nullable=False)
    request_ip = Column(Text, nullable=False)
    dataset_id = Column(Text, nullable=False)
    resource_id = Column(Text, nullable=False)
    user_name = Column(Text)
    user_email = Column(Text)
    user_org = Column(Text)
    user_orgtype = Column(Text)
    user_country = Column(Text)
    user_datausage = Column(Text)
    user_otherdata = Column(Text)
    user_hearfrom = Column(Text)
    token_given = Column(Text, ForeignKey("token.token_id"))

    def __init__(self, request_id, request_date, request_ip, dataset_id, resource_id, user_name, user_email, user_org, user_orgtype, user_country, user_datausage, user_otherdata, user_hearfrom):
        self.request_id = request_id
        self.request_date = request_date
        self.request_ip = request_ip
        self.dataset_id = dataset_id
        self.resource_id = resource_id
        self.user_name = user_name
        self.user_email = user_email
        self.user_org = user_org
        self.user_orgtype = user_orgtype
        self.user_country = user_country
        self.user_datausage = user_datausage
        self.user_otherdata = user_otherdata
        self.user_hearfrom = user_hearfrom


#Model/class of Datasets accessed by tokens.
class datasetokenModel(Base):
    __tablename__ = "datasetoken"
    dataset_id = Column(Text, primary_key=True)
    token_id = Column(Text, ForeignKey("token.token_id"), primary_key=True, nullable=False)
    grant_date = Column(DateTime, nullable=False)
    grant_by = Column(Text, nullable=False)

    def __init__(self, dataset_id, token_id, grant_by):
        self.dataset_id = dataset_id
        self.token_id = token_id
        self.grant_date = datetime.datetime.now()
        self.grant_by = grant_by

#Model/class of Resources accessed by tokens
class resourcetokenModel(Base):
    __tablename__ = "resourcetoken"
    resource_id = Column(Text, primary_key=True)
    token_id = Column(Text, ForeignKey("token.token_id"), primary_key=True, nullable=False)
    grant_date = Column(DateTime, nullable=False)
    grant_by = Column(Text, nullable=False)
    dataset_id = Column(Text, nullable=False)

    def __init__(self, dataset_id, resource_id, token_id, grant_by):
        self.dataset_id = dataset_id
        self.resource_id = resource_id
        self.token_id = token_id
        self.grant_date = datetime.datetime.now()
        self.grant_by = grant_by

#Model/class of User Groups
class authgroupModel(Base):
    __tablename__ = "authgroup"
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(Text, nullable=False)
    date_added = Column(DateTime, nullable=False)
    added_by = Column(Text, nullable=False)

    def __init__(self, group_name,added_by):
        self.group_name = group_name
        self.date_added = datetime.datetime.now()
        self.added_by = added_by

#Model/class of Users in Groups
class usergroupModel(Base):
    __tablename__ = "usergroup"
    user_id = Column(Text, ForeignKey("user.user_id"), primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey("authgroup.group_id"), primary_key=True, nullable=False)
    join_date = Column(DateTime, nullable=False)
    joined_by = Column(Text, nullable=False)

    def __init__(self, user_id, group_id, join_by):
        self.user_id = user_id
        self.group_id = group_id
        self.join_date = datetime.datetime.now()
        self.joined_by = join_by

#Model/class of datasets granted to a user
class userdatasetModel(Base):
    __tablename__ = "userdataset"
    dataset_id = Column(Text, primary_key=True, nullable=False)
    user_id = Column(Text, ForeignKey("user.user_id"), primary_key=True, nullable=False)
    grant_date = Column(DateTime, nullable=False)
    grant_by = Column(Text, nullable=False)

    def __init__(self, dataset_id, user_id, grant_by):
        self.dataset_id = dataset_id
        self.user_id = user_id
        self.grant_date = datetime.datetime.now()
        self.grant_by = grant_by

#Model/class of resources granted to a user
class useresourceModel(Base):
    __tablename__ = "useresource"
    dataset_id = Column(Text, primary_key=True, nullable=False)
    resource_id = Column(Text, primary_key=True, nullable=False)
    user_id = Column(Text, ForeignKey("user.user_id"), primary_key=True, nullable=False)
    grant_date = Column(DateTime, nullable=False)
    grant_by = Column(Text, nullable=False)

    def __init__(self, dataset_id, resource_id, user_id, grant_by):
        self.dataset_id = dataset_id
        self.resource_id = resource_id
        self.user_id = user_id
        self.grant_date = datetime.datetime.now()
        self.grant_by = grant_by

#Model/class of datasets granted to a group
class groupdatasetModel(Base):
    __tablename__ = "groupdataset"
    dataset_id = Column(Text, primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey("authgroup.group_id"), primary_key=True, nullable=False)
    grant_date = Column(DateTime, nullable=False)
    grant_by = Column(Text, nullable=False)

    def __init__(self, dataset_id, group_id, grant_by):
        self.dataset_id = dataset_id
        self.group_id = group_id
        self.grant_date = datetime.datetime.now()
        self.grant_by = grant_by

#Model/class of resources granted to a group
class groupresourceModel(Base):
    __tablename__ = "groupresource"
    resource_id = Column(Text, primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey("authgroup.group_id"), primary_key=True, nullable=False)
    dataset_id = Column(Text, nullable=False)
    grant_date = Column(DateTime, nullable=False)
    grant_by = Column(Text, nullable=False)

    def __init__(self, dataset_id, resource_id, group_id, grant_by):
        self.resource_id = resource_id
        self.group_id = group_id
        self.dataset_id = dataset_id
        self.grant_date = datetime.datetime.now()
        self.grant_by = grant_by


#Model/class for administrators users
class adminUsersModel(Base):
    __tablename__ = "adminusers"
    ckan_user = Column(Text, primary_key=True, nullable=False)
    can_adduser = Column(Integer)
    can_addresusers = Column(Integer)
    can_addresgroups = Column(Integer)
    can_addrestokens = Column(Integer)
    is_resAdmin = Column(Integer)

    def __init__(self,ckan_user,can_adduser,can_addresusers,can_addresgroups,can_addrestokens,is_resAdmin):
        self.ckan_user = ckan_user
        self.can_adduser = can_adduser
        self.can_addresusers = can_addresusers
        self.can_addresgroups = can_addresgroups
        self.can_addrestokens = can_addrestokens
        self.is_resAdmin = is_resAdmin
