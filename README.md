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
4 tabelas: `contas_usuario`, `horas_projeto`, `horas_projeto_membros` (ligação N:N) e `horas_entrega`.
Fonte do diagrama: [`docs/diagrama.mmd`](docs/diagrama.mmd) · imagem: [`docs/diagrama.png`](docs/diagrama.png).

```mermaid
erDiagram
    contas_usuario ||--o{ horas_entrega : "registra (colaborador)"
    contas_usuario |o--o{ horas_entrega : "assina (gestor)"
    horas_projeto ||--o{ horas_entrega : "recebe"
    contas_usuario ||--o{ horas_projeto_membros : "participa"
    horas_projeto ||--o{ horas_projeto_membros : "tem membros"

    contas_usuario {
        bigint id PK
        varchar(150) username UK "login"
        varchar(128) password "hash"
        varchar(150) first_name
        varchar(150) last_name
        varchar(254) email
        varchar(20) perfil "COLABORADOR | GESTOR"
        bool is_active
        bool is_staff "acesso ao admin"
        bool is_superuser
        datetime date_joined
        datetime last_login
    }

    horas_projeto {
        bigint id PK
        varchar(120) nome
        varchar(120) cliente
        bool ativo
    }

    horas_projeto_membros {
        bigint id PK
        bigint projeto_id FK "-> horas_projeto"
        bigint usuario_id FK "-> contas_usuario"
    }

    horas_entrega {
        bigint id PK
        bigint colaborador_id FK "-> contas_usuario (CASCADE)"
        bigint projeto_id FK "-> horas_projeto (PROTECT)"
        date data
        text descricao
        decimal(5_2) horas
        varchar(20) status "PENDENTE | APROVADA | RECUSADA"
        bigint assinado_por_id FK "-> contas_usuario (SET NULL), nulo"
        datetime assinado_em "nulo"
    }
```

| Relacionamento | Cardinalidade | Regra |
|---|---|---|
| Usuário → Entrega (colaborador) | 1:N | apagar usuário apaga suas entregas (CASCADE) |
| Usuário → Entrega (assinado_por) | 0..1:N | apagar gestor mantém a entrega, campo vira nulo (SET NULL) |
| Projeto → Entrega | 1:N | não é possível apagar projeto com entregas (PROTECT) |
| Usuário ↔ Projeto | N:N | via `horas_projeto_membros` |
