# Guia de Validação e Teste do PWA

Este documento descreve como validar e testar o Progressive Web App (PWA) "3 Coisas de Hoje" tanto em dispositivos móveis quanto em desktop.

## 📋 Pré-requisitos

- O app Django deve estar rodando (localmente ou em produção)
- Navegadores modernos: Chrome, Edge, ou Safari (iOS)
- Para produção: HTTPS é obrigatório (exceto localhost)

## 🖥️ Validação em Desktop (Chrome/Edge)

### 1. Abrir as DevTools

1. Abra o app no navegador (Chrome ou Edge)
2. Pressione `F12` ou clique com o botão direito → "Inspecionar"
3. Vá para a aba **"Application"** (ou "Aplicativo" em português)

### 2. Verificar o Manifest

1. No menu lateral, clique em **"Manifest"**
2. Verifique se:
   - ✅ O manifest está carregado corretamente
   - ✅ Todos os campos estão preenchidos (name, short_name, icons, etc.)
   - ✅ Os ícones aparecem corretamente (se os ícones não existirem, aparecerá um aviso)
   - ✅ Não há erros em vermelho

### 3. Verificar o Service Worker

1. No menu lateral, clique em **"Service Workers"**
2. Verifique se:
   - ✅ O service worker está registrado
   - ✅ O status é "activated and is running"
   - ✅ Não há erros em vermelho
   - ✅ A URL do service worker está correta (`/service-worker.js`)

### 4. Verificar a Instalabilidade

1. Procure o ícone de **instalação** na barra de endereços:
   - Chrome: Ícone de "+" ou "Instalar" no canto direito da barra de endereços
   - Edge: Ícone similar no canto direito
2. Se o ícone aparecer, o app é instalável
3. Clique no ícone para instalar o app
4. O app deve abrir em uma janela separada (modo standalone)

### 5. Testar o Modo Instalado

1. Após instalar, abra o app instalado
2. Verifique se:
   - ✅ Não há barra de endereços (modo standalone)
   - ✅ O app funciona normalmente
   - ✅ O service worker está ativo (verifique nas DevTools)

### 6. Usar a Página de Debug

1. Acesse `/pwa-debug/` (requer login)
2. A página mostra:
   - Status do manifest
   - Status do service worker
   - Estado da instalação
   - Informações do navegador
   - Modo de exibição atual

## 📱 Validação em Mobile (Android)

### 1. Acessar o App

1. Abra o Chrome no dispositivo Android
2. Acesse a URL do app (pode ser localhost se estiver na mesma rede, ou URL de produção)

### 2. Verificar o Banner de Instalação

1. O banner de instalação deve aparecer automaticamente após alguns segundos
2. O banner deve mostrar:
   - Texto "📱 Instale o app"
   - Botão "Instalar Agora"
3. Se o banner não aparecer, verifique:
   - Se o evento `beforeinstallprompt` foi disparado (console do navegador)
   - Se o app já está instalado
   - Se o navegador suporta PWA

### 3. Instalar o App

1. Toque no botão "Instalar Agora" no banner
2. Ou use o menu do Chrome (⋮) → "Instalar app" ou "Adicionar à tela inicial"
3. Confirme a instalação
4. O app deve aparecer na tela inicial

### 4. Testar o App Instalado

1. Abra o app da tela inicial
2. Verifique se:
   - ✅ O app abre em modo standalone (sem barra de navegador)
   - ✅ Funciona offline (se o service worker estiver cacheando)
   - ✅ O ícone do app aparece corretamente

### 5. Verificar nas DevTools (Opcional)

1. Conecte o dispositivo Android ao computador via USB
2. No Chrome do desktop, vá para `chrome://inspect`
3. Encontre o dispositivo e clique em "inspect"
4. Use as DevTools para verificar o manifest e service worker

## 🍎 Validação em iOS (Safari)

### 1. Acessar o App

1. Abra o Safari no iPhone/iPad
2. Acesse a URL do app

### 2. Instalar o App

1. Toque no botão de **Compartilhar** (ícone de quadrado com seta)
2. Role para baixo e toque em **"Adicionar à Tela de Início"**
3. Toque em **"Adicionar"** no canto superior direito
4. O app aparecerá na tela inicial

### 3. Testar o App Instalado

1. Abra o app da tela inicial
2. Verifique se:
   - ✅ O app abre em modo standalone
   - ✅ Funciona normalmente
   - ⚠️ Nota: Service Workers têm suporte limitado no iOS

## ✅ Checklist de Validação

### Funcionalidades Básicas

- [ ] Manifest.json está acessível e válido
- [ ] Service Worker está registrado e ativo
- [ ] Ícones estão disponíveis (ou placeholders)
- [ ] App pode ser instalado em desktop (Chrome/Edge)
- [ ] App pode ser instalado em mobile (Android)
- [ ] App funciona em modo standalone após instalação
- [ ] Banner de instalação aparece quando apropriado
- [ ] Botão de instalação funciona corretamente

### Desktop (Chrome/Edge)

- [ ] Ícone de instalação aparece na barra de endereços
- [ ] App instala corretamente
- [ ] App abre em janela separada (standalone)
- [ ] Service worker funciona offline
- [ ] Página de debug (`/pwa-debug/`) mostra informações corretas

### Mobile (Android)

- [ ] Banner de instalação aparece
- [ ] App pode ser adicionado à tela inicial
- [ ] App abre em modo standalone
- [ ] Ícone do app aparece corretamente
- [ ] Funciona offline (se service worker estiver ativo)

### iOS (Safari)

- [ ] App pode ser adicionado à tela inicial
- [ ] App abre em modo standalone
- [ ] Funciona normalmente (service worker pode ter limitações)

## 🔧 Solução de Problemas

### O ícone de instalação não aparece

**Possíveis causas:**
- O app já está instalado
- O manifest.json tem erros
- Os ícones não estão disponíveis
- O service worker não está registrado
- O app não atende aos critérios de instalabilidade

**Solução:**
1. Verifique o manifest nas DevTools (aba Application → Manifest)
2. Verifique se há erros no console
3. Verifique se o service worker está ativo
4. Use a página `/pwa-debug/` para diagnóstico

### O banner de instalação não aparece

**Possíveis causas:**
- O evento `beforeinstallprompt` não foi disparado
- O app já está instalado
- O navegador não suporta PWA
- O banner foi fechado recentemente (armazenado no localStorage)

**Solução:**
1. Limpe o localStorage: `localStorage.removeItem('pwa_install_dismissed')`
2. Verifique o console do navegador para erros
3. Verifique se o app já está instalado
4. Tente em outro navegador

### O service worker não está ativo

**Possíveis causas:**
- O app não está sendo servido via HTTPS (exceto localhost)
- Erros no código do service worker
- Cache antigo do service worker

**Solução:**
1. Verifique se está usando HTTPS (ou localhost)
2. Verifique erros no console
3. Desregistre o service worker nas DevTools (Application → Service Workers → Unregister)
4. Recarregue a página

### Os ícones não aparecem

**Possíveis causas:**
- Os arquivos de ícone não existem
- Os caminhos no manifest estão incorretos
- Os ícones não foram coletados (collectstatic)

**Solução:**
1. Gere os ícones usando o script: `python generate_icons.py`
2. Execute `python manage.py collectstatic`
3. Verifique os caminhos no manifest.json
4. Verifique se os arquivos existem em `staticfiles/`

## 📝 Notas Importantes

### Produção

- ⚠️ **HTTPS é obrigatório** para PWA funcionar em produção (exceto localhost)
- ⚠️ Certifique-se de que todos os arquivos estáticos foram coletados (`collectstatic`)
- ⚠️ Verifique se os ícones estão disponíveis nos caminhos corretos
- ⚠️ Teste em diferentes navegadores e dispositivos

### Desenvolvimento

- ✅ Em localhost, HTTP é aceito para desenvolvimento
- ✅ Use a página `/pwa-debug/` para diagnóstico rápido
- ✅ Verifique o console do navegador para erros
- ✅ Use as DevTools para inspecionar o manifest e service worker

### Limitações Conhecidas

- **iOS/Safari**: Service Workers têm suporte limitado
- **Firefox**: Suporte a PWA instalável é limitado
- **Ícones**: Se não existirem, o PWA ainda funciona, mas sem ícones personalizados

## 🚀 Próximos Passos

1. Gerar ícones profissionais (substituir placeholders)
2. Testar em diferentes dispositivos e navegadores
3. Configurar HTTPS em produção
4. Coletar arquivos estáticos (`collectstatic`)
5. Monitorar erros e melhorar a experiência do usuário

## 📚 Recursos Adicionais

- [MDN - Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web.dev - PWA](https://web.dev/progressive-web-apps/)
- [Chrome DevTools - Application](https://developer.chrome.com/docs/devtools/application/)
- [PWA Builder](https://www.pwabuilder.com/)




