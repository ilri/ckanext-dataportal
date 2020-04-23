import ckan.plugins as plugins
import routes.mapper as r


class IlriapiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes)

    # IConfigurer

    # IRoutes
    def before_map(self, map):
        with r.SubMapper(
            map, controller="ckanext.ilriapi.controller:ILRIAPI_list_Controller"
        ) as ILRIAPIListCountries:
            ILRIAPIListCountries.connect(
                "ILRIAPIListCountries",
                "/api/ilri/1/action/list_countries",
                action="list_countries",
            )
            ILRIAPIListCountries.connect(
                "ILRIAPIListRegions",
                "/api/ilri/1/action/list_regions",
                action="list_regions",
            )
            ILRIAPIListCountries.connect(
                "ILRIAPIListSubjects",
                "/api/ilri/1/action/list_subjects",
                action="list_subjects",
            )
            ILRIAPIListCountries.connect(
                "ILRIAPIListSpecies",
                "/api/ilri/1/action/list_species",
                action="list_species",
            )
            ILRIAPIListCountries.connect(
                "ILRIAPIListStructure",
                "/api/ilri/1/action/list_structure",
                action="list_structure",
            )
            ILRIAPIListCountries.connect(
                "ILRIAPIListTags", "/api/ilri/1/action/list_tags", action="list_tags"
            )
            ILRIAPIListCountries.connect(
                "ILRIAPIListConfFields",
                "/api/ilri/1/action/list_confidential_fields",
                action="list_confidentialFields",
            )

        return map

    def after_map(self, map):
        return map
