import logging

logger = logging.getLogger(__name__)


class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the API call
        logger.info(f"API called: {request.method} {request.path}")

        # Proceed with the request
        response = self.get_response(request)

        return response
