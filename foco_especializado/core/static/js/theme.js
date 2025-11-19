/* ============================================
   GERENCIAMENTO DE TEMA (DARK MODE)
   ============================================
   
   Este script gerencia a alternância entre modo claro
   e escuro, respeitando a preferência do sistema e
   persistindo a escolha do usuário.
   
   Funcionalidades:
   - Detecta preferência do sistema (prefers-color-scheme)
   - Persiste escolha do usuário no localStorage
   - Atualiza atributo data-theme no elemento raiz
   - Atualiza meta theme-color para PWA
   - Evita "flash" de tema errado ao carregar
*/

(function() {
    'use strict';
    
    // ============================================
    // CONSTANTES
    // ============================================
    const STORAGE_KEY = 'theme';
    const THEME_LIGHT = 'light';
    const THEME_DARK = 'dark';
    
    // Cores para meta theme-color (PWA)
    const THEME_COLOR_LIGHT = '#F9FAFB';
    const THEME_COLOR_DARK = '#1E293B';
    
    // ============================================
    // FUNÇÕES AUXILIARES
    // ============================================
    
    /**
     * Obtém o tema salvo no localStorage
     * @returns {string|null} 'light', 'dark' ou null se não existir
     */
    function getStoredTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            console.warn('[Theme] Erro ao ler localStorage:', e);
            return null;
        }
    }
    
    /**
     * Salva o tema no localStorage
     * @param {string} theme - 'light' ou 'dark'
     */
    function setStoredTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            console.warn('[Theme] Erro ao salvar no localStorage:', e);
        }
    }
    
    /**
     * Detecta a preferência do sistema
     * @returns {string} 'light' ou 'dark'
     */
    function getSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return THEME_DARK;
        }
        return THEME_LIGHT;
    }
    
    /**
     * Obtém o tema atual a ser aplicado
     * Prioridade: localStorage > preferência do sistema > light (padrão)
     * @returns {string} 'light' ou 'dark'
     */
    function getCurrentTheme() {
        const stored = getStoredTheme();
        if (stored === THEME_LIGHT || stored === THEME_DARK) {
            return stored;
        }
        return getSystemPreference();
    }
    
    /**
     * Aplica o tema no documento
     * @param {string} theme - 'light' ou 'dark'
     */
    function applyTheme(theme) {
        const root = document.documentElement;
        root.setAttribute('data-theme', theme);
        
        // Atualiza meta theme-color para PWA
        updateThemeColor(theme);
        
        // Dispara evento customizado para outros scripts
        const event = new CustomEvent('themechange', {
            detail: { theme: theme }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Atualiza a meta tag theme-color para PWA
     * @param {string} theme - 'light' ou 'dark'
     */
    function updateThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            // Cria a meta tag se não existir
            metaThemeColor = document.createElement('meta');
            metaThemeColor.setAttribute('name', 'theme-color');
            document.head.appendChild(metaThemeColor);
        }
        
        const color = theme === THEME_DARK ? THEME_COLOR_DARK : THEME_COLOR_LIGHT;
        metaThemeColor.setAttribute('content', color);
    }
    
    /**
     * Alterna entre tema claro e escuro
     * @returns {string} O novo tema aplicado
     */
    function toggleTheme() {
        const current = getCurrentTheme();
        const newTheme = current === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
        
        applyTheme(newTheme);
        setStoredTheme(newTheme);
        
        return newTheme;
    }
    
    /**
     * Inicializa o tema ao carregar a página
     * Deve ser executado o mais cedo possível para evitar "flash"
     */
    function initTheme() {
        const theme = getCurrentTheme();
        applyTheme(theme);
        
        // Se não havia tema salvo, salva a preferência do sistema
        if (!getStoredTheme()) {
            setStoredTheme(theme);
        }
    }
    
    /**
     * Monitora mudanças na preferência do sistema
     * (se o usuário não tiver escolhido um tema manualmente)
     */
    function watchSystemPreference() {
        if (!window.matchMedia) {
            return;
        }
        
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Adiciona listener para mudanças na preferência do sistema
        mediaQuery.addEventListener('change', function(e) {
            // Só atualiza se o usuário não tiver escolhido um tema manualmente
            const stored = getStoredTheme();
            if (!stored || stored === 'auto') {
                const newTheme = e.matches ? THEME_DARK : THEME_LIGHT;
                applyTheme(newTheme);
                setStoredTheme(newTheme);
            }
        });
    }
    
    // ============================================
    // INICIALIZAÇÃO
    // ============================================
    
    // Aplica o tema ANTES do DOM estar completamente carregado
    // para evitar "flash" de tema errado
    if (document.readyState === 'loading') {
        // DOM ainda não carregou, aplica imediatamente
        initTheme();
    } else {
        // DOM já carregou, aplica imediatamente também
        initTheme();
    }
    
    // Quando o DOM estiver pronto, configura o botão toggle
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setupToggleButton();
            watchSystemPreference();
        });
    } else {
        // DOM já está pronto
        setupToggleButton();
        watchSystemPreference();
    }
    
    /**
     * Configura o botão toggle de tema
     */
    function setupToggleButton() {
        const toggleButton = document.getElementById('theme-toggle');
        
        if (!toggleButton) {
            // Botão não existe ainda, tenta novamente após um pequeno delay
            setTimeout(setupToggleButton, 100);
            return;
        }
        
        toggleButton.addEventListener('click', function(e) {
            e.preventDefault();
            const newTheme = toggleTheme();
            console.log('[Theme] Tema alterado para:', newTheme);
        });
        
        // Adiciona aria-label dinâmico
        updateToggleAriaLabel();
    }
    
    /**
     * Atualiza o aria-label do botão toggle
     */
    function updateToggleAriaLabel() {
        const toggleButton = document.getElementById('theme-toggle');
        if (toggleButton) {
            const currentTheme = getCurrentTheme();
            const oppositeTheme = currentTheme === THEME_LIGHT ? 'escuro' : 'claro';
            toggleButton.setAttribute('aria-label', `Alternar para modo ${oppositeTheme}`);
            toggleButton.setAttribute('title', `Alternar para modo ${oppositeTheme}`);
        }
    }
    
    // Atualiza aria-label quando o tema muda
    document.addEventListener('themechange', function() {
        updateToggleAriaLabel();
    });
    
    // ============================================
    // API PÚBLICA (para uso em outros scripts)
    // ============================================
    
    window.ThemeManager = {
        getCurrentTheme: getCurrentTheme,
        setTheme: function(theme) {
            if (theme === THEME_LIGHT || theme === THEME_DARK) {
                applyTheme(theme);
                setStoredTheme(theme);
            }
        },
        toggleTheme: toggleTheme
    };
    
})();




