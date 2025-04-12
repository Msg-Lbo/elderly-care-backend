from rest_framework.response import Response
from rest_framework import status

class APIResponse(Response):
    def __init__(self, code=200, message='success', data=None, status=status.HTTP_200_OK, **kwargs):
        response_data = {
            'code': code,
            'message': message,
            'data': data
        }
        super().__init__(data=response_data, status=status, **kwargs)

class APIError(Exception):
    def __init__(self, code=400, message='error', data=None):
        self.code = code
        self.message = message
        self.data = data 