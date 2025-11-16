"""
Script simples para criar ícones PNG básicos usando apenas a biblioteca padrão.

Este script cria ícones PNG básicos usando a biblioteca padrão do Python.
Os ícones são placeholders simples que podem ser substituídos depois.

NOTA: Este script requer que você tenha o Pillow instalado.
Se não tiver, use uma das ferramentas online mencionadas no README_ICONES.md

Uso:
    python create_icons_simple.py
"""

import os
import sys

def check_pillow():
    """Verifica se o Pillow está instalado."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        return True, Image, ImageDraw, ImageFont
    except ImportError:
        return False, None, None, None

def create_simple_icon(size, output_path):
    """Cria um ícone PNG simples."""
    has_pillow, Image, ImageDraw, ImageFont = check_pillow()
    
    if not has_pillow:
        print("ERRO: Pillow não está instalado.")
        print("Instale com: pip install Pillow")
        print("\nAlternativa: Use uma das ferramentas online mencionadas no README_ICONES.md")
        return False
    
    width, height = size
    bg_color = (79, 70, 229)  # #4F46E5
    text_color = (255, 255, 255)  # Branco
    
    # Cria a imagem
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Desenha um círculo branco
    margin = width // 8
    draw.ellipse([margin, margin, width - margin, height - margin], fill=text_color)
    
    # Desenha o número "3"
    try:
        # Tenta usar uma fonte maior
        font_size = max(20, width // 4)
        # Por enquanto, usa fonte padrão
        font = ImageFont.load_default()
    except:
        font = None
    
    text = "3"
    # Posiciona o texto no centro
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - text_height // 4
    
    draw.text((x, y), text, fill=bg_color, font=font)
    
    # Salva o ícone
    img.save(output_path, 'PNG')
    return True

def main():
    """Função principal."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Criando ícones PNG para o PWA...")
    print(f"Diretório: {script_dir}\n")
    
    # Verifica se o Pillow está instalado
    has_pillow, _, _, _ = check_pillow()
    if not has_pillow:
        print("\n" + "="*60)
        print("Pillow não está instalado.")
        print("\nPara instalar:")
        print("  pip install Pillow")
        print("\nOu use uma das ferramentas online:")
        print("  - https://realfavicongenerator.net/")
        print("  - https://www.pwabuilder.com/imageGenerator")
        print("  - https://github.com/onderceylan/pwa-asset-generator")
        print("="*60)
        sys.exit(1)
    
    # Tamanhos de ícone
    sizes = [
        (192, 192, "icon-192.png"),
        (256, 256, "icon-256.png"),
        (512, 512, "icon-512.png"),
    ]
    
    # Cria os ícones
    created = 0
    for width, height, filename in sizes:
        filepath = os.path.join(script_dir, filename)
        print(f"Criando {filename} ({width}x{height})...")
        if create_simple_icon((width, height), filepath):
            print(f"✓ {filename} criado")
            created += 1
        else:
            print(f"✗ Falha ao criar {filename}")
    
    # Cria ícones maskable
    maskable_sizes = [
        (192, 192, "icon-192-maskable.png"),
        (512, 512, "icon-512-maskable.png"),
    ]
    
    for width, height, filename in maskable_sizes:
        filepath = os.path.join(script_dir, filename)
        print(f"Criando {filename} ({width}x{height})...")
        if create_simple_icon((width, height), filepath):
            print(f"✓ {filename} criado")
            created += 1
        else:
            print(f"✗ Falha ao criar {filename}")
    
    print(f"\n✓ {created} ícone(s) criado(s) com sucesso!")
    print("\n⚠️  NOTA: Estes são ícones placeholder básicos.")
    print("   Para produção, substitua por ícones profissionais.")
    print("   Veja README_ICONES.md para mais informações.")

if __name__ == '__main__':
    main()

