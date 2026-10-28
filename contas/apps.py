from django.apps import AppConfig
from django.db.models.signals import post_migrate

ACOES = {"add": "adicionar", "change": "alterar", "delete": "remover", "view": "visualizar"}


def traduzir_permissoes(**kwargs):
    """O Django grava os nomes das permissões em inglês ("Can add ..."); renomeia para pt-BR."""
    from django.conf import settings
    from django.contrib.auth.models import Permission
    from django.utils import translation

    with translation.override(settings.LANGUAGE_CODE):  # o migrate roda em inglês
        for p in Permission.objects.select_related("content_type"):
            acao = p.codename.split("_", 1)[0]
            modelo = p.content_type.model_class()
            if acao in ACOES and modelo:
                p.name = f"Pode {ACOES[acao]} {modelo._meta.verbose_name}"
                p.save(update_fields=["name"])


class ContasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "contas"
    verbose_name = "Contas"

    def ready(self):
        post_migrate.connect(traduzir_permissoes, sender=self)
