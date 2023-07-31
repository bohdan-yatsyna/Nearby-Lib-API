from typing import Type

from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from library_app.pagination import Pagination
from payments.models import Payment
from payments.serializers import PaymentSerializer, PaymentDetailSerializer


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
        queryset = self.queryset

        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")

            if user_id:
                queryset = queryset.filter(user_id=user_id)

            return queryset

        queryset = queryset.filter(borrowing_id__user=self.request.user.id)

        return queryset
