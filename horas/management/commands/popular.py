"""Cria dados de demonstração: python manage.py popular"""
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from contas.models import Usuario
from horas.models import Entrega, Projeto


class Command(BaseCommand):
    def handle(self, *args, **opts):
        def user(username, nome, perfil, **extra):
            u, _ = Usuario.objects.get_or_create(username=username, defaults=dict(first_name=nome, perfil=perfil, **extra))
            u.set_password("senha123")
            u.save()
            return u

        user("admin", "Administrador", Usuario.Perfil.GESTOR, is_staff=True, is_superuser=True)
        ana = user("ana", "Ana", Usuario.Perfil.GESTOR)
        carla = user("carla", "Carla", Usuario.Perfil.COLABORADOR)
        diego = user("diego", "Diego", Usuario.Perfil.COLABORADOR)

        site, _ = Projeto.objects.get_or_create(nome="Site institucional", defaults={"cliente": "ACME"})
        app, _ = Projeto.objects.get_or_create(nome="App mobile", defaults={"cliente": "ACME"})
        site.membros.add(carla, diego)
        app.membros.add(carla)

        if not Entrega.objects.exists():
            status = [Entrega.Status.APROVADA, Entrega.Status.APROVADA, Entrega.Status.RECUSADA, Entrega.Status.PENDENTE]
            for colab, projetos in [(carla, [site, app]), (diego, [site])]:
                for i in range(8):
                    st = status[i % 4]
                    Entrega.objects.create(
                        colaborador=colab, projeto=projetos[i % len(projetos)],
                        data=date(2026, 10, 1) + timedelta(days=i * 4),
                        descricao=f"Entrega {i + 1}", horas=Decimal(2 + i % 5), status=st,
                        assinado_por=ana if st != Entrega.Status.PENDENTE else None,
                        assinado_em=timezone.now() if st != Entrega.Status.PENDENTE else None,
                    )
        self.stdout.write(self.style.SUCCESS("Pronto. Usuários admin, ana (gestora), carla e diego; senha: senha123"))
