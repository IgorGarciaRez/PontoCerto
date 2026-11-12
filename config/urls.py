from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from contas.views import LoginForm, cadastro
from horas import views as horas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/login/', LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('contas/', include('django.contrib.auth.urls')),  # logout
    path('contas/cadastro/', cadastro, name='cadastro'),
    path('', horas.inicio, name='inicio'),
    path('entregas/<int:pk>/excluir/', horas.entrega_excluir, name='entrega_excluir'),
    path('assinaturas/', horas.assinaturas, name='assinaturas'),
    path('assinaturas/<int:pk>/<str:acao>/', horas.assinar, name='assinar'),
]
