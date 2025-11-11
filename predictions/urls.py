# predictions/urls.py
from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import PredictDemandView, RecommendProductView, PredictSalesView

urlpatterns = [
    # Vamos a crear una vista llamada 'PredictDemandView'
    # La URL será algo como: /api/predict/demand/1/ (para el producto 1)
    #path('demand/<int:producto_id>/', views.PredictDemandView.as_view(), name='predict_demand'),

    # --- Endpoint 1 (El que ya tenías) ---
    # (Ej: /api/predict/demand/3/)
    path('demand/<int:producto_id>/', 
         views.PredictDemandView.as_view(), 
         name='predict_demand'),
    
    # --- Endpoint 2 (¡EL NUEVO!) ---
    # (Ej: /api/predict/recommend/3/)
    path('recommend/<int:producto_id>/', 
         views.RecommendProductView.as_view(), 
         name='predict_recommend'),

    path('sales/category/<int:subcategoria_id>/', 
         views.PredictSalesView.as_view(), 
         name='predict_sales_category'),
]