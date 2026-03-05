# Sistema de Agendamento Online (Django 5+)

Aplicação web completa para gerenciamento de agendamentos online, com perfis de **Cliente** e **Administrador**, sem sistema de pagamento.

## Requisitos

- Python 3.12+ (ou compatível com Django 5)
- `pip`

## Como executar

1. Entrar na pasta do projeto:

```bash
cd sistema_agendamento
```

2. Criar e ativar ambiente virtual (opcional, recomendado):

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

3. Instalar dependências:

```bash
pip install django>=5,<6
```

4. Criar migrações e migrar banco SQLite:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Criar usuário administrador (opcional):

```bash
python manage.py createsuperuser
```

6. Rodar servidor:

```bash
python manage.py runserver
```

Acesse: `http://127.0.0.1:8000/`

## Funcionalidades implementadas

- Autenticação: cadastro, login, logout e recuperação de senha.
- Perfis de usuário: Cliente e Administrador.
- Cliente:
  - Criar agendamento (serviço, data e horário).
  - Visualizar listagem paginada dos próprios agendamentos.
  - Editar agendamento apenas se estiver **Pendente**.
  - Cancelar com antecedência mínima configurável em `settings.py` (`CANCELLATION_MIN_HOURS`).
- Administrador:
  - CRUD de Serviços.
  - CRUD de Horários disponíveis.
  - Dashboard com indicadores simples.
  - Listagem paginada de todos os agendamentos.
  - Filtro por data e busca por nome/username do cliente.
  - Alteração de status (Pendente, Confirmado, Cancelado, Concluído).
- Regras:
  - Bloqueio de datas passadas.
  - Bloqueio de conflito de horário para mesma data.
  - Feedback visual com Django Messages.

## Estrutura de pastas

```text
sistema_agendamento/
  manage.py
  db.sqlite3 (gerado após migrate)
  sistema_agendamento/
    __init__.py
    settings.py
    urls.py
    asgi.py
    wsgi.py
  agendamentos/
    __init__.py
    apps.py
    admin.py
    forms.py
    models.py
    urls.py
    views.py
    migrations/
      __init__.py
  templates/
    base.html
    registration/
      login.html
      register.html
      password_reset_form.html
      password_reset_done.html
      password_reset_confirm.html
      password_reset_complete.html
    agendamentos/
      home.html
      dashboard_admin.html
      servico_list.html
      servico_form.html
      horario_list.html
      horario_form.html
      agendamento_cliente_list.html
      agendamento_form.html
      agendamento_admin_list.html
      agendamento_status_form.html
      confirm_delete.html
      pagination.html
  static/
    css/
      styles.css
```

## Observações técnicas

- A recuperação de senha usa backend de e-mail em console (`EMAIL_BACKEND = console`), ideal para desenvolvimento.
- O tipo de usuário é salvo no model `Perfil` (OneToOne com `User`).
- O layout foi feito com Bootstrap 5 e CSS customizado responsivo.


-  projeto feito em vibe code