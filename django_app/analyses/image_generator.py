"""
Image Generator Service für Share-Grafiken
Erstellt personalisierte Share-Images mit Pillow
"""
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import os


class ShareImageGenerator:
    """Generiert personalisierte Share-Grafiken für Social Media"""
    
    # Instagram Story Format
    IG_STORY_WIDTH = 1080
    IG_STORY_HEIGHT = 1920
    
    # Standard Post Format
    POST_WIDTH = 1200
    POST_HEIGHT = 630
    
    # Farben
    RED_FLAG_COLOR = '#EF4444'
    WHITE = '#FFFFFF'
    GRAY_900 = '#111827'
    GRAY_100 = '#F3F4F6'
    
    @classmethod
    def generate_instagram_story(cls, analysis):
        """
        Generiert Instagram Story Share-Grafik (1080x1920)
        
        Args:
            analysis: Analysis Model Instance
            
        Returns:
            str: Pfad zur generierten Bilddatei
        """
        # Erstelle Bild
        img = Image.new('RGB', (cls.IG_STORY_WIDTH, cls.IG_STORY_HEIGHT), color=cls.RED_FLAG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Fonts laden
        try:
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 120)
            score_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 300)
            text_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 60)
            small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 45)
        except:
            title_font = ImageFont.load_default()
            score_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Weißer Bereich in der Mitte
        white_rect_margin = 80
        white_rect = [
            white_rect_margin,
            400,
            cls.IG_STORY_WIDTH - white_rect_margin,
            1500
        ]
        draw.rounded_rectangle(white_rect, radius=40, fill=cls.WHITE)
        
        # Titel
        title_text = "RedFlag Analyzer"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (cls.IG_STORY_WIDTH - title_width) // 2
        draw.text((title_x, 200), title_text, fill=cls.WHITE, font=title_font)
        
        # Score
        score_text = str(analysis.score_total)
        score_bbox = draw.textbbox((0, 0), score_text, font=score_font)
        score_width = score_bbox[2] - score_bbox[0]
        score_x = (cls.IG_STORY_WIDTH - score_width) // 2
        draw.text((score_x, 600), score_text, fill=cls.RED_FLAG_COLOR, font=score_font)
        
        # "/10 Red Flags" Text
        subtitle_text = "/10 Red Flags"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=text_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (cls.IG_STORY_WIDTH - subtitle_width) // 2
        draw.text((subtitle_x, 950), subtitle_text, fill=cls.GRAY_900, font=text_font)
        
        # Kategorie Scores (wenn vorhanden)
        y_offset = 1100
        category_scores = analysis.category_scores.all()[:4]  # Max 4 Kategorien
        
        for cat_score in category_scores:
            category_name = cls._get_category_emoji_name(cat_score.category)
            category_text = f"{category_name}: {cat_score.score}/10"
            
            text_bbox = draw.textbbox((0, 0), category_text, font=small_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (cls.IG_STORY_WIDTH - text_width) // 2
            
            draw.text((text_x, y_offset), category_text, fill=cls.GRAY_900, font=small_font)
            y_offset += 70
        
        # Footer
        footer_text = "redflag-analyzer.com"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=text_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (cls.IG_STORY_WIDTH - footer_width) // 2
        draw.text((footer_x, 1750), footer_text, fill=cls.WHITE, font=text_font)
        
        # Speichere Bild
        filename = f'share_ig_story_{analysis.id}.png'
        filepath = os.path.join(settings.MEDIA_ROOT, 'share_images', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img.save(filepath)
        
        return filepath
    
    @classmethod
    def generate_standard_post(cls, analysis):
        """
        Generiert Standard Share-Grafik (1200x630) für Twitter, Facebook etc.
        
        Args:
            analysis: Analysis Model Instance
            
        Returns:
            str: Pfad zur generierten Bilddatei
        """
        # Erstelle Bild
        img = Image.new('RGB', (cls.POST_WIDTH, cls.POST_HEIGHT), color=cls.RED_FLAG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Fonts laden
        try:
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
            score_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 180)
            text_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
        except:
            title_font = ImageFont.load_default()
            score_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Weißer Kreis für Score
        circle_center = (cls.POST_WIDTH // 2, cls.POST_HEIGHT // 2)
        circle_radius = 200
        draw.ellipse(
            [
                circle_center[0] - circle_radius,
                circle_center[1] - circle_radius,
                circle_center[0] + circle_radius,
                circle_center[1] + circle_radius
            ],
            fill=cls.WHITE
        )
        
        # Score im Kreis
        score_text = str(analysis.score_total)
        score_bbox = draw.textbbox((0, 0), score_text, font=score_font)
        score_width = score_bbox[2] - score_bbox[0]
        score_height = score_bbox[3] - score_bbox[1]
        score_x = circle_center[0] - score_width // 2
        score_y = circle_center[1] - score_height // 2 - 20
        draw.text((score_x, score_y), score_text, fill=cls.RED_FLAG_COLOR, font=score_font)
        
        # "/10" unter dem Score
        subtitle_text = "/10"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=text_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = circle_center[0] - subtitle_width // 2
        draw.text((subtitle_x, circle_center[1] + 60), subtitle_text, fill=cls.GRAY_900, font=text_font)
        
        # Titel oben
        title_text = "🚩 RedFlag Analyzer"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (cls.POST_WIDTH - title_width) // 2
        draw.text((title_x, 50), title_text, fill=cls.WHITE, font=title_font)
        
        # Footer
        footer_text = "Wie viele Red Flags hast du? → redflag-analyzer.com"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=text_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (cls.POST_WIDTH - footer_width) // 2
        draw.text((footer_x, 550), footer_text, fill=cls.WHITE, font=text_font)
        
        # Speichere Bild
        filename = f'share_post_{analysis.id}.png'
        filepath = os.path.join(settings.MEDIA_ROOT, 'share_images', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img.save(filepath)
        
        return filepath
    
    @staticmethod
    def _get_category_emoji_name(category):
        """Helper: Kategorie zu Emoji + Name"""
        categories = {
            'TRUST': '🤝 Vertrauen',
            'BEHAVIOR': '🎭 Verhalten',
            'VALUES': '💎 Werte',
            'DYNAMICS': '⚡ Dynamik',
        }
        return categories.get(category, category)
