# PontoCerto

Sistema para entrega, assinatura e contabilização de horas trabalhadas pelos colaboradores de uma empresa.

## Integrantes
- Igor Garcia Rezende
- Mateus Milani

## Descrição
O colaborador registra suas entregas (projeto, data, descrição e horas trabalhadas).
O gestor assina (aprova) ou recusa cada entrega. O total de horas de cada colaborador considera apenas as entregas assinadas.

## Tecnologias
- Python 3 / Django 6
- SQLite (banco relacional)
- Django Admin com tema Unfold (tema claro/escuro, filtros)
- htmx

## Instalação
```bash
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py popular       # dados de demonstração
```

## Execução
```bash
python manage.py runserver
```
Acesse http://127.0.0.1:8000/admin/ — usuários de teste: `admin`, `ana` (gestora), `carla` e `diego` (colaboradores), todos com senha `senha123`.

## Principais funcionalidades
- Perfis: Gestor e Colaborador
- CRUD de usuários, projetos e entregas
- Assinatura (aprovação) das entregas pelo gestor
- Contabilização das horas assinadas por colaborador
- Painel administrativo com filtros por perfil, status, colaborador, projeto, data e horas

## Estrutura do projeto
```
config/   configurações e URLs do projeto
contas/   usuários e perfis
horas/    projetos e entregas
          management/commands/popular.py  dados de demonstração
locale/   tradução pt-BR dos textos do tema Unfold
```

## Modelagem
```
Usuario N─N Projeto        (membros do projeto)
Usuario 1─N Entrega N─1 Projeto
Usuario 1─N Entrega        (gestor que assinou)
```
