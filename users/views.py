from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers import UserSerializer


# Only for documentation purposes (Swagger)
@extend_schema_view(
    post=extend_schema(
        description="Endpoint for creating user, no permissions required"
    )
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


# Only for documentation purposes (Swagger)
@extend_schema_view(
    get=extend_schema(
        description="Endpoint with detail information about current user"
    ),
    put=extend_schema(
        description="Endpoint for update current user details"
    ),
    patch=extend_schema(
        description="Endpoint for partial update current user details"
    ),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
