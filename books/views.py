from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from books.models import Book
from books.permissions import IsAdminOrIfUserReadOnly
from books.serializers import BookSerializer
from library_app.pagination import Pagination


# Only for documentation purposes (Swagger)
@extend_schema_view(
    list=extend_schema(
        description="Endpoint showing list of all books in the system"
    ),
    retrieve=extend_schema(
        description="Endpoint showing specific book by it id"
    ),
    create=extend_schema(
        description="Endpoint for creating book, admin users only"
    ),
    update=extend_schema(
        description="Endpoint for updating book, admin users only"
    ),
    partial_update=extend_schema(
        description="Endpoint for partial book updating, admin users only"
    ),
    destroy=extend_schema(
        description="Endpoint for deleting book, admin users only"
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = Pagination
    permission_classes = (IsAdminOrIfUserReadOnly,)
    authentication_classes = (JWTAuthentication,)
