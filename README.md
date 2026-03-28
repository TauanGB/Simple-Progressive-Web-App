# Simple Progressive Web App (Django)

Projeto **básico e funcional** de **Progressive Web App (PWA)** com backend **Django**. O domínio da aplicação é uma **lista diária de tarefas** (até três por dia): suficiente para um CRUD e fluxos reais, enquanto o foco do repositório é demonstrar **manifest**, **service worker**, **instalação** e **experiência mobile/offline** coerentes com boas práticas de PWA.

## O que este repositório pretende mostrar

- **PWA**: `manifest.json`, `service-worker.js`, tema, ícones, atalhos e banner de instalação.
- **Django**: autenticação, modelos de plano do dia e tarefas, templates e deploy (incl. Docker/Railway).
- **Contexto de tarefas**: criar/editar/concluir tarefas, histórico e revisão do dia — cenário simples para exercitar o app como “app instalável”, não um produto terapêutico ou de saúde.

## ⚙️ Deploy & ENV (DEV/PROD/Railway)

### Variáveis (.env)

Use `env.example` na raiz como base.

### DEV (SQLite automático)

Na raiz do repositório (onde está `manage.py`):

```bash
export DJANGO_SETTINGS_MODULE=foco_especializado.settings.dev
python manage.py runserver
```

No Windows (PowerShell): `$env:DJANGO_SETTINGS_MODULE="foco_especializado.settings.dev"` antes de `runserver`.

### HTTPS no desenvolvimento (evita erro “only supports HTTP”)

O `runserver` padrão **só fala HTTP**. Se você abrir `https://127.0.0.1:8000`, o navegador manda TLS e o servidor responde com erro (`Bad request version` / “only supports HTTP”).

**Opção A — sem HTTPS:** use sempre **`http://127.0.0.1:8000`** ou **`http://localhost:8000`**. Para PWA, `localhost` já é [contexto seguro](https://developer.mozilla.org/docs/Web/Security/Secure_Contexts) no navegador.

**Opção B — HTTPS local:** instale dependências de dev e use o comando que sobe o Werkzeug com certificado autoassinado em `./ssl/`:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
export DJANGO_SETTINGS_MODULE=foco_especializado.settings.dev
python manage.py runserver_https
```

PowerShell:

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
$env:DJANGO_SETTINGS_MODULE="foco_especializado.settings.dev"
python manage.py runserver_https
```

Abra **`https://localhost:8000`** (o cert é para `localhost`; em `127.0.0.1` o aviso de certificado pode ser pior). Na primeira execução os arquivos `ssl/dev.crt` e `ssl/dev.key` são criados.

### PROD local (Docker)

```bash
docker build -t sistemaeg3 .
docker run -p 8000:8000 --env-file ./env.example sistemaeg3
```

### Railway

- Deploy por repo (Dockerfile detectado)
- Defina ENV obrigatórias:
  - `DJANGO_SETTINGS_MODULE=foco_especializado.settings.prod`
  - `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`
  - MySQL: `MYSQL_HOST`, `MYSQL_PORT=3306`, `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`, `USE_PYMYSQL=1`
- Health path: `/healthz`

## 🚀 Como rodar localmente

### Pré-requisitos

- Python 3.8 ou superior
- pip

### Passos

1. Na raiz do repositório (onde está `manage.py`), crie e ative um ambiente virtual.
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. Opcional: `python manage.py createsuperuser`
5. `python manage.py runserver`
6. Abra http://127.0.0.1:8000/ — o admin fica em `/admin/`.

Para desenvolvimento com settings explícitos, use `DJANGO_SETTINGS_MODULE=foco_especializado.settings.dev` como acima.

## 📁 Estrutura (resumo)

```
foco_especializado/     # Projeto Django (URLs, settings)
core/                   # App: tarefas, templates, PWA estático
  static/
    manifest.json
    service-worker.js
manage.py
requirements.txt
```

## Funcionalidades (app de tarefas)

- **Hoje**: até três tarefas por dia, progresso e consistência (streak).
- **Criação guiada** de tarefas.
- **Histórico** e **detalhes** de dias anteriores.
- **Revisão do dia** (reflexão / motivos de não conclusão).
- **PWA**: instalar na tela inicial, assets em cache, página offline.

## Arquivos PWA principais

| Arquivo | Papel |
|--------|--------|
| `core/static/manifest.json` | Nome, ícones, `display`, atalhos |
| `core/static/service-worker.js` | Cache e fallback offline |
| `core/templates/core/base.html` | Manifest, meta tags, banner de instalação |
| `core/static/js/pwa-install.js` | Fluxo de instalação |

## Notas

- **Produção**: `DEBUG=False`, `SECRET_KEY` forte, HTTPS, `ALLOWED_HOSTS` e banco adequado (PostgreSQL/MySQL).

## Licença

Projeto educativo / demonstrativo; use e adapte conforme a licença do repositório.

---

**Stack:** Django 5.x · PWA (Web App Manifest + Service Worker)
