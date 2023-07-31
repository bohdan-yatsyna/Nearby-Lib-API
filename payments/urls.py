from rest_framework import routers

from payments.views import PaymentViewSet

app_name = "borrowings"

router = routers.DefaultRouter()
router.register("", PaymentViewSet, basename="borrowing")

urlpatterns = [] + router.urls
