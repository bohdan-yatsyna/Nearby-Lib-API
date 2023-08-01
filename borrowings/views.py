from typing import Type, Any

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
    CreateBorrowingSerializer,
)
from library_app.pagination import Pagination


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
        user = self.request.user
        queryset = self.queryset

        if user.is_staff is False:
            queryset.filter(user=user)

        if user.is_staff:
            user_id = self.request.query_params.get("user_id")

            if user_id:
                queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active")

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
            borrowing = Borrowing.objects.get(pk=pk)

            if not borrowing.actual_return_date:
                serializer = self.get_serializer(borrowing, data=request.data)
                serializer.is_valid(raise_exception=True)
                borrowing.actual_return_date = serializer.validated_data.get(
                    "actual_return_date"
                )
                borrowing.save()

                book_id = borrowing.book
                book = get_object_or_404(Book, id=book_id)
                book.inventory += 1
                book.save()

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                {"details": "It is impossible to return borrowed book twice"}
            )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(self, request, *args, **kwargs)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user_id=self.request.user)
