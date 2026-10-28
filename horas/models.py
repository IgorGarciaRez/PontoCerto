from django.conf import settings
from django.db import models


class Projeto(models.Model):
    nome = models.CharField(max_length=120)
    cliente = models.CharField(max_length=120, blank=True)
    membros = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="projetos")
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

