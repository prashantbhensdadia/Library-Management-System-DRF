from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from rest_framework import status
from rest_framework.authtoken.models import Token


class MyAuthentication(TokenAuthentication):

    def authenticate(self, request):
        # Fetching token HTTP_AUTHORIZATION
        auth_token = request.META.get("HTTP_AUTHORIZATION")
        response = {}
        
        if auth_token == None or auth_token == '':
            # Token is blank or Token is required
            response['message'] = "Token is required."
            response['status'] = status.HTTP_401_UNAUTHORIZED
            raise exceptions.AuthenticationFailed(response)
        
        else:
            if not auth_token.startswith('Token '):
                # Token format is invalid
                response['message'] = "Token format is invalid."
                response['status'] = status.HTTP_401_UNAUTHORIZED
                raise exceptions.AuthenticationFailed(response)
        
        # Fetching token key
        auth_token = auth_token.split(' ')

        # Checking token is valid or not
        token = Token.objects.filter(key = auth_token[1]).first() 
        if not token:
            # Token value is invalid
            response['message'] = "Token is invalid."
            response['status'] = status.HTTP_401_UNAUTHORIZED
            raise exceptions.AuthenticationFailed(response)
        
        return (token.user, token) 

