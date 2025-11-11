from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MetodoPagoViewSet,
    PagoViewSet,
    VentaViewSet,
    DetalleVentaViewSet,
    CrearStripePaymentIntentView,
)

router = DefaultRouter()
router.register(r"metodos-pago", MetodoPagoViewSet)
router.register(r"pagos", PagoViewSet)
router.register(r"ventas", VentaViewSet)
router.register(r"detalles-venta", DetalleVentaViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        'crear-payment-intent/', # Esta es la URL que llamará React
        CrearStripePaymentIntentView.as_view(), 
        name='crear_payment_intent'
    ),
]
