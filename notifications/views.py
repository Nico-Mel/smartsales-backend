from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from utils.viewsets import SoftDeleteViewSet
from .models import Notificacion
from .serializers import NotificacionSerializer

class NotificacionViewSet(SoftDeleteViewSet):
    queryset = Notificacion.objects.all().order_by("-fecha_creada")
    serializer_class = NotificacionSerializer
    module_name = "Notificacion"

    def perform_create(self, serializer):
        # asigna empresa automáticamente si el usuario tiene una
        user = self.request.user
        empresa = getattr(user, "empresa", None)
        # si el payload incluye usuario distinto, se respetará; normalmente backend usa request.user
        serializer.save(empresa=empresa)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        noti = self.get_object()
        noti.leida = True
        noti.save()
        return Response({"detail": "Marcada como leída."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        user = request.user
        qs = self.get_queryset().filter(usuario=user, leida=False)
        updated = qs.update(leida=True)
        return Response({"updated": updated}, status=status.HTTP_200_OK)
