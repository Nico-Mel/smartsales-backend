# tenants/views.py
from rest_framework import viewsets
from .models import Empresa, Plan 
from .serializers import EmpresaSerializer, PlanSerializer 
from utils.permissions import ModulePermission

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.filter(activo=True)
    serializer_class = PlanSerializer
    permission_classes = [ModulePermission]
    module_name = "Plan"

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all().order_by('nombre')
    serializer_class = EmpresaSerializer
    permission_classes = [ModulePermission]
    module_name = "Empresa"

# Create your views here.
