import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import routes.mapper as r


class IlrifrontendPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public/images')
        toolkit.add_resource('fanstatic', 'ilrifrontend')

    # IRoutes
    def before_map(self, map):
        # This is a better function because in the connect if defines an item for example ilri_policy that then we can use in build_nav_main helper function
        with r.SubMapper(map,
                         controller='ckanext.ilrifrontend.controller:requestAccountController') as requestAccount:
            requestAccount.connect('requestAccount', '/requestaccount', action='display_requestAccount')

        with r.SubMapper(map, controller='ckanext.ilrifrontend.controller:policyController') as policy:
            policy.connect('ILRIPolicy', '/policy', action='display_policy')

        with r.SubMapper(map, controller='ckanext.ilrifrontend.controller:harvestController') as harvest:
            harvest.connect('HarvestInfo', '/harvestinfo', action='display_harvestInfo')

        # with r.SubMapper(map,  controller='ckanext.ilrifrontend.controller:ILRIAPI_list_Controller') as ILRIAPIListCountries:
        #    ILRIAPIListCountries.connect('ILRIAPIListCountries','/api/ilri/1/action/list_countries',action='list_countries')

        return map

    def after_map(self, map):
        return map