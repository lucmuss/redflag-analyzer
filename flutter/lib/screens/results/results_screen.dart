import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/analysis_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/charts/score_gauge.dart';
import '../../widgets/charts/category_radar_chart.dart';
import '../../services/pdf_service.dart';

class ResultsScreen extends StatelessWidget {
  const ResultsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Analyseergebnis'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () => _shareResults(context),
          ),
        ],
      ),
      body: Consumer2<AnalysisProvider, AuthProvider>(
        builder: (context, analysisProvider, authProvider, _) {
          final analysis = analysisProvider.currentAnalysis;

          if (analysis == null) {
            return const Center(
              child: Text('Keine Analyse gefunden'),
            );
          }

          if (!analysis.isUnlocked) {
            return _buildLockedView(context, analysis, authProvider);
          }

          return _buildUnlockedView(context, analysis);
        },
      ),
    );
  }

  Widget _buildLockedView(
    BuildContext context,
    analysis,
    AuthProvider authProvider,
  ) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        children: [
          // Lock Icon
          Icon(
            Icons.lock_outline,
            size: 80,
            color: Theme.of(context).colorScheme.primary,
          ),
          
          const SizedBox(height: 24),
          
          Text(
            'Analyse gesperrt',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          
          const SizedBox(height: 16),
          
          Text(
            'Verwenden Sie einen Credit, um das vollständige Ergebnis freizuschalten.',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          
          const SizedBox(height: 32),
          
          // Credits Info
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Ihre Credits:'),
                      Text(
                        '${authProvider.credits}',
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              color: Theme.of(context).colorScheme.primary,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 20),
                  
                  FilledButton.icon(
                    onPressed: authProvider.credits > 0
                        ? () => _unlockAnalysis(context)
                        : null,
                    icon: const Icon(Icons.lock_open),
                    label: const Text('Jetzt freischalten (1 Credit)'),
                  ),
                  
                  if (authProvider.credits == 0) ...[
                    const SizedBox(height: 16),
                    OutlinedButton.icon(
                      onPressed: () => _buyCredits(context),
                      icon: const Icon(Icons.shopping_cart),
                      label: const Text('Credits kaufen (5€)'),
                    ),
                  ],
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Preview
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Im freigeschalteten Ergebnis:',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  _buildFeature(context, Icons.analytics, 'Gesamtscore (0-10)'),
                  _buildFeature(context, Icons.radar, 'Radar Chart (4 Kategorien)'),
                  _buildFeature(context, Icons.warning, 'Top 5 Red Flags'),
                  _buildFeature(context, Icons.picture_as_pdf, 'PDF Export'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUnlockedView(BuildContext context, analysis) {
    final scoreTotal = analysis.scoreTotal ?? 0.0;
    final categoryScores = analysis.categoryScores;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Score Gauge (Tachometer)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: ScoreGauge(score: scoreTotal),
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Radar Chart
          if (categoryScores != null) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: CategoryRadarChart(categoryScores: categoryScores),
              ),
            ),
            const SizedBox(height: 24),
          ],
          
          // Category Scores (as backup/text)
          if (categoryScores != null) ...[
            Text(
              'Detaillierte Scores',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            _buildCategoryCard(context, 'Vertrauen', categoryScores.trust, Colors.blue),
            _buildCategoryCard(context, 'Verhalten', categoryScores.behavior, Colors.green),
            _buildCategoryCard(context, 'Werte', categoryScores.values, Colors.orange),
            _buildCategoryCard(context, 'Dynamik', categoryScores.dynamics, Colors.purple),
          ],
          
          const SizedBox(height: 24),
          
          // Top Red Flags
          if (analysis.topRedFlags != null && analysis.topRedFlags!.isNotEmpty) ...[
            Text(
              'Top Red Flags',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            ...analysis.topRedFlags!.take(5).map((flag) {
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  leading: const Icon(Icons.warning, color: Colors.red),
                  title: Text(flag.key.replaceAll('_', ' ')),
                  trailing: Text(
                    'Impact: ${flag.impact.toStringAsFixed(1)}',
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                ),
              );
            }),
          ],
          
          const SizedBox(height: 32),
          
          // Actions
          FilledButton.icon(
            onPressed: () => _exportPDF(context),
            icon: const Icon(Icons.picture_as_pdf),
            label: const Text('Als PDF exportieren'),
          ),
          
          const SizedBox(height: 16),
          
          OutlinedButton.icon(
            onPressed: () => Navigator.of(context).popUntil((route) => route.isFirst),
            icon: const Icon(Icons.home),
            label: const Text('Zurück zur Startseite'),
          ),
        ],
      ),
    );
  }

  Widget _buildFeature(BuildContext context, IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        children: [
          Icon(icon, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 12),
          Text(text),
        ],
      ),
    );
  }

  Widget _buildCategoryCard(
    BuildContext context,
    String title,
    double score,
    Color color,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: score / 10,
                    backgroundColor: color.withOpacity(0.2),
                    valueColor: AlwaysStoppedAnimation(color),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 16),
            Text(
              score.toStringAsFixed(1),
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(BuildContext context, double score) {
    if (score < 3) return Colors.green;
    if (score < 5) return Colors.orange;
    if (score < 7) return Colors.deepOrange;
    return Colors.red;
  }

  String _getScoreLabel(double score) {
    if (score < 3) return 'Niedrig - Wenig Risiko';
    if (score < 5) return 'Mittel - Einige Bedenken';
    if (score < 7) return 'Hoch - Viele Warnsignale';
    return 'Sehr Hoch - Kritisch';
  }

  Future<void> _unlockAnalysis(BuildContext context) async {
    final analysisProvider = context.read<AnalysisProvider>();
    final authProvider = context.read<AuthProvider>();
    final analysis = analysisProvider.currentAnalysis;

    if (analysis == null) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Analyse freischalten?'),
        content: const Text(
          'Möchten Sie 1 Credit verwenden, um diese Analyse freizuschalten?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Freischalten'),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      final success = await analysisProvider.unlockAnalysis(analysis.id);
      if (success && context.mounted) {
        authProvider.deductCredit();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Analyse freigeschaltet!')),
        );
      }
    }
  }

  void _buyCredits(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Credits kaufen'),
        content: const Text(
          'In-App-Purchase Integration kommt in der nächsten Version!\n\n'
          'Preis: 5€ für 1 Credit',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _shareResults(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Share-Funktion kommt bald!')),
    );
  }

  Future<void> _exportPDF(BuildContext context) async {
    final analysisProvider = context.read<AnalysisProvider>();
    final authProvider = context.read<AuthProvider>();
    final analysis = analysisProvider.currentAnalysis;

    if (analysis == null || !analysis.isUnlocked) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Analyse muss freigeschaltet sein')),
        );
      }
      return;
    }

    // Show loading
    if (context.mounted) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    try {
      final pdfService = PdfService();
      final pdfBytes = await pdfService.generateAnalysisPdf(
        analysis,
        userName: authProvider.currentUser?.email,
      );

      // Hide loading
      if (context.mounted) Navigator.pop(context);

      // Share PDF
      await pdfService.sharePdf(
        pdfBytes,
        'redflag_analysis_${DateTime.now().millisecondsSinceEpoch}.pdf',
      );

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('PDF erfolgreich erstellt!')),
        );
      }
    } catch (e) {
      // Hide loading
      if (context.mounted) Navigator.pop(context);

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Fehler beim PDF-Export: ${e.toString()}'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }
}
