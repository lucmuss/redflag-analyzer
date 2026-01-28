"""
PDF Export für Analysis Reports
Nutzt WeasyPrint für HTML-to-PDF Conversion
"""
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import logging

logger = logging.getLogger(__name__)


class AnalysisPDFExporter:
    """
    PDF-Export für Analysis mit professionellem Layout.
    """
    
    def __init__(self, analysis):
        self.analysis = analysis
        self.user = analysis.user
    
    def generate_pdf(self) -> HttpResponse:
        """
        Generiere PDF und return HttpResponse.
        """
        try:
            # Render HTML Template
            html_string = self._render_html()
            
            # WeasyPrint Configuration
            font_config = FontConfiguration()
            
            # Custom CSS für PDF
            css = CSS(string=self._get_custom_css(), font_config=font_config)
            
            # HTML zu PDF konvertieren
            html = HTML(string=html_string)
            pdf = html.write_pdf(stylesheets=[css], font_config=font_config)
            
            # HTTP Response erstellen
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="redflag_analysis_{self.analysis.id}.pdf"'
            
            logger.info(f"PDF export successful for analysis {self.analysis.id}")
            return response
            
        except Exception as e:
            logger.error(f"PDF export failed for analysis {self.analysis.id}: {str(e)}")
            raise
    
    def _render_html(self) -> str:
        """
        Render HTML Template für PDF.
        """
        # Berechne alle notwendigen Daten
        category_scores = {
            cs.category: float(cs.score) 
            for cs in self.analysis.category_scores.all()
        }
        
        top_red_flags = self.analysis.get_top_red_flags(limit=10)
        
        context = {
            'analysis': self.analysis,
            'user': self.user,
            'category_scores': category_scores,
            'top_red_flags': top_red_flags,
            'score_total': float(self.analysis.score_total),
            'partner_name': self.analysis.partner_name or 'Unbekannt',
            'partner_age': self.analysis.partner_age or 'N/A',
        }
        
        return render_to_string('analyses/pdf_report.html', context)
    
    def _get_custom_css(self) -> str:
        """
        Custom CSS für PDF-Styling.
        """
        return """
        @page {
            size: A4;
            margin: 2cm;
            @bottom-right {
                content: "Seite " counter(page) " von " counter(pages);
                font-size: 10px;
                color: #666;
            }
        }
        
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }
        
        h1 {
            color: #EF4444;
            font-size: 24pt;
            margin-bottom: 20px;
            border-bottom: 3px solid #EF4444;
            padding-bottom: 10px;
        }
        
        h2 {
            color: #333;
            font-size: 18pt;
            margin-top: 25px;
            margin-bottom: 15px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 5px;
        }
        
        h3 {
            color: #666;
            font-size: 14pt;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .score-card {
            background: #f9fafb;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .score-high {
            background: #fee2e2;
            border-color: #EF4444;
        }
        
        .score-medium {
            background: #fef3c7;
            border-color: #f59e0b;
        }
        
        .score-low {
            background: #d1fae5;
            border-color: #10b981;
        }
        
        .red-flag-item {
            border-left: 4px solid #EF4444;
            padding-left: 15px;
            margin-bottom: 15px;
            page-break-inside: avoid;
        }
        
        .category-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        
        th {
            background: #f3f4f6;
            font-weight: bold;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            font-size: 9pt;
            color: #666;
        }
        
        .watermark {
            position: fixed;
            bottom: 10px;
            right: 10px;
            opacity: 0.3;
            font-size: 8pt;
            color: #999;
        }
        """


def export_analysis_pdf(analysis):
    """
    Helper function für schnellen PDF Export.
    """
    exporter = AnalysisPDFExporter(analysis)
    return exporter.generate_pdf()
