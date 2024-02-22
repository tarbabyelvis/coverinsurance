# Generic Class Creation with Django REST Framework

## Overview

This README describes a generic way of creating class-based views in Django REST
Framework (DRF) along with a custom HTTP response class.

## Code Structure

```python
from rest_framework.views import APIView
from FinCover.http_responses import HTTPResponse

class YourAPIView(APIView):
    def get(self, request):
        data = {'key': 'value'}
        return HTTPResponse.success(data)

    def post(self, request):
        # Perform actions and handle exceptions
        try:
            # Some logic
            return HTTPResponse.success(message="Resource created successfully", status_code=status.HTTP_201_CREATED)
        except Exception as e:
            return HTTPResponse.error(message=str(e))
```
