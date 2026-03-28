"""
Script para gerar ícones PNG a partir do icon.svg existente.

Este script converte o SVG para PNG nos tamanhos necessários para o PWA.
Se o SVG não existir, gera ícones placeholder básicos.

Uso:
    python generate_icons.py

Requisitos:
    pip install Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("Erro: Pillow não está instalado.")
    print("Instale com: pip install Pillow")
    exit(1)

# Tamanhos de ícone necessários para o PWA
ICON_SIZES = [
    (192, 192),
    (256, 256),
    (512, 512),
]

# Cores do tema
BACKGROUND_COLOR = (79, 70, 229)  # #4F46E5 (primary color)
TEXT_COLOR = (255, 255, 255)  # Branco
ACCENT_COLOR = (255, 255, 255)  # Branco

# Diretório de saída
# Obtém o diretório onde este script está localizado
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = SCRIPT_DIR


def create_icon(size):
    """Cria um ícone placeholder no tamanho especificado."""
    width, height = size
    
    # Cria uma imagem com fundo
    img = Image.new('RGB', (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Desenha um círculo no centro
    margin = width // 8
    circle_size = width - (margin * 2)
    circle_coords = [
        margin, margin,
        width - margin, height - margin
    ]
    draw.ellipse(circle_coords, fill=TEXT_COLOR)
    
    # Desenha o número "3" no centro
    try:
        # Tenta usar uma fonte padrão
        font_size = width // 3
        # Fonte básica do PIL
        font = ImageFont.load_default()
        # Ajusta o tamanho da fonte
        # Como load_default() não permite tamanho personalizado,
        # vamos desenhar manualmente
    except:
        font = None
    
    # Desenha o número "3" manualmente
    text = "3"
    # Calcula posição do texto (centralizado)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Posição centralizada
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - text_height // 4
    
    # Desenha o texto
    draw.text(
        (x, y),
        text,
        fill=BACKGROUND_COLOR,
        font=font
    )
    
    # Para ícones maiores, desenha um texto mais elaborado
    if size[0] >= 256:
        # Desenha rótulo curto abaixo do número
        text2 = "Dia"
        bbox2 = draw.textbbox((0, 0), text2, font=font)
        text2_width = bbox2[2] - bbox2[0]
        text2_height = bbox2[3] - bbox2[1]
        
        x2 = (width - text2_width) // 2
        y2 = y + text_height + text2_height // 2
        
        draw.text(
            (x2, y2),
            text2,
            fill=BACKGROUND_COLOR,
            font=font
        )
    
    return img


def create_maskable_icon(size):
    """Cria um ícone maskable (com área segura) no tamanho especificado."""
    width, height = size
    
    # Cria uma imagem com fundo transparente
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Área segura: 80% do tamanho total (centralizado)
    safe_area_size = int(width * 0.8)
    safe_area_margin = (width - safe_area_size) // 2
    
    # Desenha um círculo na área segura
    circle_coords = [
        safe_area_margin, safe_area_margin,
        width - safe_area_margin, height - safe_area_margin
    ]
    draw.ellipse(circle_coords, fill=BACKGROUND_COLOR)
    
    # Desenha o número "3" no centro
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    text = "3"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - text_height // 4
    
    draw.text(
        (x, y),
        text,
        fill=TEXT_COLOR,
        font=font
    )
    
    return img


def main():
    """Função principal que gera todos os ícones."""
    svg_path = os.path.join(OUTPUT_DIR, 'icon.svg')
    
    # Verifica se existe o SVG e usa o script especializado
    if os.path.exists(svg_path):
        print("SVG encontrado! Usando generate_icons_from_svg.py...")
        print("Execute: python generate_icons_from_svg.py")
        print("\nOu continuando com geracao basica...")
        print("=" * 60)
    
    print("Gerando icones para o PWA...")
    print(f"Diretorio de saida: {OUTPUT_DIR}")
    
    # Gera ícones normais
    for size in ICON_SIZES:
        width, height = size
        filename = f"icon-{width}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        print(f"Gerando {filename}...")
        icon = create_icon(size)
        icon.save(filepath, 'PNG')
        print(f"OK - {filename} criado")
    
    # Gera ícones maskable (apenas 192 e 512)
    maskable_sizes = [(192, 192), (512, 512)]
    for size in maskable_sizes:
        width, height = size
        filename = f"icon-{width}-maskable.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        print(f"Gerando {filename}...")
        icon = create_maskable_icon(size)
        icon.save(filepath, 'PNG')
        print(f"OK - {filename} criado")
    
    print("\n" + "=" * 60)
    print("Todos os icones foram gerados com sucesso!")
    print("=" * 60)
    
    if os.path.exists(svg_path):
        print("\nNOTA: Para melhor qualidade, use:")
        print("   python generate_icons_from_svg.py")
        print("   (Este script usa o icon.svg como base)")
    else:
        print("\nNOTA: Estes sao icones placeholder basicos.")
        print("   Para producao, crie um icon.svg e use:")
        print("   python generate_icons_from_svg.py")


if __name__ == '__main__':
    main()

