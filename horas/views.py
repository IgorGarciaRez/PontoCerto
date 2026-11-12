from functools import wraps

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from unfold.widgets import (
    INPUT_CLASSES,
    UnfoldAdminDecimalFieldWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextareaWidget,
)

from contas.models import Usuario

from .models import Entrega

# As views devolvem a página inteira; o HTMX (hx-select) troca só o pedaço que mudou.
# Assim tudo também funciona sem JavaScript.


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ["projeto", "data", "horas", "descricao"]
        widgets = {  # mesmos widgets/classes dos formulários do admin (Unfold)
            "projeto": UnfoldAdminSelectWidget(),
            "data": forms.DateInput(attrs={"type": "date", "class": " ".join(INPUT_CLASSES)}, format="%Y-%m-%d"),
            "horas": UnfoldAdminDecimalFieldWidget(),
            "descricao": UnfoldAdminTextareaWidget(attrs={"rows": 2}),
        }

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["projeto"].queryset = usuario.projetos.filter(ativo=True)  # só projetos dos quais é membro
        self.fields["projeto"].empty_label = "Selecione o projeto"

    def clean_horas(self):
        horas = self.cleaned_data["horas"]
        if not 0 < horas <= 24:
            raise forms.ValidationError("Informe entre 0 e 24 horas.")
        return horas


def gestor_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.perfil != Usuario.Perfil.GESTOR:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def _editaveis(usuario):
    return usuario.entregas.exclude(status=Entrega.Status.APROVADA)  # assinada não muda mais


@login_required
def inicio(request):
    """Colaborador: lista, cria e edita as próprias entregas."""
    editando = None
    if request.GET.get("editar"):
        editando = get_object_or_404(_editaveis(request.user), pk=request.GET["editar"])
    form = EntregaForm(request.user, request.POST or None, instance=editando)
    if request.method == "POST" and form.is_valid():
        entrega = form.save(commit=False)
        entrega.colaborador = request.user
        entrega.status = Entrega.Status.PENDENTE  # editar uma recusada reenvia para assinatura
        entrega.registrar_assinatura(None)
        entrega.save()
        messages.success(request, "Entrega atualizada." if editando else "Entrega registrada. Aguardando assinatura.")
        return redirect("inicio")

    entregas = request.user.entregas.select_related("projeto", "assinado_por")
    total = entregas.filter(status=Entrega.Status.APROVADA).aggregate(t=Sum("horas"))["t"] or 0
    return render(request, "horas/inicio.html", {"title": "Minhas entregas", "form": form, "editando": editando,
                                                 "entregas": entregas, "total": total})


@require_POST
@login_required
def entrega_excluir(request, pk):
    get_object_or_404(_editaveis(request.user), pk=pk).delete()
    messages.success(request, "Entrega excluída.")
    return redirect("inicio")


@gestor_required
def assinaturas(request):
    """Gestor: filtra entregas, assina/recusa e vê o total de horas assinadas por colaborador."""
    status = request.GET.get("status", Entrega.Status.PENDENTE)
    colaborador = request.GET.get("colaborador", "")
    entregas = Entrega.objects.exclude(colaborador=request.user).select_related("colaborador", "projeto", "assinado_por")
    if status:
        entregas = entregas.filter(status=status)
    if colaborador:
        entregas = entregas.filter(colaborador_id=colaborador)

    totais = (Usuario.objects.annotate(qtd=Count("entregas"),
                                       total=Sum("entregas__horas", filter=Q(entregas__status=Entrega.Status.APROVADA)))
              .filter(qtd__gt=0).order_by("first_name"))
    return render(request, "horas/assinaturas.html", {
        "title": "Assinaturas", "entregas": entregas, "totais": totais, "status": status, "colaborador": colaborador,
        "status_choices": Entrega.Status.choices,
    })


@require_POST
@gestor_required
def assinar(request, pk, acao):
    novo = {"aprovar": Entrega.Status.APROVADA, "recusar": Entrega.Status.RECUSADA}.get(acao)
    if not novo:
        raise Http404
    entrega = get_object_or_404(Entrega.objects.exclude(colaborador=request.user), pk=pk)
    entrega.status = novo
    entrega.registrar_assinatura(request.user)
    entrega.save()
    messages.success(request, f"Entrega de {entrega.colaborador} {entrega.get_status_display().lower()}.")
    filtro = request.POST.get("status", "")
    filtro = filtro if filtro in Entrega.Status.values else ""
    return redirect(f"{reverse('assinaturas')}?status={filtro}")
