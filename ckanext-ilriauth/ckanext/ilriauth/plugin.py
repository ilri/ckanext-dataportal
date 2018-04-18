import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import routes.mapper as r
from .dbfunctions import userCanAddUsers, userCanManageResources, isResourceAdmin, userResourceAccess


class IlriauthPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes)
    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ILRIAuthDir')

    def get_helpers(self):
        return {'ILRIAuth_userCanAddUsers': userCanAddUsers,
                'ILRIAuth_userCanManageResources': userCanManageResources,
                'ILRIAuth_isResourceAdmin': isResourceAdmin,
                'ILRIAuth_userResourceAccess': userResourceAccess}

    # Implement IRoutes
    def before_map(self, map):
        # This is a better function because in the connect if defines an item for example ilri_policy that then we can use in build_nav_main helper function
        with r.SubMapper(map, controller='ckanext.ilriauth.controller:addNewUserController') as addNewUser:
            addNewUser.connect('addNewUser', '/ilriauth/addNewUser', action='display_addNewUser')

        with r.SubMapper(map, controller='ckanext.ilriauth.controller:statisticsController') as showStats:
            showStats.connect('showStats', '/ilriauth/showstats', action='display_stats')
            showStats.connect('requestStats', '/ilriauth/requeststats', action='request_stats')

        with r.SubMapper(map, controller='ckanext.ilriauth.controller:resourceAuthController') as manageUsers:
            manageUsers.connect('manageUsers', '/ilriauth/manageusers', action='manageUsers')

        with r.SubMapper(map, controller='ckanext.ilriauth.controller:resourceAuthController') as manageOneUser:
            manageOneUser.connect('manageOneUser', '/ilriauth/manageusers/{userID}', action='manageOneUser')

        with r.SubMapper(map, controller='ckanext.ilriauth.controller:resourceAuthController') as manageGroups:
            manageGroups.connect('manageGroups', '/ilriauth/managegroups', action='manageGroups')

        with r.SubMapper(map,
                         controller='ckanext.ilriauth.controller:resourceAuthController') as manageGroupMembers:
            manageGroupMembers.connect('manageGroupMembers', '/ilriauth/managegroups/{groupID}',
                                       action='manageGroupMembers')

        with r.SubMapper(map, controller='ckanext.ilriauth.controller:resourceAuthController') as manageOneGroup:
            manageOneGroup.connect('manageOneGroup', '/ilriauth/managegroups/{groupID}/auth',
                                   action='manageOneGroup')

        with r.SubMapper(map, controller='ckanext.ilriauth.controller:resourceAuthController') as manageTokens:
            manageTokens.connect('manageTokens', '/ilriauth/managetokens', action='manageTokens')

        with r.SubMapper(map, controller='ckanext.ilriauth.controller:resourceAuthController') as manageOneToken:
            manageOneToken.connect('manageOneToken', '/ilriauth/managetokens/{tokenID}', action='manageOneToken')
            manageOneToken.connect('emailToken', '/ilriauth/emailtoken/{tokenID}', action='emailToken')

        with r.SubMapper(map,
                         controller='ckanext.ilriauth.controller:resourceAuthController') as showRequestDetails:
            showRequestDetails.connect('showRequestDetails', '/ilriauth/managetokens/request/{requestID}',
                                       action='showRequestDetails')

        return map

    def after_map(self, map):
        return map