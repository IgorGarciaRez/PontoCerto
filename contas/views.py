from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from unfold.widgets import INPUT_CLASSES

from .models import Usuario


def _estilo_unfold(form):
    """Aplica nos campos as mesmas classes que o Unfold usa nos inputs do admin."""
    for campo in form.fields.values():
        campo.widget.attrs["class"] = " ".join(INPUT_CLASSES)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _estilo_unfold(self)


class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Usuario
        fields = ["username", "first_name", "email"]  # perfil fica COLABORADOR; só o admin promove a gestor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _estilo_unfold(self)


def cadastro(request):
    form = CadastroForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())
        return redirect("inicio")
    return render(request, "registration/cadastro.html", {"form": form})
