# 📋 Instruções de Instalação e Uso - MVP "3 Coisas de Hoje"

## 🚀 Instalação Rápida

### 1. Criar e Ativar Ambiente Virtual

**Windows (PowerShell):**
```powershell
cd foco_especializado
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
cd foco_especializado
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
cd foco_especializado
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Criar Superusuário (Opcional)

```bash
python manage.py createsuperuser
```

Siga as instruções para criar um usuário administrador (útil para acessar `/admin/`).

### 5. Iniciar Servidor

```bash
python manage.py runserver
```

### 6. Acessar o App

- **App principal:** http://127.0.0.1:8000/
- **Admin Django:** http://127.0.0.1:8000/admin/

## 📝 Primeiros Passos

1. **Criar uma conta:**
   - Acesse http://127.0.0.1:8000/registrar/
   - Crie um usuário e senha

2. **Fazer login:**
   - Acesse http://127.0.0.1:8000/login/
   - Entre com suas credenciais

3. **Criar suas primeiras tarefas:**
   - Você será redirecionado para criar tarefas do dia
   - Siga o fluxo guiado (primeira, segunda, terceira tarefa)
   - Ou use a sugestão de IA para quebrar uma intenção vaga

4. **Gerenciar tarefas:**
   - Marque tarefas como concluídas
   - Edite ou delete tarefas conforme necessário
   - Faça a revisão do dia ao final

## 🗂️ Estrutura de Arquivos Criados

### App Core (`core/`)

- **models.py**: Modelos `DayPlan` e `Task`
- **views.py**: Todas as views do app (home, criar tarefas, histórico, etc.)
- **urls.py**: Rotas do app
- **forms.py**: Formulários (TaskForm, RevisaoDiaForm)
- **ai_service.py**: Stub de serviço de IA para sugestões
- **admin.py**: Configuração do admin Django

### Templates (`core/templates/core/`)

- **base.html**: Template base com navbar e footer
- **home.html**: Página principal (hoje)
- **criar_plano_dia.html**: Criação guiada de tarefas
- **editar_tarefa.html**: Edição de tarefa
- **deletar_tarefa.html**: Confirmação de deleção
- **historico.html**: Lista de dias anteriores
- **detalhes_dia.html**: Detalhes de um dia específico
- **revisao_dia.html**: Revisão e reflexão do dia
- **sobre.html**: Página informativa
- **login.html**: Página de login
- **registrar.html**: Página de registro

### Arquivos PWA (`core/static/`)

- **manifest.json**: Configuração do Progressive Web App
- **service-worker.js**: Service Worker básico (esqueleto)

### Configurações do Projeto

- **settings.py**: Configurado com app `core`, português do Brasil, timezone de São Paulo
- **urls.py**: Rotas principais incluindo app core e autenticação
- **requirements.txt**: Dependências (Django 5.2.8+)

## ⚙️ Funcionalidades Implementadas

✅ Página do dia de hoje com até 3 tarefas  
✅ Criação guiada de tarefas (fluxo passo a passo)  
✅ Edição, marcação e deleção de tarefas  
✅ Histórico de dias anteriores  
✅ Visualização de detalhes de um dia  
✅ Revisão do dia (motivo de não conclusão + reflexão)  
✅ Sugestão de tarefas por IA (stub implementado)  
✅ Cálculo de streak (dias consecutivos)  
✅ Autenticação de usuários  
✅ PWA básico (manifest + service worker)  
✅ Interface responsiva com Tailwind CSS  

## 🔧 Pontos de Atenção para Futuras Melhorias

### 1. Integração Real de IA
**Arquivo:** `core/ai_service.py`
- Substituir função `sugerir_tarefas_por_ia()` por chamada real a API
- Adicionar variável de ambiente para API key
- Instalar biblioteca apropriada (ex.: `openai`, `anthropic`)

### 2. Ícones PWA
**Arquivo:** `core/static/`
- Criar ícones reais (192x192 e 512x512)
- Adicionar ao `manifest.json`
- Descomentar referência no `base.html`

### 3. Service Worker Offline
**Arquivo:** `core/static/service-worker.js`
- Implementar cache robusto de assets
- Adicionar estratégia de cache offline
- Implementar sincronização em background

### 4. Segurança para Produção
**Arquivo:** `foco_especializado/settings.py`
- Configurar `SECRET_KEY` via variável de ambiente
- Desativar `DEBUG = False`
- Configurar `ALLOWED_HOSTS`
- Usar HTTPS
- Configurar banco de dados de produção (PostgreSQL/MySQL)

## 🐛 Solução de Problemas

### Erro: "No module named 'django'"
- Certifique-se de que o ambiente virtual está ativado
- Execute `pip install -r requirements.txt`

### Erro: "ModuleNotFoundError: No module named 'core'"
- Verifique se `core` está em `INSTALLED_APPS` no `settings.py`
- Execute `python manage.py makemigrations` e `python manage.py migrate`

### Erro ao acessar `/manifest.json` ou `/service-worker.js`
- Verifique se os arquivos existem em `core/static/`
- Verifique se as rotas estão configuradas em `core/urls.py`

### Página em branco ou erro 500
- Verifique os logs do servidor Django
- Certifique-se de que as migrações foram executadas
- Verifique se há erros de sintaxe nos templates

## 📚 Recursos Adicionais

- **Documentação Django:** https://docs.djangoproject.com/
- **Tailwind CSS:** https://tailwindcss.com/
- **PWA Guide:** https://web.dev/progressive-web-apps/

---

**MVP criado com sucesso! 🎉**

Para dúvidas ou problemas, consulte o `README.md` ou os comentários no código.

