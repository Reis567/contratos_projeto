# contratos/urls.py
from django.urls import path
from . import views

# contratos/urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('contrato/novo/', views.selecionar_tipo_contrato, name='selecionar_tipo_contrato'),
    path('contrato/locacao/novo/', views.criar_contrato_locacao, name='criar_contrato_locacao'),
    path('contrato/<int:contrato_id>/', views.visualizar_contrato, name='visualizar_contrato'),
    path('contrato/<int:contrato_id>/pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('contrato/<int:contrato_id>/editar/', views.editar_contrato, name='editar_contrato'),
]