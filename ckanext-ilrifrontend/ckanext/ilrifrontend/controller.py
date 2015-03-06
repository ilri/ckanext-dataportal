import ckan.plugins.toolkit as toolkit

class requestAccountController(toolkit.BaseController):
    def display_requestAccount(self):
        return toolkit.render('ilripages/request_account.html')

class policyController(toolkit.BaseController):
    def display_policy(self):
        return toolkit.render('ilripages/display_policy.html')

class harvestController(toolkit.BaseController):
    def display_harvestInfo(self):
        vars = {'host': toolkit.request.host_url}
        return toolkit.render('ilripages/harvest_info.html',extra_vars=vars)

