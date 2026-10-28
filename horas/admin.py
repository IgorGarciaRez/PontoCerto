from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RelatedDropdownFilter

from .models import Projeto


@admin.register(Projeto)
class ProjetoAdmin(ModelAdmin):
    list_display = ["nome", "cliente", "ativo"]
    search_fields = ["nome", "cliente"]
    list_filter = ["ativo", ("membros", RelatedDropdownFilter)]
    list_filter_submit = True
    filter_horizontal = ["membros"]

