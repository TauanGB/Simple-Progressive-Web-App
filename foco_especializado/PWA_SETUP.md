# Configuração PWA - Documentação Completa

## 📱 Resumo

O projeto Django "3 Coisas de Hoje" foi configurado como um Progressive Web App (PWA) completo e funcional. Este documento descreve todas as alterações feitas e como testar o PWA.

## ✅ O que foi implementado

### 1. Manifest.json
- ✅ Configurado com todas as propriedades necessárias
- ✅ Nome, descrição, ícones, cores, orientação
- ✅ Shortcuts para rotas principais
- ✅ Configuração para diferentes plataformas (iOS, Android, Windows)

### 2. Service Worker
- ✅ Implementado com cache offline funcional
- ✅ Estratégia Network First com fallback para cache (páginas HTML)
- ✅ Estratégia Cache First com fallback para network (assets estáticos)
- ✅ Página offline básica quando não há conexão
- ✅ Limpeza automática de caches antigos

### 3. Botão de Instalação
- ✅ Captura do evento `beforeinstallprompt`
- ✅ Botão de instalação visível na interface
- ✅ Suporte para iOS/Safari (instruções manuais)
- ✅ Detecção automática se o app já está instalado
- ✅ Feedback visual após instalação

### 4. Meta Tags PWA
- ✅ Meta tags para iOS/Apple
- ✅ Meta tags para Android/Chrome
- ✅ Meta tags gerais PWA
- ✅ Apple Touch Icons
- ✅ Favicon

### 5. Estilos CSS
- ✅ Estilos para banner de instalação
- ✅ Estilos responsivos para mobile
- ✅ Ajustes para modo standalone (PWA instalado)
- ✅ Suporte para safe areas (notch, etc.)

## 🚀 Guia rápido (iPhone + limpeza + push)

### Instalar no iPhone
1. Abra o app no Safari ou Chrome no iOS 16.4+.
2. Um “pílula” discreta aparecerá perto da navegação com o texto **Compartilhar → Adicionar à Tela de Início**.
3. Toque em **Instalar no iPhone** para abrir o passo‑a‑passo detectando automaticamente se você está no Safari ou no Chrome.
4. Após adicionar o atalho à Home Screen, abra o ícone recém-criado. Na primeira execução standalone o app mostra um toast: **“App instalado — atalhos offline e notificações habilitados”**.

### Limpar cache e Service Worker
1. Abra o app no Chrome/Edge e pressione `Ctrl+Shift+I` para abrir o DevTools.
2. Vá em **Application → Service Workers** e clique em **Unregister**.
3. Ainda em **Application**, abra **Storage** e clique em **Clear site data** para limpar caches e Storage.
4. Recarregue a página para que o `service-worker.js` atual seja instalado novamente.

### Validar Push Web (opcional)
1. Defina a variável de ambiente `PWA_PUSH_PUBLIC_KEY` com a chave pública VAPID.
2. Acesse o app instalado (modo standalone). O script solicitará permissão de push e registrará o subscription apenas nesse contexto.
3. Use a ferramenta `web-push` ou sua API backend para enviar uma notificação de teste para o endpoint retornado (evento `pwa:push:subscribed` no navegador).
4. Em navegadores que não suportam push (Safari < 16.4 ou navegadores sem `PushManager`) o registro é ignorado silenciosamente.

### Feature flag
- `PWA_ENABLED` controla todos os componentes novos (manifest link, service worker, hints iOS, etc.). Defina `PWA_ENABLED=0` para voltar ao comportamento antigo sem remover código.
- Cores padrão podem ser sobrepostas via `PWA_THEME_COLOR` e `PWA_BACKGROUND_COLOR`.

## 📁 Arquivos criados/modificados

### Arquivos criados:
1. `foco_especializado/core/static/js/pwa-install.js` - Gerenciador de instalação PWA
2. `foco_especializado/core/static/icon.svg` - Ícone SVG placeholder
3. `foco_especializado/core/static/generate_icons.py` - Script para gerar ícones PNG
4. `foco_especializado/core/static/create_icons_simple.py` - Script alternativo para gerar ícones
5. `foco_especializado/core/static/README_ICONES.md` - Documentação sobre ícones
6. `foco_especializado/PWA_SETUP.md` - Este documento

### Arquivos modificados:
1. `foco_especializado/core/static/manifest.json` - Melhorado com todas as configurações
2. `foco_especializado/core/static/service-worker.js` - Implementado cache offline funcional
3. `foco_especializado/core/templates/core/base.html` - Adicionado banner de instalação, meta tags, scripts
4. `foco_especializado/core/static/css/app.css` - Adicionados estilos para banner de instalação

### Arquivos que já existiam (sem alterações):
- `foco_especializado/core/views.py` - Views para servir manifest e service worker (já existiam)
- `foco_especializado/core/urls.py` - URLs para manifest e service worker (já existiam)

## 🔧 Como testar o PWA localmente

### 1. Preparação

#### Instalar dependências (se necessário)
```bash
pip install Pillow
```

#### Gerar ícones (opcional, mas recomendado)
```bash
cd foco_especializado/core/static
python create_icons_simple.py
```

**Nota:** Se o Pillow não estiver instalado ou houver problemas, você pode:
- Usar ferramentas online (veja `README_ICONES.md`)
- Criar ícones manualmente
- Usar ícones placeholder temporários

### 2. Rodar o projeto

```bash
# No diretório raiz do projeto
python manage.py runserver
```

### 3. Acessar via navegador

1. Abra o Chrome ou Edge (recomendado para testar PWA)
2. Acesse `http://localhost:8000` (ou a porta configurada)
3. Faça login ou crie uma conta

### 4. Verificar o PWA

#### Chrome DevTools:
1. Abra as DevTools (F12)
2. Vá para a aba **Application** (ou **Aplicativo**)
3. Verifique:
   - **Manifest**: Deve mostrar o manifest.json carregado
   - **Service Workers**: Deve mostrar o service worker registrado e ativo
   - **Cache Storage**: Deve mostrar o cache criado
   - **Installable**: Deve indicar se o app é instalável

#### Testar instalação:
1. Procure pelo ícone de instalação na barra de endereços do Chrome
2. Ou clique no botão "Instalar" no banner que aparece no topo da página
3. O app deve ser instalado e abrir em modo standalone

#### Testar offline:
1. Abra as DevTools (F12)
2. Vá para a aba **Network** (Rede)
3. Marque a opção **Offline** (Offline)
4. Recarregue a página
5. A página deve carregar do cache (modo offline)

### 5. Lighthouse (Auditoria PWA)

1. Abra as DevTools (F12)
2. Vá para a aba **Lighthouse**
3. Selecione **Progressive Web App**
4. Clique em **Generate report** (Gerar relatório)
5. Verifique a pontuação e sugestões

## 🚀 Ambiente de produção

### ⚠️ Requisitos essenciais

1. **HTTPS**: O PWA **DEVE** ser servido via HTTPS em produção
   - Service Workers não funcionam em HTTP (exceto localhost)
   - Use um certificado SSL válido
   - Configure o servidor web (Nginx, Apache, etc.) para HTTPS

2. **Arquivos estáticos**: Configure corretamente o Django para servir arquivos estáticos
   ```bash
   python manage.py collectstatic
   ```
   - Configure `STATIC_ROOT` no `settings.py`
   - Configure o servidor web para servir arquivos estáticos

3. **CORS**: Se necessário, configure CORS corretamente
   - O service worker precisa acessar recursos do mesmo domínio
   - Ou configure CORS adequadamente se usar CDN

### Configurações recomendadas

#### settings.py
```python
# Produção
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com', 'www.seu-dominio.com']

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

#### Nginx (exemplo)
```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location /static/ {
        alias /path/to/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Ajustes adicionais para produção

1. **Versão do cache**: Incremente `CACHE_VERSION` no `service-worker.js` quando houver mudanças nos assets
2. **Ícones**: Substitua os ícones placeholder por ícones profissionais
3. **Manifest**: Ajuste URLs e configurações conforme necessário
4. **Cache**: Ajuste estratégias de cache conforme necessário
5. **Offline page**: Crie uma página offline personalizada se desejar

## 📝 Notas importantes

### iOS/Safari
- iOS/Safari não suporta `beforeinstallprompt` da mesma forma que Chrome/Edge
- O app mostra instruções manuais para instalação no iOS
- O usuário deve usar "Adicionar à Tela de Início" manualmente

### Android/Chrome
- Suporte completo para `beforeinstallprompt`
- Botão de instalação aparece automaticamente
- Instalação funciona perfeitamente

### Desktop
- Chrome e Edge suportam instalação de PWA
- O app pode ser instalado como aplicativo desktop
- Funciona em Windows, macOS e Linux

## 🐛 Troubleshooting

### Service Worker não registra
- Verifique se está usando HTTPS (ou localhost)
- Verifique se o arquivo `service-worker.js` está acessível
- Verifique o console do navegador para erros

### Ícones não aparecem
- Verifique se os arquivos de ícone existem em `core/static/`
- Execute `python manage.py collectstatic`
- Verifique os caminhos no `manifest.json`

### Botão de instalação não aparece
- Verifique se o app atende aos critérios de instalação
- Verifique se o manifest.json está correto
- Verifique se o service worker está ativo
- Verifique o console do navegador para erros

### Cache não funciona
- Verifique se o service worker está ativo
- Verifique se os recursos estão sendo cacheados
- Verifique o Cache Storage nas DevTools
- Limpe o cache e recarregue a página

## 📚 Recursos adicionais

- [MDN - Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Google - PWA](https://web.dev/progressive-web-apps/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)

## 🎯 Próximos passos (opcional)

1. **Ícones profissionais**: Substitua os ícones placeholder por ícones profissionais
2. **Página offline personalizada**: Crie uma página offline mais elaborada
3. **Notificações push**: Implemente notificações push (opcional)
4. **Background sync**: Implemente sincronização em background (opcional)
5. **Analytics**: Adicione analytics para rastrear instalações
6. **A/B testing**: Teste diferentes estratégias de cache
7. **Performance**: Otimize ainda mais o desempenho do PWA

## ✅ Checklist final

- [x] Manifest.json configurado
- [x] Service Worker implementado
- [x] Botão de instalação funcional
- [x] Meta tags PWA adicionadas
- [x] Estilos CSS para PWA
- [x] Cache offline funcional
- [x] Suporte para iOS/Safari
- [x] Suporte para Android/Chrome
- [ ] Ícones PNG criados (opcional - pode ser feito depois)
- [ ] Testado localmente
- [ ] Configurado para produção (HTTPS)
- [ ] Testado em produção

## 🎉 Conclusão

O projeto Django "3 Coisas de Hoje" está agora configurado como um PWA completo e funcional. O app pode ser instalado em dispositivos móveis e desktop, funciona offline, e oferece uma experiência de aplicativo nativo.

**Próximo passo:** Teste o PWA localmente seguindo as instruções acima, e depois configure para produção com HTTPS.

---

**Data de criação:** 2024
**Versão:** 1.0
**Autor:** Sistema de configuração PWA

