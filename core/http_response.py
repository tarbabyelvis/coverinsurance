from rest_framework.response import Response
from rest_framework import status


class HTTPResponse:
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Generate a successful HTTP response.
        :param data: Data to be included in the response.
        :param message: Message to be included in the response.
        :param status_code: HTTP status code.
        :return: Response object.
        """
        return Response(
            {"success": True, "message": message, "data": data}, status=status_code
        )

    @staticmethod
    def error(
        message="Internal Server Error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        """
        Generate an error HTTP response.
        :param message: Error message to be included in the response.
        :param status_code: HTTP status code.
        :return: Response object.
        """
        return Response({"success": False, "message": message}, status=status_code)
