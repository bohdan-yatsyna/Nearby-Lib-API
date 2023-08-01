from typing import Type

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from library_app.pagination import Pagination
from payments.models import Payment
from payments.serializers import PaymentSerializer, PaymentDetailSerializer


# Only for documentation purposes (Swagger)
@extend_schema_view(
    list=extend_schema(
        description=(
            "Endpoint with list of payment. "
            "For standard users only their borrowings, "
            "for admin users all the borrowings in the system."
        )
    ),
    retrieve=extend_schema(
        description="Endpoint showing specific payment by it id"
    ),
)
class PaymentViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Payment.objects.select_related("borrowing_id")
    serializer_class = PaymentSerializer
    pagination_class = Pagination
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self) -> Type[Serializer]:

        if self.action == "retrieve":
            return PaymentDetailSerializer

        return PaymentSerializer

    def get_queryset(self) -> QuerySet[Payment]:
        user = self.request.user
        queryset = self.queryset

        if not user.is_staff:
            queryset.filter(borrowing_id__user=user)

        return queryset
