from sqlalchemy.orm import configure_mappers

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from .dbmodels import (
    userModel,
    tokenModel,
    resourcestatsModel,
    tokenrequestModel,
    datasetokenModel,
    resourcetokenModel,
    authgroupModel,
    usergroupModel,
    userdatasetModel,
    useresourceModel,
    groupdatasetModel,
    groupresourceModel,
    adminUsersModel,
)  # flake8: noqa

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()
