"""User Api views"""

from rest_framework import (generics, authentication, permissions,)
from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateAuthTokenView(ObtainAuthToken):
    """Create a new auth token for user."""

    serializer_class = AuthTokenSerializer
    # allow you to return responses with various media type
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageProfileView(generics.RetrieveUpdateAPIView):
    """Manage to authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the authenticated user"""

        return self.request.user
