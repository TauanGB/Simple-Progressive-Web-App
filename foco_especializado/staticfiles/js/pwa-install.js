/**
 * PWA Installation Manager - Melhorado para Android
 * 
 * Gerencia a instalação do Progressive Web App (PWA) com suporte aprimorado para Android.
 * 
 * Este script:
 * 1. Captura o evento beforeinstallprompt
 * 2. Mostra banner de instalação automaticamente (especialmente no Android)
 * 3. Oferece prompt automático após interação do usuário
 * 4. Detecta se o app já está instalado
 * 5. Fornece instruções manuais para iOS/Safari e Android (fallback)
 * 
 * ⚠️ PRODUÇÃO: Em ambiente de produção, é ESSENCIAL servir o app via HTTPS
 * para que o PWA funcione corretamente.
 */

(function() {
  'use strict';

  const PWA_CONFIG = window.__PWA_SETTINGS || { enabled: false };
  if (!PWA_CONFIG.enabled) {
    console.warn('[PWA Install] Flag PWA_ENABLED está desligada. Script interrompido.');
    return;
  }

  // Variável global para armazenar o evento beforeinstallprompt
  let deferredPrompt = null;
  let installButton = null;
  let installBanner = null;
  let iosHint = null;
  let iosInstallButton = null;
  let iosHintDismiss = null;
  let isInstalled = false;
  let bannerShown = false;
  let autoPromptTimer = null;

  const STORAGE_KEYS = {
    DISMISSED: 'pwa_install_dismissed',
    INSTALLED: 'pwa_installed',
    IOS_HINT_DISMISSED: 'pwa_ios_hint_dismissed',
    FIRST_BOOT_PENDING: 'pwa_first_boot_pending_toast'
  };

  const INSTALL_SUCCESS_MESSAGE = 'App instalado — atalhos offline e notificações habilitados';
  
  // Configurações
  const CONFIG = {
    // Tempo em ms antes de mostrar o banner automaticamente (Android)
    AUTO_SHOW_DELAY: 3000,
    // Tempo em ms antes de mostrar prompt automático após interação
    AUTO_PROMPT_DELAY: 5000,
    // Mostrar banner mesmo sem beforeinstallprompt no Android
    SHOW_BANNER_ALWAYS_ANDROID: true,
    // Armazenar preferência do usuário no localStorage
    STORAGE_KEY: STORAGE_KEYS.DISMISSED,
    // Dias até mostrar novamente após ser fechado
    DISMISS_DURATION_DAYS: 7
  };
  
  // Verifica se o app já está instalado
  function checkIfInstalled() {
    if (isStandaloneMode()) {
      isInstalled = true;
      localStorage.setItem(STORAGE_KEYS.INSTALLED, 'true');
      hideIosHint(false);
      hideInstallButton();
      maybeRegisterPush();
      return true;
    }
    
    // Verifica se foi instalado recentemente
    if (localStorage.getItem(STORAGE_KEYS.INSTALLED) === 'true') {
      isInstalled = true;
      hideInstallButton();
      return true;
    }
    
    return false;
  }
  
  // Verifica se o banner foi fechado recentemente
  function isBannerDismissed() {
    const dismissed = localStorage.getItem(CONFIG.STORAGE_KEY);
    if (!dismissed) return false;
    
    const dismissedDate = new Date(dismissed);
    const now = new Date();
    const daysDiff = (now - dismissedDate) / (1000 * 60 * 60 * 24);
    
    return daysDiff < CONFIG.DISMISS_DURATION_DAYS;
  }
  
  // Marca o banner como fechado
  function dismissBanner() {
    localStorage.setItem(CONFIG.STORAGE_KEY, new Date().toISOString());
    hideInstallButton();
  }
  
  // Verifica se é Android
  function isAndroid() {
    return /Android/i.test(navigator.userAgent);
  }
  
  // Verifica se é iOS/Safari
  function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  }

  function isStandaloneDisplay() {
    return window.matchMedia('(display-mode: standalone)').matches;
  }

  function isStandaloneIOS() {
    return window.navigator.standalone === true;
  }

  function isStandaloneMode() {
    return isStandaloneDisplay() || isStandaloneIOS();
  }
  
  // Verifica se é Chrome no Android
  function isChromeAndroid() {
    return isAndroid() && /Chrome/i.test(navigator.userAgent);
  }

  function isSafariIOS() {
    const ua = navigator.userAgent || '';
    return isIOS() && /safari/i.test(ua) && !/crios|fxios|opios/i.test(ua);
  }

  function isChromeIOS() {
    return isIOS() && /crios/i.test(navigator.userAgent || '');
  }
  
  // Verifica se é mobile
  function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }
  
  function shouldShowIosHint() {
    if (!iosHint || !isIOS() || isInstalled || isStandaloneMode()) {
      return false;
    }
    const dismissedAt = localStorage.getItem(STORAGE_KEYS.IOS_HINT_DISMISSED);
    if (!dismissedAt) {
      return true;
    }
    const diffDays = (Date.now() - Date.parse(dismissedAt)) / (1000 * 60 * 60 * 24);
    return diffDays >= CONFIG.DISMISS_DURATION_DAYS;
  }

  function showIosHint() {
    if (iosHint) {
      iosHint.hidden = false;
    }
  }

  function hideIosHint(persist = true) {
    if (iosHint) {
      iosHint.hidden = true;
    }
    if (persist) {
      localStorage.setItem(STORAGE_KEYS.IOS_HINT_DISMISSED, new Date().toISOString());
    }
  }

  function maybeShowIosHint() {
    if (!shouldShowIosHint()) {
      return;
    }
    setTimeout(() => {
      if (shouldShowIosHint()) {
        showIosHint();
      }
    }, CONFIG.AUTO_SHOW_DELAY);
  }
  
  // Obtém referências aos elementos do DOM
  function getInstallElements() {
    installButton = document.getElementById('pwa-install-button');
    installBanner = document.getElementById('pwa-install-banner');
    iosHint = document.getElementById('ios-install-hint');
    iosInstallButton = document.getElementById('ios-install-button');
    iosHintDismiss = document.getElementById('ios-hint-dismiss');
  }
  
  // Mostra o botão de instalação
  function showInstallButton(force = false) {
    // Não mostra se foi fechado recentemente (exceto se forçado)
    if (!force && isBannerDismissed()) {
      return;
    }
    
    if (installButton) {
      installButton.style.display = 'inline-block';
    }
    if (installBanner) {
      installBanner.style.display = 'block';
      bannerShown = true;
    }
  }
  
  // Oculta o botão de instalação
  function hideInstallButton() {
    if (installButton) {
      installButton.style.display = 'none';
    }
    if (installBanner) {
      installBanner.style.display = 'none';
    }
  }
  
  // Mostra instruções de instalação para Android (fallback)
  function showAndroidInstallInstructions() {
    // Remove modal existente se houver
    const existingModal = document.getElementById('pwa-install-modal');
    if (existingModal) {
      existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.id = 'pwa-install-modal';
    modal.innerHTML = `
      <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        padding: 20px;
        animation: fadeIn 0.3s ease-out;
      ">
        <div style="
          background: white;
          border-radius: 16px;
          padding: 24px;
          max-width: 400px;
          width: 100%;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          animation: slideUp 0.3s ease-out;
        ">
          <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 3rem; margin-bottom: 8px;">📱</div>
            <h2 style="
              font-size: 1.5rem;
              font-weight: 600;
              margin: 0 0 8px 0;
              color: #111827;
            ">Instalar App</h2>
            <p style="
              font-size: 0.875rem;
              color: #6B7280;
              margin: 0;
            ">Adicione este app à tela inicial</p>
          </div>
          
          <div style="
            background: #F3F4F6;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
          ">
            <p style="
              font-size: 0.875rem;
              color: #374151;
              margin: 0 0 12px 0;
              font-weight: 600;
            ">Para instalar no Android:</p>
            <ol style="
              font-size: 0.875rem;
              color: #4B5563;
              margin: 0;
              padding-left: 20px;
              line-height: 2;
            ">
              <li>Toque no menu (⋮) no canto superior direito do navegador</li>
              <li>Selecione <strong>"Instalar app"</strong> ou <strong>"Adicionar à tela inicial"</strong></li>
              <li>Confirme a instalação</li>
            </ol>
          </div>
          
          <div style="display: flex; gap: 12px;">
            <button id="pwa-modal-close" style="
              background-color: #E5E7EB;
              color: #374151;
              border: none;
              padding: 12px 24px;
              font-size: 1rem;
              border-radius: 8px;
              cursor: pointer;
              flex: 1;
              font-weight: 600;
            ">Fechar</button>
            <button id="pwa-modal-try" style="
              background-color: #4F46E5;
              color: white;
              border: none;
              padding: 12px 24px;
              font-size: 1rem;
              border-radius: 8px;
              cursor: pointer;
              flex: 1;
              font-weight: 600;
            ">Tentar Instalar</button>
          </div>
        </div>
      </div>
    `;
    
    // Adiciona estilos de animação
    if (!document.getElementById('pwa-modal-styles')) {
      const style = document.createElement('style');
      style.id = 'pwa-modal-styles';
      style.textContent = `
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from {
            transform: translateY(20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
      `;
      document.head.appendChild(style);
    }
    
    document.body.appendChild(modal);
    
    // Botão fechar
    document.getElementById('pwa-modal-close').addEventListener('click', function() {
      modal.remove();
      dismissBanner();
    });
    
    // Botão tentar instalar
    document.getElementById('pwa-modal-try').addEventListener('click', function() {
      modal.remove();
      // Tenta instalar se houver deferredPrompt
      if (deferredPrompt) {
        installPWA();
      } else {
        // Se não houver prompt, mostra instruções novamente após um momento
        setTimeout(function() {
          alert('Por favor, use o menu do navegador (⋮) para instalar o app.\n\nOu aguarde alguns segundos para tentarmos novamente.');
        }, 100);
      }
    });
    
    // Fecha ao clicar fora
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        modal.remove();
        dismissBanner();
      }
    });
  }
  
  // Mostra instruções de instalação para Desktop (Chrome/Edge)
  function showDesktopInstallInstructions() {
    const modal = document.createElement('div');
    modal.id = 'pwa-desktop-modal';
    modal.innerHTML = `
      <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        padding: 20px;
      ">
        <div style="
          background: white;
          border-radius: 16px;
          padding: 24px;
          max-width: 500px;
          width: 100%;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
          <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 3rem; margin-bottom: 8px;">💻</div>
            <h2 style="
              font-size: 1.5rem;
              font-weight: 600;
              margin: 0 0 8px 0;
              color: #111827;
            ">Instalar App no Desktop</h2>
            <p style="
              font-size: 0.875rem;
              color: #6B7280;
              margin: 0;
            ">Adicione este app ao seu computador para acesso rápido</p>
          </div>
          
          <div style="
            background: #F3F4F6;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
          ">
            <p style="
              font-size: 0.875rem;
              color: #374151;
              margin: 0 0 12px 0;
              font-weight: 600;
            ">Para instalar no Chrome/Edge (Desktop):</p>
            <ol style="
              font-size: 0.875rem;
              color: #4B5563;
              margin: 0;
              padding-left: 20px;
              line-height: 2;
            ">
              <li>Procure o ícone de <strong>"Instalar"</strong> ou <strong>"+"</strong> na barra de endereços (canto direito)</li>
              <li>Clique no ícone e selecione <strong>"Instalar"</strong></li>
              <li>Confirme a instalação na janela que aparecer</li>
            </ol>
            <p style="
              font-size: 0.75rem;
              color: #6B7280;
              margin: 12px 0 0 0;
              font-style: italic;
            ">Ou use o botão "Instalar Agora" acima quando disponível.</p>
          </div>
          
          <div style="display: flex; gap: 12px;">
            <button id="pwa-desktop-modal-close" style="
              background-color: #E5E7EB;
              color: #374151;
              border: none;
              padding: 12px 24px;
              font-size: 1rem;
              border-radius: 8px;
              cursor: pointer;
              flex: 1;
              font-weight: 600;
            ">Fechar</button>
            <button id="pwa-desktop-modal-try" style="
              background-color: #4F46E5;
              color: white;
              border: none;
              padding: 12px 24px;
              font-size: 1rem;
              border-radius: 8px;
              cursor: pointer;
              flex: 1;
              font-weight: 600;
            ">Tentar Instalar</button>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Botão fechar
    document.getElementById('pwa-desktop-modal-close').addEventListener('click', function() {
      modal.remove();
      dismissBanner();
    });
    
    // Botão tentar instalar
    document.getElementById('pwa-desktop-modal-try').addEventListener('click', function() {
      modal.remove();
      // Tenta instalar se houver deferredPrompt
      if (deferredPrompt) {
        installPWA();
      } else {
        // Se não houver prompt, mostra mensagem
        setTimeout(function() {
          alert('Por favor, procure o ícone de instalação na barra de endereços do navegador (canto direito) ou aguarde alguns segundos para tentarmos novamente.');
        }, 100);
      }
    });
    
    // Fecha ao clicar fora
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        modal.remove();
        dismissBanner();
      }
    });
  }
  
  // Mostra instruções de instalação para iOS/Safari
  function showIOSInstallInstructions() {
    const modal = document.createElement('div');
    modal.id = 'pwa-ios-modal';
    const chrome = isChromeIOS();
    const browserLabel = chrome ? 'Chrome no iOS' : 'Safari';
    const steps = chrome
      ? `
            <li>Toque no botão <strong>Compartilhar</strong> (ícone com seta para cima).</li>
            <li>Role a folha de opções e toque em <strong>"Adicionar à Tela de Início"</strong>.</li>
            <li>Confirme tocando em <strong>"Adicionar"</strong>.</li>
        `
      : `
            <li>No Safari, toque no botão <strong>Compartilhar</strong> (quadrado com seta).</li>
            <li>Role até encontrar <strong>"Adicionar à Tela de Início"</strong>.</li>
            <li>Escolha o nome e toque em <strong>"Adicionar"</strong> no canto superior direito.</li>
        `;
    modal.innerHTML = `
      <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        padding: 20px;
      ">
        <div style="
          background: white;
          border-radius: 16px;
          padding: 24px;
          max-width: 420px;
          width: 100%;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
          <h2 style="
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0 0 16px 0;
            color: #111827;
          ">Instalar no iPhone</h2>
          <p style="
            font-size: 0.95rem;
            color: #6B7280;
            margin: 0 0 12px 0;
          ">Detectamos ${browserLabel}. Veja os passos:</p>
          <ol style="
            font-size: 0.875rem;
            color: #374151;
            margin: 0 0 16px 0;
            padding-left: 20px;
            line-height: 1.8;
          ">
            ${steps}
          </ol>
          <p style="font-size: 0.75rem; color: #9CA3AF; margin-bottom: 16px;">
            Após instalar, abra o atalho pela tela inicial para liberar notificações e modo offline.
          </p>
          <button onclick="this.closest('#pwa-ios-modal').remove()" style="
            background-color: #4F46E5;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 1rem;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            font-weight: 600;
          ">Entendi</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }
  
  // Prompt automático após interação do usuário
  function setupAutoPrompt() {
    // Aguarda interação do usuário (scroll, click, etc.)
    let userInteracted = false;
    
    const interactionEvents = ['scroll', 'click', 'touchstart', 'keydown'];
    const onInteraction = function() {
      if (!userInteracted) {
        userInteracted = true;
        
        // Remove listeners
        interactionEvents.forEach(event => {
          document.removeEventListener(event, onInteraction);
        });
        
        // Aguarda um tempo antes de mostrar prompt automático
        autoPromptTimer = setTimeout(function() {
          // Só mostra se não estiver instalado e houver deferredPrompt
          if (!isInstalled && deferredPrompt && !bannerShown) {
            console.log('[PWA Install] Mostrando prompt automático após interação');
            // Mostra o banner primeiro
            showInstallButton(true);
            // Depois tenta o prompt (pode não funcionar em todos os casos)
            // O prompt automático precisa ser acionado por uma ação do usuário
          }
        }, CONFIG.AUTO_PROMPT_DELAY);
      }
    };
    
    // Adiciona listeners
    interactionEvents.forEach(event => {
      document.addEventListener(event, onInteraction, { once: true, passive: true });
    });
  }
  
  // Inicializa o gerenciador de instalação
  function initPWAInstall() {
    // Obtém referências aos elementos
    getInstallElements();

    if (iosHintDismiss) {
      iosHintDismiss.addEventListener('click', function(e) {
        e.preventDefault();
        hideIosHint(true);
      });
    }

    if (iosInstallButton) {
      iosInstallButton.addEventListener('click', function(e) {
        e.preventDefault();
        showIOSInstallInstructions();
      });
    }

    handleFirstBootToast();

    // Verifica se o app já está instalado
    if (checkIfInstalled()) {
      console.log('[PWA Install] App já está instalado');
      return;
    }
    
    // Configura prompt automático
    setupAutoPrompt();
    
    // iOS/Safari: Mostra instruções manuais
    if (isIOS()) {
      console.log('[PWA Install] iOS detectado - mostrando instruções manuais');
      
      if (installButton) {
        installButton.addEventListener('click', function(e) {
          e.preventDefault();
          showIOSInstallInstructions();
        });
      }

      maybeShowIosHint();
      
      // Mostra banner após um delay no iOS
      setTimeout(function() {
        if (!isBannerDismissed()) {
          showInstallButton(true);
        }
      }, CONFIG.AUTO_SHOW_DELAY);
      
      return;
    }
    
    // Android: Configuração especial
    if (isAndroid()) {
      console.log('[PWA Install] Android detectado');
      
      // Mostra banner automaticamente no Android após um delay
      if (CONFIG.SHOW_BANNER_ALWAYS_ANDROID) {
        setTimeout(function() {
          if (!isInstalled && !isBannerDismissed() && !bannerShown) {
            console.log('[PWA Install] Mostrando banner automaticamente no Android');
            showInstallButton(true);
          }
        }, CONFIG.AUTO_SHOW_DELAY);
      }
      
      // Adiciona listener ao botão para mostrar instruções se não houver prompt
      if (installButton) {
        installButton.addEventListener('click', function(e) {
          e.preventDefault();
          if (deferredPrompt) {
            // Tem prompt, instala diretamente
            installPWA();
          } else {
            // Não tem prompt, mostra instruções
            showAndroidInstallInstructions();
          }
        });
      }
    }
    
    // Desktop (Chrome/Edge): Configuração especial
    // O evento beforeinstallprompt também funciona em desktop
    if (!isMobile() && !isIOS()) {
      console.log('[PWA Install] Desktop detectado (Chrome/Edge)');
      
      // Adiciona listener ao botão para instalação em desktop
      if (installButton) {
        installButton.addEventListener('click', function(e) {
          e.preventDefault();
          if (deferredPrompt) {
            // Tem prompt, instala diretamente
            installPWA();
          } else {
            // Não tem prompt, mostra instruções para desktop
            showDesktopInstallInstructions();
          }
        });
      }
    }
    
    // Captura o evento beforeinstallprompt (Chrome, Edge, etc.)
    // Este evento funciona tanto em mobile quanto em desktop
    window.addEventListener('beforeinstallprompt', function(e) {
      console.log('[PWA Install] Evento beforeinstallprompt capturado');
      
      // Previne o prompt padrão do navegador
      e.preventDefault();
      
      // Armazena o evento para uso posterior
      deferredPrompt = e;
      
      // Mostra o banner imediatamente quando o evento é capturado
      // Funciona tanto em mobile quanto em desktop
      if (!isBannerDismissed()) {
        showInstallButton(true);
      }
      
      // No Android, tenta mostrar prompt automático após interação
      if (isAndroid()) {
        // Aguarda um pouco e tenta prompt automático (se usuário interagiu)
        setTimeout(function() {
          // O prompt automático precisa ser acionado por uma ação do usuário
          // Por isso não chamamos diretamente, mas mostramos o banner
        }, 1000);
      }
    });
    
    // Detecta se o app foi instalado
    window.addEventListener('appinstalled', function(e) {
      console.log('[PWA Install] App instalado com sucesso');
      isInstalled = true;
      hideInstallButton();
      hideIosHint(false);
      deferredPrompt = null;
      localStorage.setItem(STORAGE_KEYS.INSTALLED, 'true');
      localStorage.setItem(STORAGE_KEYS.FIRST_BOOT_PENDING, 'true');
      
      // Mostra mensagem de sucesso
      showInstallSuccessMessage(INSTALL_SUCCESS_MESSAGE);
    });
    
    // Adiciona botão de fechar no banner (se não existir)
    if (installBanner) {
      // Verifica se já existe botão de fechar
      let closeButton = installBanner.querySelector('.pwa-install-close');
      if (!closeButton) {
        closeButton = document.createElement('button');
        closeButton.className = 'pwa-install-close';
        closeButton.innerHTML = '✕';
        closeButton.style.cssText = `
          position: absolute;
          top: 8px;
          right: 8px;
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          cursor: pointer;
          font-size: 16px;
          line-height: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
        `;
        closeButton.addEventListener('click', function(e) {
          e.stopPropagation();
          dismissBanner();
        });
        installBanner.style.position = 'relative';
        installBanner.appendChild(closeButton);
      }
    }
  }
  
  // Instala o PWA
  function installPWA() {
    if (deferredPrompt) {
      // Mostra o prompt de instalação
      deferredPrompt.prompt();
      
      // Aguarda a resposta do usuário
      deferredPrompt.userChoice.then(function(choiceResult) {
        console.log('[PWA Install] Escolha do usuário:', choiceResult.outcome);
        
        if (choiceResult.outcome === 'accepted') {
          console.log('[PWA Install] Usuário aceitou a instalação');
          localStorage.setItem(STORAGE_KEYS.INSTALLED, 'true');
        } else {
          console.log('[PWA Install] Usuário rejeitou a instalação');
          // Não fecha o banner se rejeitou, para tentar novamente depois
        }
        
        // Limpa o prompt
        deferredPrompt = null;
      });
    } else {
      // Não há prompt disponível, mostra instruções
      console.log('[PWA Install] Nenhum prompt disponível, mostrando instruções');
      if (isAndroid()) {
        showAndroidInstallInstructions();
      } else if (isIOS()) {
        showIOSInstallInstructions();
      } else if (!isMobile()) {
        // Desktop
        showDesktopInstallInstructions();
      }
    }
  }
  
  // Mostra mensagem de sucesso após instalação
  async function maybeRegisterPush() {
    if (
      !PWA_CONFIG.push_public_key ||
      !('Notification' in window) ||
      !('serviceWorker' in navigator) ||
      !('PushManager' in window)
    ) {
      return;
    }

    if (!isStandaloneMode()) {
      return;
    }

    let permission = Notification.permission;
    if (permission === 'default') {
      try {
        permission = await Notification.requestPermission();
      } catch (error) {
        console.warn('[PWA Install] Permissão de push não concedida', error);
        return;
      }
    }

    if (permission !== 'granted') {
      return;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      let subscription = await registration.pushManager.getSubscription();
      if (!subscription) {
        const applicationServerKey = urlBase64ToUint8Array(PWA_CONFIG.push_public_key);
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey,
        });
      }
      window.dispatchEvent(new CustomEvent('pwa:push:subscribed', { detail: subscription }));
      if (navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
          type: 'PUSH_SUBSCRIPTION_READY',
          subscription,
        });
      }
    } catch (error) {
      console.warn('[PWA Install] Push registration indisponível', error);
    }
  }

  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  function handleFirstBootToast() {
    if (
      localStorage.getItem(STORAGE_KEYS.FIRST_BOOT_PENDING) === 'true' &&
      isStandaloneMode()
    ) {
      showInstallSuccessMessage(INSTALL_SUCCESS_MESSAGE);
      localStorage.setItem(STORAGE_KEYS.FIRST_BOOT_PENDING, 'false');
      maybeRegisterPush();
    }
  }

  function showInstallSuccessMessage(text = INSTALL_SUCCESS_MESSAGE) {
    const message = document.createElement('div');
    message.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background-color: #10B981;
      color: white;
      padding: 16px 24px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 10001;
      font-size: 0.875rem;
      font-weight: 500;
      animation: slideDown 0.3s ease-out;
      max-width: 90%;
      text-align: center;
    `;
    message.textContent = text;
    document.body.appendChild(message);
    
    setTimeout(function() {
      message.style.animation = 'slideUp 0.3s ease-out';
      setTimeout(function() {
        message.remove();
      }, 300);
    }, 3000);
  }
  
  // Adiciona estilos de animação
  function addAnimationStyles() {
    if (!document.getElementById('pwa-install-styles')) {
      const style = document.createElement('style');
      style.id = 'pwa-install-styles';
      style.textContent = `
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        @keyframes slideOut {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(100%);
            opacity: 0;
          }
        }
        @keyframes slideDown {
          from {
            transform: translateX(-50%) translateY(-20px);
            opacity: 0;
          }
          to {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
          }
        }
        @keyframes slideUp {
          from {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
          }
          to {
            transform: translateX(-50%) translateY(-20px);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }
  
  // Inicializa quando o DOM estiver pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      addAnimationStyles();
      initPWAInstall();
    });
  } else {
    addAnimationStyles();
    initPWAInstall();
  }
  
  // Expõe funções globais para uso externo
  window.installPWA = installPWA;
  window.showPWAInstallInstructions = function() {
    if (isAndroid()) {
      showAndroidInstallInstructions();
    } else if (isIOS()) {
      showIOSInstallInstructions();
    }
  };
  
  // Expõe função para verificar se é Android (útil para debug)
  window.isAndroidDevice = isAndroid;
  window.isIOSDevice = isIOS;
  
})();
