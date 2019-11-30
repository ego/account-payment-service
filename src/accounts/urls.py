"""accounts URL Configuration."""

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import include
from rest_framework import routers

from payments import views as pay_views

router = routers.DefaultRouter()  # pylint: disable=C0103
router.register(r"accounts", pay_views.AccountViewSet)
router.register(r"payments", pay_views.PaymentViewSet)


urlpatterns = [url(r"^api/v1/", include((router.urls, "account_service"), namespace="v1"))]  # pylint: disable=C0103


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
