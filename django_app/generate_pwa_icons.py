#!/usr/bin/env python3
"""
PWA Icon Generator
Generiert App Icons für Progressive Web App in verschiedenen Größen
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Erstelle ein Icon mit rotem Flaggen-Symbol"""
    img = Image.new('RGB', (size, size), color='#EF4444')  # RedFlag Red
    draw = ImageDraw.Draw(img)
    
    # Weißer Kreis als Hintergrund
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill='white')
    
    # Rote Flagge (vereinfacht als Emoji-Alternative)
    try:
        font_size = size // 2
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
        
        # Flaggen-Emoji
        text = "🚩"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - size // 10
        
        draw.text((x, y), text, font=font, embedded_color=True)
    except Exception as e:
        print(f"Font error: {e}, using fallback")
        # Fallback: Einfaches RF Logo
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size//3)
            text = "RF"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            draw.text((x, y), text, fill='#EF4444', font=font)
        except:
            # Ultimate fallback
            draw.rectangle([size//3, size//4, 2*size//3, 3*size//4], fill='#EF4444')
    
    img.save(output_path, 'PNG')
    print(f"✓ Created: {output_path} ({size}x{size})")

if __name__ == '__main__':
    # Icon Größen für PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # Erstelle static/icons Verzeichnis
    icons_dir = 'static/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    print("🎨 Generating PWA Icons...")
    for size in sizes:
        output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        create_icon(size, output_path)
    
    # Favicon
    create_icon(32, 'static/icons/favicon-32x32.png')
    create_icon(16, 'static/icons/favicon-16x16.png')
    
    # Apple Touch Icon (spezielle Größen)
    create_icon(180, 'static/icons/apple-touch-icon.png')
    
    print("\n✅ All icons generated successfully!")
    print(f"Location: {icons_dir}/")
