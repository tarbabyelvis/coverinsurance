from django_tenants.middleware import TenantMiddleware
from django.http import Http404


class CustomTenantMiddleware(TenantMiddleware):
    def process_request(self, request):
        try:
            # get the current tenant based on the request's hostname
            hostname = request.META['HTTP_HOST']
            print("Hostname: {}".format(hostname))
            # tenant = self.get_tenant(hostname)
            # set the request.tenant attribute to the current tenant
            request.tenant = hostname
        except Http404:
            pass
        return super().process_request(request)
