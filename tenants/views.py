from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
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
            tenant["domain"] = f"https://{domain[0]['domain']}"
            if tenant["name"] != "public":
                result.append(tenant)
        return Response(result, status=status.HTTP_200_OK)
