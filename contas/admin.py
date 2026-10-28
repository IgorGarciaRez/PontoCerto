from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import Usuario

admin.site.unregister(Group)  # perfis são definidos pelo campo "perfil", grupos não são usados


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ["username", "first_name", "email", "perfil", "is_active"]
    list_filter = [("perfil", ChoicesDropdownFilter), "is_active", "is_staff"]
    list_filter_submit = True
    fieldsets = [
        (None, {"fields": ["username", "password"]}),
        ("Dados pessoais", {"fields": ["first_name", "last_name", "email", "perfil"]}),
        ("Acesso", {"fields": ["is_active", "is_staff", "is_superuser"]}),
    ]
    add_fieldsets = [
        (None, {"fields": ["username", "password1", "password2", "first_name", "perfil"]}),
    ]
