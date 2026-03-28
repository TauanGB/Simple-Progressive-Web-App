# Instruções de instalação e uso

Repositório focado em um **PWA funcional** com **Django**, usando um **fluxo simples de tarefas diárias** como contexto de negócio.

## Instalação rápida

### 1. Ambiente virtual

Na **raiz do repositório** (onde está `manage.py`):

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Dependências

```bash
pip install -r requirements.txt
```

### 3. Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 5. Servidor

**HTTP (padrão):**

```bash
python manage.py runserver
```

- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

**Se aparecer “only supports HTTP” / `Bad request version`:** você está usando **`https://`** no navegador com o servidor HTTP. Use **`http://`** ou suba HTTPS de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Com `requirements.txt` já instalado:

```bash
pip install -r requirements-dev.txt
export DJANGO_SETTINGS_MODULE=foco_especializado.settings.dev
python manage.py runserver_https
```

No PowerShell, troque a linha `export` por `$env:DJANGO_SETTINGS_MODULE="foco_especializado.settings.dev"`.

Depois acesse **https://localhost:8000** (veja o `README.md`).

## Primeiros passos

1. Registrar em `/registrar/` e fazer login em `/login/`.
2. Criar as tarefas do dia pelo fluxo guiado.
3. No celular ou no Chrome, testar **Instalar app** / **Adicionar à tela inicial** para validar o PWA.

## Estrutura útil

- `core/models.py` — `DayPlan`, `Task`
- `core/static/manifest.json` e `service-worker.js` — PWA
- `foco_especializado/settings/` — ambientes dev/prod

## PWA e melhorias

- Ícones: veja `core/static/README_ICONES.md` se precisar gerar ou ajustar assets.
- Service worker: evoluir cache e estratégias conforme `core/static/service-worker.js`.

## Problemas comuns

- **No module named 'django'**: ative o venv e rode `pip install -r requirements.txt`.
- **Manifest/service worker**: confira rotas em `core/urls.py` e a aba Application do DevTools.

Para visão geral do objetivo do projeto, use o `README.md`.
