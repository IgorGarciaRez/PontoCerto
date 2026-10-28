from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Perfil(models.TextChoices):
        COLABORADOR = "COLABORADOR", "Colaborador"
        GESTOR = "GESTOR", "Gestor"

    perfil = models.CharField(max_length=20, choices=Perfil.choices, default=Perfil.COLABORADOR)

    class Meta:
        verbose_name = "usuário"

    def __str__(self):
        return self.get_full_name() or self.username
