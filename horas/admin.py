from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RangeDateFilter,
    RangeNumericFilter,
    RelatedDropdownFilter,
)

from .models import Entrega, Projeto


@admin.register(Projeto)
class ProjetoAdmin(ModelAdmin):
    list_display = ["nome", "cliente", "ativo"]
    search_fields = ["nome", "cliente"]
    list_filter = ["ativo", ("membros", RelatedDropdownFilter)]
    list_filter_submit = True
    filter_horizontal = ["membros"]


@admin.register(Entrega)
class EntregaAdmin(ModelAdmin):
    list_display = ["data", "colaborador", "projeto", "horas", "status", "assinado_por"]
    search_fields = ["descricao", "projeto__nome", "colaborador__username", "colaborador__first_name"]
    list_filter = [
        ("status", ChoicesDropdownFilter),
        ("colaborador", RelatedDropdownFilter),
        ("projeto", RelatedDropdownFilter),
        ("data", RangeDateFilter),
        ("horas", RangeNumericFilter),
    ]
    list_filter_submit = True
    readonly_fields = ["assinado_por", "assinado_em"]

    def save_model(self, request, obj, form, change):
        if "status" in form.changed_data:
            obj.registrar_assinatura(request.user)
        super().save_model(request, obj, form, change)
