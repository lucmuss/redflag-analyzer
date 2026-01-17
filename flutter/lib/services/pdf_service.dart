import 'dart:typed_data';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:logger/logger.dart';

import '../models/analysis.dart';

/// PDF Generation Service
class PdfService {
  final Logger _logger = Logger();

  /// Generate PDF from Analysis
  Future<Uint8List> generateAnalysisPdf(
    Analysis analysis, {
    String? userName,
  }) async {
    final pdf = pw.Document();

    // Load logo (if available)
    // For now, we'll use text-based branding

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(32),
        build: (context) => [
          // Header
          _buildHeader(userName),
          pw.SizedBox(height: 24),
          
          // Overall Score
          _buildScoreSection(analysis),
          pw.SizedBox(height: 24),
          
          // Category Scores
          if (analysis.categoryScores != null) ...[
            _buildCategorySection(analysis.categoryScores!),
            pw.SizedBox(height: 24),
          ],
          
          // Top Red Flags
          if (analysis.topRedFlags != null && analysis.topRedFlags!.isNotEmpty) ...[
            _buildRedFlagsSection(analysis.topRedFlags!),
            pw.SizedBox(height: 24),
          ],
          
          // Footer
          pw.Spacer(),
          _buildFooter(),
        ],
      ),
    );

    _logger.d('PDF generated successfully');
    return pdf.save();
  }

  pw.Widget _buildHeader(String? userName) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Row(
          mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
          children: [
            pw.Column(
              crossAxisAlignment: pw.CrossAxisAlignment.start,
              children: [
                pw.Text(
                  'RedFlag Analyzer',
                  style: pw.TextStyle(
                    fontSize: 28,
                    fontWeight: pw.FontWeight.bold,
                    color: PdfColors.red700,
                  ),
                ),
                pw.SizedBox(height: 4),
                pw.Text(
                  'Beziehungsanalyse-Bericht',
                  style: const pw.TextStyle(
                    fontSize: 14,
                    color: PdfColors.grey700,
                  ),
                ),
              ],
            ),
            pw.Column(
              crossAxisAlignment: pw.CrossAxisAlignment.end,
              children: [
                if (userName != null) ...[
                  pw.Text(
                    userName,
                    style: pw.TextStyle(
                      fontSize: 12,
                      fontWeight: pw.FontWeight.bold,
                    ),
                  ),
                  pw.SizedBox(height: 4),
                ],
                pw.Text(
                  DateTime.now().toString().split(' ')[0],
                  style: const pw.TextStyle(
                    fontSize: 10,
                    color: PdfColors.grey600,
                  ),
                ),
              ],
            ),
          ],
        ),
        pw.SizedBox(height: 16),
        pw.Divider(thickness: 2, color: PdfColors.red700),
      ],
    );
  }

  pw.Widget _buildScoreSection(Analysis analysis) {
    final score = analysis.scoreTotal ?? 0.0;
    final color = _getScoreColor(score);
    final label = _getScoreLabel(score);

    return pw.Container(
      padding: const pw.EdgeInsets.all(24),
      decoration: pw.BoxDecoration(
        color: PdfColors.grey100,
        borderRadius: pw.BorderRadius.circular(12),
        border: pw.Border.all(color: color, width: 2),
      ),
      child: pw.Column(
        children: [
          pw.Text(
            'Gesamtscore',
            style: pw.TextStyle(
              fontSize: 18,
              fontWeight: pw.FontWeight.bold,
            ),
          ),
          pw.SizedBox(height: 16),
          pw.Text(
            score.toStringAsFixed(1),
            style: pw.TextStyle(
              fontSize: 48,
              fontWeight: pw.FontWeight.bold,
              color: color,
            ),
          ),
          pw.SizedBox(height: 8),
          pw.Text(
            label,
            style: const pw.TextStyle(
              fontSize: 14,
              color: PdfColors.grey700,
            ),
            textAlign: pw.TextAlign.center,
          ),
          pw.SizedBox(height: 16),
          _buildScoreBar(score),
        ],
      ),
    );
  }

  pw.Widget _buildScoreBar(double score) {
    return pw.Container(
      height: 20,
      decoration: pw.BoxDecoration(
        borderRadius: pw.BorderRadius.circular(10),
        color: PdfColors.grey300,
      ),
      child: pw.Stack(
        children: [
          pw.Container(
            width: (score / 10) * 400,
            decoration: pw.BoxDecoration(
              borderRadius: pw.BorderRadius.circular(10),
              color: _getScoreColor(score),
            ),
          ),
        ],
      ),
    );
  }

  pw.Widget _buildCategorySection(CategoryScores scores) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          'Kategorie-Scores',
          style: pw.TextStyle(
            fontSize: 20,
            fontWeight: pw.FontWeight.bold,
          ),
        ),
        pw.SizedBox(height: 16),
        _buildCategoryRow('Vertrauen (TRUST)', scores.trust, PdfColors.blue),
        pw.SizedBox(height: 12),
        _buildCategoryRow('Verhalten (BEHAVIOR)', scores.behavior, PdfColors.green),
        pw.SizedBox(height: 12),
        _buildCategoryRow('Werte (VALUES)', scores.values, PdfColors.orange),
        pw.SizedBox(height: 12),
        _buildCategoryRow('Dynamik (DYNAMICS)', scores.dynamics, PdfColors.purple),
      ],
    );
  }

  pw.Widget _buildCategoryRow(String title, double score, PdfColor color) {
    return pw.Container(
      padding: const pw.EdgeInsets.all(12),
      decoration: pw.BoxDecoration(
        border: pw.Border.all(color: PdfColors.grey400),
        borderRadius: pw.BorderRadius.circular(8),
      ),
      child: pw.Row(
        children: [
          pw.Expanded(
            flex: 3,
            child: pw.Text(
              title,
              style: pw.TextStyle(
                fontSize: 14,
                fontWeight: pw.FontWeight.bold,
              ),
            ),
          ),
          pw.Expanded(
            flex: 5,
            child: pw.Container(
              height: 16,
              decoration: pw.BoxDecoration(
                borderRadius: pw.BorderRadius.circular(8),
                color: PdfColors.grey300,
              ),
              child: pw.Stack(
                children: [
                  pw.Container(
                    width: (score / 10) * 250,
                    decoration: pw.BoxDecoration(
                      borderRadius: pw.BorderRadius.circular(8),
                      color: color,
                    ),
                  ),
                ],
              ),
            ),
          ),
          pw.SizedBox(width: 16),
          pw.Text(
            score.toStringAsFixed(1),
            style: pw.TextStyle(
              fontSize: 16,
              fontWeight: pw.FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  pw.Widget _buildRedFlagsSection(List<RedFlag> redFlags) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          'Top Red Flags',
          style: pw.TextStyle(
            fontSize: 20,
            fontWeight: pw.FontWeight.bold,
          ),
        ),
        pw.SizedBox(height: 16),
        ...redFlags.take(5).map((flag) => pw.Container(
              margin: const pw.EdgeInsets.only(bottom: 8),
              padding: const pw.EdgeInsets.all(12),
              decoration: pw.BoxDecoration(
                color: PdfColors.red50,
                border: pw.Border.all(color: PdfColors.red200),
                borderRadius: pw.BorderRadius.circular(8),
              ),
              child: pw.Row(
                children: [
                  pw.Container(
                    width: 8,
                    height: 8,
                    decoration: const pw.BoxDecoration(
                      color: PdfColors.red,
                      shape: pw.BoxShape.circle,
                    ),
                  ),
                  pw.SizedBox(width: 12),
                  pw.Expanded(
                    child: pw.Text(
                      flag.key.replaceAll('_', ' ').toUpperCase(),
                      style: const pw.TextStyle(fontSize: 12),
                    ),
                  ),
                  pw.Text(
                    'Impact: ${flag.impact.toStringAsFixed(1)}',
                    style: pw.TextStyle(
                      fontSize: 11,
                      fontWeight: pw.FontWeight.bold,
                      color: PdfColors.red700,
                    ),
                  ),
                ],
              ),
            )),
      ],
    );
  }

  pw.Widget _buildFooter() {
    return pw.Column(
      children: [
        pw.Divider(thickness: 1, color: PdfColors.grey400),
        pw.SizedBox(height: 8),
        pw.Row(
          mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
          children: [
            pw.Text(
              'Erstellt mit RedFlag Analyzer',
              style: const pw.TextStyle(
                fontSize: 9,
                color: PdfColors.grey600,
              ),
            ),
            pw.Text(
              'www.redflag-analyzer.app',
              style: pw.TextStyle(
                fontSize: 9,
                color: PdfColors.blue700,
                decoration: pw.TextDecoration.underline,
              ),
            ),
          ],
        ),
        pw.SizedBox(height: 4),
        pw.Text(
          'Diese Analyse dient nur zu Informationszwecken und ersetzt keine professionelle Beratung.',
          style: const pw.TextStyle(
            fontSize: 8,
            color: PdfColors.grey500,
          ),
          textAlign: pw.TextAlign.center,
        ),
      ],
    );
  }

  PdfColor _getScoreColor(double score) {
    if (score < 3) return PdfColors.green700;
    if (score < 6) return PdfColors.orange700;
    return PdfColors.red700;
  }

  String _getScoreLabel(double score) {
    if (score < 3) return 'Niedrig - Wenig Risiko';
    if (score < 6) return 'Mittel - Einige Bedenken';
    if (score < 8) return 'Hoch - Viele Warnsignale';
    return 'Sehr Hoch - Kritisch';
  }

  /// Share or save PDF
  Future<void> sharePdf(Uint8List pdfBytes, String fileName) async {
    await Printing.sharePdf(
      bytes: pdfBytes,
      filename: fileName,
    );
  }

  /// Print PDF
  Future<void> printPdf(Uint8List pdfBytes) async {
    await Printing.layoutPdf(
      onLayout: (format) async => pdfBytes,
    );
  }
}
