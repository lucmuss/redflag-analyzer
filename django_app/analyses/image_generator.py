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
    GRAY_600 = '#4B5563'
    
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
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
            score_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 300)
            text_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 60)
            small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 50)
        except:
            title_font = ImageFont.load_default()
            score_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Weißer Bereich in der Mitte
        white_rect_margin = 80
        white_rect = [
            white_rect_margin,
            450,
            cls.IG_STORY_WIDTH - white_rect_margin,
            1500
        ]
        draw.rounded_rectangle(white_rect, radius=40, fill=cls.WHITE)
        
        # Titel - kleinere Schrift, weiter oben
        title_text = "RedFlag Analyzer"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (cls.IG_STORY_WIDTH - title_width) // 2
        draw.text((title_x, 250), title_text, fill=cls.WHITE, font=title_font)
        
        # Score
        score_text = f"{float(analysis.score_total):.1f}"
        score_bbox = draw.textbbox((0, 0), score_text, font=score_font)
        score_width = score_bbox[2] - score_bbox[0]
        score_x = (cls.IG_STORY_WIDTH - score_width) // 2
        draw.text((score_x, 650), score_text, fill=cls.RED_FLAG_COLOR, font=score_font)
        
        # "/5 Red Flags" Text
        subtitle_text = "/5 Red Flags"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=text_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (cls.IG_STORY_WIDTH - subtitle_width) // 2
        draw.text((subtitle_x, 1000), subtitle_text, fill=cls.GRAY_900, font=text_font)
        
        # Kategorie Scores (ohne Emojis)
        y_offset = 1150
        category_scores = analysis.category_scores.all()[:4]
        
        for cat_score in category_scores:
            category_name = cls._get_category_name(cat_score.category)
            category_text = f"{category_name}: {float(cat_score.score):.1f}/5"
            
            text_bbox = draw.textbbox((0, 0), category_text, font=small_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (cls.IG_STORY_WIDTH - text_width) // 2
            
            draw.text((text_x, y_offset), category_text, fill=cls.GRAY_900, font=small_font)
            y_offset += 80
        
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
        Mit Kategorien-Durchschnitten
        
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
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 50)
            score_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 140)
            text_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 35)
            small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
        except:
            title_font = ImageFont.load_default()
            score_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Linke Seite: Score
        left_width = 500
        
        # Weißer Kreis für Score (links)
        circle_center_x = left_width // 2
        circle_center_y = cls.POST_HEIGHT // 2
        circle_radius = 150
        draw.ellipse(
            [
                circle_center_x - circle_radius,
                circle_center_y - circle_radius,
                circle_center_x + circle_radius,
                circle_center_y + circle_radius
            ],
            fill=cls.WHITE
        )
        
        # Score im Kreis
        score_text = f"{float(analysis.score_total):.1f}"
        score_bbox = draw.textbbox((0, 0), score_text, font=score_font)
        score_width = score_bbox[2] - score_bbox[0]
        score_height = score_bbox[3] - score_bbox[1]
        score_x = circle_center_x - score_width // 2
        score_y = circle_center_y - score_height // 2 - 15
        draw.text((score_x, score_y), score_text, fill=cls.RED_FLAG_COLOR, font=score_font)
        
        # "/5" unter dem Score
        subtitle_text = "/5"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=text_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = circle_center_x - subtitle_width // 2
        draw.text((subtitle_x, circle_center_y + 50), subtitle_text, fill=cls.GRAY_900, font=text_font)
        
        # Rechte Seite: Kategorien
        right_x_start = left_width + 50
        category_scores = analysis.category_scores.all()[:4]
        
        # Titel rechts
        categories_title = "Kategorien:"
        draw.text((right_x_start, 80), categories_title, fill=cls.WHITE, font=title_font)
        
        # Kategorien auflisten
        y_offset = 160
        for cat_score in category_scores:
            category_name = cls._get_category_name(cat_score.category)
            category_text = f"{category_name}: {float(cat_score.score):.1f}/5"
            
            draw.text((right_x_start, y_offset), category_text, fill=cls.WHITE, font=small_font)
            y_offset += 70
        
        # Titel oben
        title_text = "RedFlag Analyzer"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (cls.POST_WIDTH - title_width) // 2
        draw.text((title_x, 30), title_text, fill=cls.WHITE, font=title_font)
        
        # Footer
        footer_text = "Wie viele Red Flags hat deine Partnerin?"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=text_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (cls.POST_WIDTH - footer_width) // 2
        draw.text((footer_x, 560), footer_text, fill=cls.WHITE, font=text_font)
        
        # Speichere Bild
        filename = f'share_post_{analysis.id}.png'
        filepath = os.path.join(settings.MEDIA_ROOT, 'share_images', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img.save(filepath)
        
        return filepath
    
    @staticmethod
    def _get_category_name(category):
        """Helper: Kategorie zu Name (ohne Emojis)"""
        categories = {
            'TRUST': 'Vertrauen',
            'BEHAVIOR': 'Verhalten',
            'VALUES': 'Werte',
            'DYNAMICS': 'Dynamik',
        }
        return categories.get(category, category)
