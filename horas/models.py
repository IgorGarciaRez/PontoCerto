from django.conf import settings
from django.db import models
from django.utils import timezone


class Projeto(models.Model):
    nome = models.CharField(max_length=120)
    cliente = models.CharField(max_length=120, blank=True)
    membros = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="projetos")
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Entrega(models.Model):
    """O colaborador registra; o gestor assina (aprova) ou recusa. Só aprovadas contam nas horas."""

    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Aguardando assinatura"
        APROVADA = "APROVADA", "Assinada"
        RECUSADA = "RECUSADA", "Recusada"

    colaborador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="entregas")
    projeto = models.ForeignKey(Projeto, on_delete=models.PROTECT, related_name="entregas")
    data = models.DateField()
    descricao = models.TextField("descrição")
    horas = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    assinado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="entregas_assinadas", verbose_name="assinado por",
    )
    assinado_em = models.DateTimeField("assinado em", null=True, blank=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.data:%d/%m/%Y} - {self.projeto} ({self.horas}h)"

    def registrar_assinatura(self, usuario):
        """Chamar quando o status mudar: assinada/recusada guarda quem e quando; pendente limpa."""
        if self.status == self.Status.PENDENTE:
            self.assinado_por, self.assinado_em = None, None
        else:
            self.assinado_por, self.assinado_em = usuario, timezone.now()
