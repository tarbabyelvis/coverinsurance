from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from core.http_response import HTTPResponse
from .models import Tenant, Domain


class GetTenants(APIView):
    def get(self, request, *args, **kwargs):
        print("Getting the hostname: {}".format(request.META.get("HTTP_HOST", "")))
        url = request.build_absolute_uri("/")
        print(f"Domain url is {url}")
        tenants = Tenant.objects.filter().values()
        domains = list(Domain.objects.filter().values())
        result = []
        for tenant in tenants:
            domain = list(filter(lambda d: d["tenant_id"] == tenant["id"], domains))
            host = domain[0]['domain'].split('.')[1]
            protocol = "http" if host == "localhost" else "https"
            tenant["domain"] = f"{protocol}://{domain[0]['domain']}"
            if tenant["name"] != "public":
                result.append({'shortName': tenant["short_name"], 'domain': tenant["domain"]})
            print(result)
        return HTTPResponse.success(
            data=result,
            message="Resource retrieved successfully",
            status_code=status.HTTP_200_OK,
        )
