# Ícones PWA - Instruções

## ⚠️ IMPORTANTE: Ícones necessários

O PWA requer ícones PNG em diferentes tamanhos para funcionar corretamente. Atualmente, os ícones não foram gerados ainda.

## Tamanhos necessários

O `manifest.json` está configurado para usar os seguintes ícones:

- `icon-192.png` (192x192 pixels) - Ícone padrão
- `icon-256.png` (256x256 pixels) - Ícone médio
- `icon-512.png` (512x512 pixels) - Ícone grande
- `icon-192-maskable.png` (192x192 pixels) - Ícone maskable (área segura)
- `icon-512-maskable.png` (512x512 pixels) - Ícone maskable grande

## Como criar os ícones

### Opção 1: Usar o script Python (recomendado)

1. Instale o Pillow:
   ```bash
   pip install Pillow
   ```

2. Execute o script de geração:
   ```bash
   cd foco_especializado/core/static
   python generate_icons.py
   ```

   Isso gerará ícones placeholder básicos que podem ser substituídos depois.

### Opção 2: Usar ferramentas online

#### PWA Asset Generator
- URL: https://github.com/onderceylan/pwa-asset-generator
- Ferramenta que gera todos os ícones necessários a partir de uma imagem base

#### RealFaviconGenerator
- URL: https://realfavicongenerator.net/
- Gera ícones para diferentes plataformas e tamanhos

#### PWA Builder
- URL: https://www.pwabuilder.com/imageGenerator
- Gera ícones PWA a partir de uma imagem

### Opção 3: Criar manualmente

1. Crie uma imagem base (preferencialmente 512x512 pixels ou maior)
2. Use um editor de imagens (Photoshop, GIMP, Figma, etc.) para criar os diferentes tamanhos
3. Salve cada tamanho como PNG com o nome apropriado
4. Para ícones maskable, certifique-se de que o conteúdo importante está dentro de 80% da área central

## Especificações dos ícones

### Ícones normais
- Formato: PNG
- Fundo: Pode ser transparente ou sólido (recomendado: transparente)
- Tamanhos: 192x192, 256x256, 512x512 pixels

### Ícones maskable
- Formato: PNG
- Fundo: Transparente ou sólido
- Área segura: O conteúdo importante deve estar dentro de 80% da área central
- Tamanhos: 192x192, 512x512 pixels
- Purpose: "maskable" no manifest.json

## Diretório dos ícones

Coloque todos os ícones em:
```
foco_especializado/core/static/
```

## Atualizar o manifest.json

Após criar os ícones, certifique-se de que o `manifest.json` está configurado corretamente:

```json
{
  "icons": [
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/static/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

## Coletar arquivos estáticos

Após criar os ícones, execute:

```bash
python manage.py collectstatic
```

Isso copiará os arquivos para `staticfiles/` para uso em produção.

## Testar os ícones

1. Abra o app no navegador
2. Abra as DevTools (F12)
3. Vá para a aba "Application" (Chrome) ou "Application" (Firefox)
4. Verifique se os ícones aparecem corretamente no manifest
5. Teste a instalação do PWA

## Notas

- Os ícones são opcionais para o funcionamento básico do PWA, mas **altamente recomendados** para uma melhor experiência do usuário
- Ícones maskable são recomendados para Android, pois permitem que o sistema adapte o ícone a diferentes formas
- Certifique-se de que os ícones são visualmente claros mesmo em tamanhos pequenos
- Use cores contrastantes para melhor visibilidade
- Teste os ícones em diferentes dispositivos e tamanhos de tela

## Design recomendado

Para o app "Tarefas do Dia" (PWA), considere usar:
- Cor de fundo: #4F46E5 (primary color)
- Cor do texto/ícone: Branco (#FFFFFF)
- Tema: Foco, produtividade, organização
- Elementos: Número "3", calendário, lista de tarefas, etc.

## Ferramentas úteis

- **Figma**: https://www.figma.com/ (design de ícones)
- **GIMP**: https://www.gimp.org/ (edição de imagens gratuita)
- **Photoshop**: https://www.adobe.com/products/photoshop.html (edição profissional)
- **Inkscape**: https://inkscape.org/ (edição de SVG)
- **Canva**: https://www.canva.com/ (design simples)

## Próximos passos

1. Criar ou escolher um design de ícone
2. Gerar os ícones nos tamanhos necessários
3. Colocar os ícones em `foco_especializado/core/static/`
4. Testar o PWA com os novos ícones
5. Ajustar conforme necessário
