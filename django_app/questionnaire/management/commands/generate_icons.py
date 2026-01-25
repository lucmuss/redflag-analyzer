"""
Management Command: PWA Icons generieren
Usage: python manage.py generate_icons
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import os


class Command(BaseCommand):
    help = 'Generiert PWA App Icons (192x192, 512x512)'

    def handle(self, *args, **options):
        # Icon-Verzeichnis erstellen
        icon_dir = os.path.join(settings.BASE_DIR, 'static', 'icons')
        os.makedirs(icon_dir, exist_ok=True)
        
        # Generiere Icons
        self.stdout.write('Generiere PWA Icons...')
        
        for size in [192, 512]:
            icon = self.create_app_icon(size)
            icon_path = os.path.join(icon_dir, f'icon-{size}.png')
            icon.save(icon_path)
            self.stdout.write(self.style.SUCCESS(f'✓ {icon_path} erstellt'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Alle PWA Icons erfolgreich generiert!'))
    
    def create_app_icon(self, size):
        """Erstelle ein RedFlag Analyzer App Icon"""
        # Erstelle quadratisches Bild mit rotem Hintergrund
        img = Image.new('RGB', (size, size), color='#EF4444')
        draw = ImageDraw.Draw(img)
        
        # Zeichne weißen Kreis in der Mitte
        circle_margin = size // 8
        draw.ellipse(
            [circle_margin, circle_margin, size - circle_margin, size - circle_margin],
            fill='white'
        )
        
        # Berechne Emoji-Größe (ca. 50% des Icons)
        text_size = int(size * 0.5)
        
        # Versuche Font zu laden
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', text_size)
        except:
            try:
                font = ImageFont.truetype('arial.ttf', text_size)
            except:
                font = ImageFont.load_default()
        
        # Zeichne "RF" für RedFlag
        text = "RF"
        
        # Zentriere Text
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # Fallback für ältere Pillow Versionen
            text_width, text_height = draw.textsize(text, font=font)
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - size // 20  # Leicht nach oben
        
        draw.text((x, y), text, fill='#EF4444', font=font)
        
        return img
