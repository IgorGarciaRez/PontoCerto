from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from contas.views import LoginForm, cadastro

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/login/', LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('contas/', include('django.contrib.auth.urls')),  # logout
    path('contas/cadastro/', cadastro, name='cadastro'),
]
