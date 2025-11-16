"""
Script para gerar ícones PNG a partir do icon.svg existente.

Este script converte o SVG para PNG nos tamanhos necessários para o PWA.

Uso:
    python generate_icons_from_svg.py

Requisitos:
    pip install Pillow cairosvg
    OU
    pip install Pillow (e usar uma abordagem alternativa)
"""

import os
import sys

# Tenta importar cairosvg (melhor opção)
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False
    print("AVISO: cairosvg nao esta instalado. Tentando abordagem alternativa...")
    print("   Para melhor qualidade, instale: pip install cairosvg")

# Tenta importar Pillow (sempre necessário)
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("❌ Erro: Pillow não está instalado.")
    print("   Instale com: pip install Pillow")
    sys.exit(1)

# Tamanhos de ícone necessários para o PWA
ICON_SIZES = [
    (192, 192),
    (256, 256),
    (512, 512),
]

# Diretório do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(SCRIPT_DIR, 'icon.svg')
OUTPUT_DIR = SCRIPT_DIR


def generate_from_svg_cairo(svg_path, output_path, size):
    """Gera PNG a partir de SVG usando cairosvg (melhor qualidade)."""
    if not HAS_CAIROSVG:
        return False
    
    try:
        width, height = size
        cairosvg.svg2png(
            url=svg_path,
            write_to=output_path,
            output_width=width,
            output_height=height
        )
        return True
    except Exception as e:
        print(f"   AVISO: Erro ao usar cairosvg: {e}")
        return False


def generate_from_svg_pillow(svg_path, output_path, size):
    """Gera PNG a partir de SVG usando Pillow (fallback)."""
    if not HAS_PILLOW:
        return False
    
    try:
        # Pillow não suporta SVG diretamente, então vamos ler o SVG como texto
        # e criar uma imagem baseada nele
        from PIL import Image, ImageDraw, ImageFont
        
        width, height = size
        
        # Lê o SVG para extrair informações
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # Cores do SVG
        purple_color = (79, 70, 229)  # #4F46E5 - roxo
        white_color = (255, 255, 255)  # Branco
        
        # Seguindo exatamente o SVG:
        # - Fundo branco (transparente no SVG, mas branco para PWA)
        # - Círculo ROXO no centro (r="240" em canvas 512x512)
        # - Texto BRANCO sobre o círculo roxo
        
        # Cria imagem com fundo branco
        img = Image.new('RGB', (width, height), white_color)
        draw = ImageDraw.Draw(img)
        
        # Desenha círculo ROXO no centro (baseado no SVG: r="240" em canvas 512x512)
        # O círculo tem raio de 240px em 512px
        # Centro em (256, 256), então margem = (512 - 240*2) / 2 = 16px
        margin = int(width * 16 / 512)  # Margem proporcional
        circle_coords = [margin, margin, width - margin, height - margin]
        draw.ellipse(circle_coords, fill=purple_color)
        
        # Desenha o número "3" BRANCO no centro do círculo roxo
        # No SVG: font-size="240" para 512px, então proporcional
        font_size = int(width * 240 / 512)
        font = None
        
        # Tenta carregar uma fonte TrueType bold se disponível
        try:
            # Windows
            if sys.platform == 'win32':
                font_paths = [
                    'C:/Windows/Fonts/arialbd.ttf',  # Arial Bold
                    'C:/Windows/Fonts/arial.ttf',    # Arial (fallback)
                ]
                for fp in font_paths:
                    if os.path.exists(fp):
                        font = ImageFont.truetype(fp, font_size)
                        break
            # Linux
            elif sys.platform.startswith('linux'):
                font_paths = [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                ]
                for fp in font_paths:
                    if os.path.exists(fp):
                        font = ImageFont.truetype(fp, font_size)
                        break
            # macOS
            elif sys.platform == 'darwin':
                font_paths = [
                    '/System/Library/Fonts/Helvetica.ttc',
                    '/System/Library/Fonts/Arial Bold.ttf',
                ]
                for fp in font_paths:
                    if os.path.exists(fp):
                        font = ImageFont.truetype(fp, font_size)
                        break
        except:
            pass
        
        # Fallback para fonte padrão se não encontrou
        if font is None:
            try:
                font = ImageFont.load_default()
            except:
                pass
        
        # Desenha "3" BRANCO centralizado
        # No SVG: x="256" y="320" font-size="240" (em canvas 512x512)
        # y=320 é a linha de base do texto, precisamos centralizar verticalmente
        text = "3"
        font_size = int(width * 240 / 512)  # Proporcional ao SVG
        
        # Garante que temos uma fonte válida
        if font is None:
            try:
                font = ImageFont.load_default()
            except:
                pass
        
        if font:
            # Calcula dimensões do texto
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_ascent = -bbox[1] if bbox[1] < 0 else 0  # Altura acima da linha de base
        else:
            # Estimativa conservadora
            text_width = int(width * 0.4)
            text_height = int(height * 0.5)
            text_ascent = text_height * 0.8
        
        # Posição exata baseada no SVG
        # SVG: y=320 em 512px = proporção exata
        # Centraliza horizontalmente
        x = (width - text_width) // 2
        # y=320 no SVG é a linha de base, então ajustamos para centralizar
        # No SVG, o centro do círculo está em y=256, e o texto em y=320
        # Isso significa que o texto está 64px abaixo do centro (320-256=64)
        # Em proporção: 64/512 = 0.125
        svg_y_base = int(height * 320 / 512)  # Linha de base exata do SVG
        y = svg_y_base - text_ascent  # Ajusta para que o texto fique centralizado na posição
        
        # Desenha o texto BRANCO (sobre o círculo roxo, como no SVG)
        if font:
            draw.text((x, y), text, fill=white_color, font=font)
        else:
            draw.text((x, y), text, fill=white_color)
        
        # Desenha "Coisas" BRANCO abaixo do "3" (em TODOS os tamanhos, como no SVG)
        # No SVG: x="256" y="380" font-size="60" (em canvas 512x512)
        text2 = "Coisas"
        font_size2 = max(10, int(width * 60 / 512))  # font-size="60" no SVG, mínimo 10px
        
        font2 = None
        try:
            # Tenta usar a mesma fonte, mas menor
            if font and hasattr(font, 'path'):
                font2 = ImageFont.truetype(font.path, font_size2)
            elif sys.platform == 'win32':
                font_paths = [
                    'C:/Windows/Fonts/arialbd.ttf',
                    'C:/Windows/Fonts/arial.ttf',
                ]
                for fp in font_paths:
                    if os.path.exists(fp):
                        font2 = ImageFont.truetype(fp, font_size2)
                        break
            elif sys.platform.startswith('linux'):
                font_paths = [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                ]
                for fp in font_paths:
                    if os.path.exists(fp):
                        font2 = ImageFont.truetype(fp, font_size2)
                        break
        except:
            pass
        
        if font2 is None:
            try:
                font2 = ImageFont.load_default()
            except:
                font2 = None
        
        # Posição exata baseada no SVG: y="380" para 512px
        if font2:
            bbox2 = draw.textbbox((0, 0), text2, font=font2)
            text2_width = bbox2[2] - bbox2[0]
            text2_height = bbox2[3] - bbox2[1]
            text2_ascent = -bbox2[1] if bbox2[1] < 0 else 0
        else:
            text2_width = int(width * 0.5)
            text2_height = int(height * 0.1)
            text2_ascent = text2_height * 0.8
        
        # Centraliza horizontalmente
        x2 = (width - text2_width) // 2
        # SVG: y=380 em 512px = proporção exata
        svg_y2_base = int(height * 380 / 512)  # Linha de base exata do SVG
        y2 = svg_y2_base - text2_ascent  # Ajusta para posicionamento correto
        
        # Desenha "Coisas" BRANCO (sobre o círculo roxo, como no SVG)
        if font2:
            draw.text((x2, y2), text2, fill=white_color, font=font2)
        else:
            draw.text((x2, y2), text2, fill=white_color)
        
        img.save(output_path, 'PNG')
        return True
    except Exception as e:
        print(f"   ERRO ao gerar com Pillow: {e}")
        return False


def create_maskable_icon(size, base_icon_path):
    """Cria um ícone maskable a partir do ícone base."""
    if not HAS_PILLOW:
        return False
    
    try:
        from PIL import Image
        
        # Carrega o ícone base
        base_img = Image.open(base_icon_path).convert('RGBA')
        width, height = size
        
        # Redimensiona se necessário
        if base_img.size != (width, height):
            base_img = base_img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Cria nova imagem com área segura (80% centralizado)
        maskable_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        safe_area_size = int(width * 0.8)
        safe_area_margin = (width - safe_area_size) // 2
        
        # Redimensiona o conteúdo para a área segura
        content = base_img.resize((safe_area_size, safe_area_size), Image.Resampling.LANCZOS)
        
        # Cola o conteúdo na área segura
        maskable_img.paste(content, (safe_area_margin, safe_area_margin), content)
        
        return maskable_img
    except Exception as e:
        print(f"   ERRO ao criar maskable: {e}")
        return False


def main():
    """Função principal que gera todos os ícones."""
    print("=" * 60)
    print("Gerando icones PNG a partir do icon.svg")
    print("=" * 60)
    print(f"SVG de origem: {SVG_PATH}")
    print(f"Diretorio de saida: {OUTPUT_DIR}\n")
    
    # Verifica se o SVG existe
    if not os.path.exists(SVG_PATH):
        print(f"ERRO: SVG nao encontrado em {SVG_PATH}")
        sys.exit(1)
    
    # Gera ícones normais
    print("Gerando icones normais...")
    for size in ICON_SIZES:
        width, height = size
        filename = f"icon-{width}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        print(f"  Gerando {filename} ({width}x{height})...", end=" ")
        
        # Tenta usar cairosvg primeiro (melhor qualidade)
        success = False
        if HAS_CAIROSVG:
            success = generate_from_svg_cairo(SVG_PATH, filepath, size)
        
        # Fallback para Pillow
        if not success:
            success = generate_from_svg_pillow(SVG_PATH, filepath, size)
        
        if success:
            print("OK")
        else:
            print("FALHOU")
    
    # Gera ícones maskable (apenas 192 e 512)
    print("\nGerando icones maskable...")
    maskable_sizes = [(192, 192), (512, 512)]
    for size in maskable_sizes:
        width, height = size
        filename = f"icon-{width}-maskable.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        base_filename = f"icon-{width}.png"
        base_filepath = os.path.join(OUTPUT_DIR, base_filename)
        
        print(f"  Gerando {filename} ({width}x{height})...", end=" ")
        
        if os.path.exists(base_filepath):
            maskable_img = create_maskable_icon(size, base_filepath)
            if maskable_img:
                maskable_img.save(filepath, 'PNG')
                print("OK")
            else:
                print("FALHOU")
        else:
            print("AVISO: Icone base nao encontrado, pulando...")
    
    print("\n" + "=" * 60)
    print("Processo concluido!")
    print("=" * 60)
    
    if not HAS_CAIROSVG:
        print("\nDica: Para melhor qualidade, instale cairosvg:")
        print("   pip install cairosvg")


if __name__ == '__main__':
    main()

