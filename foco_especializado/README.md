# 3 Coisas de Hoje - MVP

App Django de apoio para organização diária com foco em poucas tarefas importantes, desenvolvido especialmente para pessoas com TDAH ou dificuldades de atenção.

## 📋 Sobre o Projeto

Este é um MVP (Minimum Viable Product) de um aplicativo web focado em ajudar pessoas a organizar o dia com poucas tarefas importantes (até 3 por dia). O app trabalha com princípios de externalização de funções executivas, transformando intenções vagas em ações claras e acionáveis.

**⚠️ IMPORTANTE:** Este app é uma ferramenta de apoio e NÃO substitui avaliação profissional, diagnóstico ou tratamento médico/psicológico.

## 🚀 Como Rodar o Projeto Localmente

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Navegue até o diretório do projeto:**
   ```bash
   cd foco_especializado
   ```

2. **Crie um ambiente virtual (recomendado):**
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual:**
   
   **Windows (PowerShell):**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   **Windows (CMD):**
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Crie um arquivo `.env` (opcional em DEV):**
   - Copie `ENV_EXAMPLE.txt` para `.env` e ajuste se necessário.
   - Em DEV, se você não preencher variáveis de MySQL, o SQLite será usado automaticamente.

6. **Executar em DEV (com settings de dev):**
   ```bash
   set DJANGO_SETTINGS_MODULE=rastreio_logistico.settings.dev
   python manage.py migrate
   python manage.py runserver
   ```
   - Alternativa Linux/Mac:
   ```bash
   export DJANGO_SETTINGS_MODULE=rastreio_logistico.settings.dev
   python manage.py migrate
   python manage.py runserver
   ```

5. **Execute as migrações do banco de dados:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Crie um superusuário (opcional, para acessar o admin):**
   ```bash
   python manage.py createsuperuser
   ```
   Siga as instruções para criar um usuário administrador.

7. **Inicie o servidor de desenvolvimento:**
   ```bash
   python manage.py runserver
   ```

8. **Acesse o app no navegador:**
   - App principal: http://127.0.0.1:8000/
   - Admin Django: http://127.0.0.1:8000/admin/
    - Healthcheck: http://127.0.0.1:8000/healthz/

## 🏗️ Deploy de Testes/Produção (MySQL + ENV)

1. Defina as variáveis de ambiente de produção:
   - `DJANGO_SETTINGS_MODULE=rastreio_logistico.settings.prod`
   - `SECRET_KEY=<sua-chave-secreta>`
   - `ALLOWED_HOSTS=<seus-hosts>`
   - `CSRF_TRUSTED_ORIGINS=<origens-csrf>`
   - `CORS_ALLOWED_ORIGINS=<origens-cors>`
   - `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`
   - Opcional: `USE_PYMYSQL=1` (se preferir PyMySQL ao invés de mysqlclient)

2. Comandos úteis (deploy):
   ```bash
   python manage.py check --deploy
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

3. Em produção, os caminhos de estáticos/mídia são:
   - `STATIC_ROOT=/app/staticfiles`
   - `MEDIA_ROOT=/app/media`

## 📁 Estrutura do Projeto

```
foco_especializado/
├── core/                          # App principal
│   ├── models.py                  # Modelos DayPlan e Task
│   ├── views.py                   # Views do app
│   ├── urls.py                    # URLs do app
│   ├── forms.py                   # Formulários
│   ├── ai_service.py              # Stub de serviço de IA
│   ├── admin.py                   # Configuração do admin
│   ├── templates/core/            # Templates HTML
│   │   ├── base.html              # Template base
│   │   ├── home.html              # Página principal (hoje)
│   │   ├── criar_plano_dia.html   # Criação de tarefas
│   │   ├── historico.html         # Histórico de dias
│   │   ├── revisao_dia.html       # Revisão do dia
│   │   ├── sobre.html             # Página sobre
│   │   └── ...
│   └── static/                     # Arquivos estáticos
│       ├── manifest.json           # Manifest PWA
│       └── service-worker.js       # Service Worker PWA
├── foco_especializado/            # Configurações do projeto
│   ├── settings.py                 # Configurações Django
│   ├── urls.py                     # URLs principais
│   └── ...
├── rastreio_logistico/            # Novo pacote de settings (DEV/PROD)
│   └── settings/
│       ├── __init__.py            # Exporta dev por padrão
│       ├── base.py                # Base com ENV + fallback SQLite
│       ├── dev.py                 # Carrega .env, libera CORS/CSRF localhost
│       └── prod.py                # MySQL/estáticos/proxy/segurança
├── manage.py                       # Script de gerenciamento Django
├── requirements.txt                # Dependências Python
└── README.md                       # Este arquivo
```

## 🎯 Funcionalidades do MVP

### 1. Página do Dia de Hoje
- Mostra a data atual
- Lista até 3 tarefas importantes do dia
- Permite criar, editar, marcar como concluída e deletar tarefas
- Mostra resumo de progresso e streak (dias consecutivos)

### 2. Criação Guiada de Tarefas
- Fluxo passo a passo para criar tarefas
- Sugestão de tarefas usando IA (stub implementado)
- Campo para "intenção vaga" que é quebrada em tarefas específicas

### 3. Histórico
- Lista de dias anteriores com progresso
- Visualização de detalhes de cada dia (somente leitura)

### 4. Revisão do Dia
- Permite registrar motivo de não conclusão
- Campo para reflexão/comentário sobre o dia

### 5. Página Sobre
- Explicação do app e seus princípios
- Avisos importantes sobre não ser diagnóstico/tratamento

## 🔧 Arquivos Principais e Suas Funções

### Models (`core/models.py`)
- **DayPlan**: Representa um plano do dia com tarefas e informações de revisão
- **Task**: Representa uma tarefa individual (até 3 por dia)

### Views (`core/views.py`)
- `home`: Página principal com o plano do dia de hoje
- `criar_plano_dia`: Fluxo de criação de tarefas
- `editar_tarefa`, `marcar_tarefa`, `deletar_tarefa`: Gerenciamento de tarefas
- `historico`, `detalhes_dia`: Visualização de histórico
- `revisao_dia`: Revisão e reflexão do dia
- `sugerir_tarefas_ia`: Endpoint AJAX para sugestões de IA
- `sobre`: Página informativa
- `registrar_usuario`: Registro de novos usuários

### AI Service (`core/ai_service.py`)
- **Stub de IA**: Função `sugerir_tarefas_por_ia()` que retorna sugestões baseadas em palavras-chave
- **Futuro**: Substituir por chamada real a API de modelo de linguagem (OpenAI, Anthropic, etc.)

### PWA
- **manifest.json**: Configuração do Progressive Web App
- **service-worker.js**: Service Worker básico (esqueleto para futuras melhorias)

## 🔮 Melhorias Futuras

### Curto Prazo
- Substituir stub de IA por integração real com API
- Adicionar ícones reais para o PWA
- Melhorar cache offline do service worker

### Médio Prazo
- Relatórios e análises de padrões
- Notificações e lembretes
- Personalização avançada
- Exportação de dados

### Longo Prazo
- App mobile nativo
- Sincronização entre dispositivos
- Colaboração/compartilhamento
- Integração com calendários

## ⚠️ Notas Importantes

1. **Autenticação**: O app usa o sistema de usuários padrão do Django. Cada usuário tem seus próprios planos e tarefas.

2. **Banco de Dados**: Por padrão, usa SQLite (desenvolvimento). Para produção, configure PostgreSQL ou MySQL.
   - Fallback automático para SQLite se `MYSQL_HOST` não estiver definido.
   - MySQL usa `utf8mb4` e `STRICT_TRANS_TABLES`.

3. **PWA**: Os arquivos PWA estão implementados como esqueleto. Para funcionalidade completa offline, será necessário expandir o service worker.

4. **IA**: A funcionalidade de sugestão de tarefas usa um stub local. Para usar IA real:
   - Adicione variável de ambiente para API key
   - Instale biblioteca apropriada (ex.: `openai`, `anthropic`)
   - Substitua a função em `ai_service.py`

5. **Segurança**: Este é um MVP para testes locais. Para produção:
   - Configure `SECRET_KEY` adequadamente
   - Desative `DEBUG`
   - Configure `ALLOWED_HOSTS`
   - Use HTTPS
   - Implemente validações e sanitizações adicionais

## 📝 Licença

Este projeto é um MVP para fins educacionais e de teste.

## 🤝 Contribuindo

Este é um projeto MVP. Sugestões e melhorias são bem-vindas!

---

**Desenvolvido com Django 5.2.8**

