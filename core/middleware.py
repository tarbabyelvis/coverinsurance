import logging

logger = logging.getLogger(__name__)


class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"API called: {request.method} {request.path}")
        self.log_request(request)
        response = self.get_response(request)
        self.log_response(response)
        return response

    def log_request(self, request):
        logger.info(f"Request: {request.method} {request.get_full_path()}")
        logger.info(f"Headers: {self.filter_sensitive_headers(request.headers)}")

    def log_response(self, response):
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.content}")

    def filter_sensitive_headers(self, headers):
        sensitive_headers = ['Authorization', 'Cookie']
        return {k: (v if k not in sensitive_headers else 'REDACTED') for k, v in headers.items()}
