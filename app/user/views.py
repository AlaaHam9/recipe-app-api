from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializer import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create new auth token for the user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class        = UserSerializer
    authentication_classes  = [authentication.TokenAuthentication] # How do you know that the user is the user they say they are
    permission_classes      = [permissions.IsAuthenticated]

    # override the get method to just retrieving the user that's attached to the request
    def get_object(self):
        return self.request.user