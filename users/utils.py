from rest_framework.pagination import PageNumberPagination


def normalize_email(email):
    """
    Normalize the email address by lowercasing the domain part of it.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        pass
    else:
        email = email_name + '@' + domain_part.lower()
    return email


class BaseResponse:
    def __init__(self, data=None, message=None, status=None, pagination=None):
        self.data = data
        self.message = message
        self.status = status
        self.pagination = pagination

    def to_dict(self):
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "pagination": self.pagination
        }


class Pagination(PageNumberPagination):
    page_size = 15
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 50


class PaginationHandlerMixin(object):
    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class PaginationResponse:
    def __init__(self, page_size=None, count=None, page=None):
        self.page_size = page_size
        self.count = count
        self.page = page

    def to_dict(self):
        return {
            "page_size": self.page_size,
            "count": self.count,
            "current_page": self.page
        }
