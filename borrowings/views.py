from typing import Type, Any

from django.db import transaction
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
    CreateBorrowingSerializer,
)
from library_app.pagination import Pagination
from notifications.notifications_bot import send_borrowing_return_notification


# Only for documentation purposes (Swagger)
@extend_schema_view(
    list=extend_schema(
        description=(
                "Endpoint with list of borrowings. "
                "For standard users only their borrowings, "
                "for admin user all the borrowings in the system."
        )
    ),
    create=extend_schema(
        description=(
                "Endpoint for creating borrowings, "
                "for authenticated users only"
        )
    ),
    retrieve=extend_schema(
        description="Endpoint showing specific borrowing by it id"
    ),
)
class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related("book", "user")
    pagination_class = Pagination
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateBorrowingSerializer

    def get_queryset(self) -> QuerySet[Borrowing]:
        queryset = self.queryset
        user = self.request.user
        is_active = self.request.query_params.get("is_active")

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        if user.is_staff:
            user_id = self.request.query_params.get("user_id")

            if user_id:
                queryset = queryset.filter(user__id=user_id)

        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)

        return queryset

    def get_serializer_class(self) -> Type[Serializer]:

        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "return_book":
            return BorrowingReturnSerializer

        return CreateBorrowingSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAdminUser],
    )
    def return_book(self, request, pk=None) -> Response:
        """Endpoint for borrowing returning"""

        with transaction.atomic():
            borrowing = self.get_object()
            serializer = self.get_serializer(borrowing, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            send_borrowing_return_notification(
                borrowing=borrowing
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

    # Only for documentation purposes (Swagger)
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                description=(
                    "Parameter for filtering according to user_id, "
                    "for admin users only (ex. '?user_id=1)."
                ),
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="is_active",
                description=(
                    "Filtering according to active borrowings "
                    "(ex. ?is_active=True)."
                ),
                required=False,
                type=str,
            ),
        ],
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(self, request, *args, **kwargs)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)
