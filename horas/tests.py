from datetime import date

from django.test import TestCase

from contas.models import Usuario

from .models import Entrega, Projeto


class FluxoTest(TestCase):
    def setUp(self):
        self.gestor = Usuario.objects.create_user("ana", password="x", perfil=Usuario.Perfil.GESTOR)
        self.carla = Usuario.objects.create_user("carla", password="x")
        self.diego = Usuario.objects.create_user("diego", password="x")
        self.proj = Projeto.objects.create(nome="Site")
        self.proj.membros.add(self.carla)
        self.outro = Projeto.objects.create(nome="Secreto")  # carla não é membro

    def nova(self, **kw):
        dados = {"projeto": self.proj.pk, "data": "2026-11-10", "horas": "4", "descricao": "Tela X"} | kw
        return self.client.post("/", dados)

    def test_login_obrigatorio(self):
        self.assertRedirects(self.client.get("/"), "/contas/login/?next=/")
        self.assertRedirects(self.client.get("/assinaturas/"), "/contas/login/?next=/assinaturas/")

    def test_cadastro_entra_como_colaborador(self):
        r = self.client.post("/contas/cadastro/", {"username": "novo", "first_name": "Novo", "email": "n@x.com",
                                                    "password1": "Xy9!abcdef", "password2": "Xy9!abcdef",
                                                    "perfil": "GESTOR"})  # tentativa de virar gestor é ignorada
        self.assertRedirects(r, "/")
        self.assertEqual(Usuario.objects.get(username="novo").perfil, Usuario.Perfil.COLABORADOR)

    def test_crud_colaborador(self):
        self.client.force_login(self.carla)
        self.assertRedirects(self.nova(), "/")
        e = Entrega.objects.get()
        self.assertEqual((e.colaborador, e.status), (self.carla, Entrega.Status.PENDENTE))

        self.client.post(f"/?editar={e.pk}", {"projeto": self.proj.pk, "data": "2026-11-10", "horas": "6", "descricao": "Y"})
        e.refresh_from_db()
        self.assertEqual(e.horas, 6)

        self.client.post(f"/entregas/{e.pk}/excluir/")
        self.assertFalse(Entrega.objects.exists())

    def test_validacoes(self):
        self.client.force_login(self.carla)
        self.assertContains(self.nova(horas="30"), "entre 0 e 24")
        self.assertEqual(self.nova(projeto=self.outro.pk).status_code, 200)  # projeto de que não é membro: inválido
        self.assertFalse(Entrega.objects.exists())

    def test_nao_mexe_em_entrega_alheia_nem_assinada(self):
        alheia = Entrega.objects.create(colaborador=self.diego, projeto=self.proj, data=date.today(), descricao="d", horas=1)
        assinada = Entrega.objects.create(colaborador=self.carla, projeto=self.proj, data=date.today(), descricao="a",
                                          horas=1, status=Entrega.Status.APROVADA)
        self.client.force_login(self.carla)
        for e in (alheia, assinada):
            self.assertEqual(self.client.post(f"/entregas/{e.pk}/excluir/").status_code, 404)
            self.assertEqual(self.client.get(f"/?editar={e.pk}").status_code, 404)
        self.assertEqual(Entrega.objects.count(), 2)

    def test_colaborador_nao_acessa_assinaturas(self):
        self.client.force_login(self.carla)
        self.assertEqual(self.client.get("/assinaturas/").status_code, 403)

    def test_gestor_assina_e_total_conta_so_assinadas(self):
        e1 = Entrega.objects.create(colaborador=self.carla, projeto=self.proj, data=date.today(), descricao="1", horas=3)
        Entrega.objects.create(colaborador=self.carla, projeto=self.proj, data=date.today(), descricao="2", horas=5)
        self.client.force_login(self.gestor)
        self.assertRedirects(self.client.post(f"/assinaturas/{e1.pk}/aprovar/", {"status": "PENDENTE"}),
                             "/assinaturas/?status=PENDENTE")
        e1.refresh_from_db()
        self.assertEqual((e1.status, e1.assinado_por), (Entrega.Status.APROVADA, self.gestor))
        self.assertEqual(self.client.get("/assinaturas/").context["totais"].get(pk=self.carla.pk).total, 3)
        self.assertEqual(self.client.post(f"/assinaturas/{e1.pk}/xpto/").status_code, 404)

    def test_editar_recusada_reenvia(self):
        e = Entrega.objects.create(colaborador=self.carla, projeto=self.proj, data=date.today(), descricao="r",
                                   horas=1, status=Entrega.Status.RECUSADA, assinado_por=self.gestor)
        self.client.force_login(self.carla)
        self.client.post(f"/?editar={e.pk}", {"projeto": self.proj.pk, "data": "2026-11-10", "horas": "2", "descricao": "r2"})
        e.refresh_from_db()
        self.assertEqual((e.status, e.assinado_por), (Entrega.Status.PENDENTE, None))

    def test_htmx_carrega_na_pagina(self):
        self.client.force_login(self.carla)
        html = self.client.get("/").content.decode()
        self.assertIn("unfold/js/htmx/htmx.js", html)
        self.assertIn('hx-select="#painel"', html)
        self.assertIn("unfold/css/styles.css", html)  # mesmo CSS do admin
        self.assertNotIn("pico", html)

    def test_login_e_cadastro_no_estilo_unfold(self):
        for url in ("/contas/login/", "/contas/cadastro/"):
            html = self.client.get(url).content.decode()
            self.assertIn("unfold/css/styles.css", html)
            self.assertIn("rounded-default", html)  # inputs com as classes do Unfold
