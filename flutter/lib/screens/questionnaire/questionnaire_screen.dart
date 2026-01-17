import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/questions_provider.dart';
import '../../providers/analysis_provider.dart';
import '../../providers/auth_provider.dart';
import '../results/results_screen.dart';
import '../auth/login_screen.dart';

class QuestionnaireScreen extends StatefulWidget {
  const QuestionnaireScreen({super.key});

  @override
  State<QuestionnaireScreen> createState() => _QuestionnaireScreenState();
}

class _QuestionnaireScreenState extends State<QuestionnaireScreen> {
  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    final questionsProvider = context.read<QuestionsProvider>();
    await questionsProvider.loadQuestions();
    await questionsProvider.loadProgress();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<QuestionsProvider>(
      builder: (context, questionsProvider, _) {
        if (questionsProvider.isLoading) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        if (questionsProvider.questions.isEmpty) {
          return Scaffold(
            appBar: AppBar(title: const Text('Fehler')),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64),
                  const SizedBox(height: 16),
                  Text(
                    questionsProvider.errorMessage ??
                        'Fragen konnten nicht geladen werden',
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => _loadQuestions(),
                    child: const Text('Erneut versuchen'),
                  ),
                ],
              ),
            ),
          );
        }

        final currentQuestion = questionsProvider.currentQuestion;
        if (currentQuestion == null) {
          return const Scaffold(
            body: Center(child: Text('Keine Frage gefunden')),
          );
        }

        final currentResponse =
            questionsProvider.getResponse(currentQuestion.key);

        return Scaffold(
          appBar: AppBar(
            title: Text(
              'Frage ${questionsProvider.currentIndex + 1}/${questionsProvider.questions.length}',
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.info_outline),
                onPressed: () => _showInfo(context),
              ),
            ],
          ),
          body: Column(
            children: [
              // Progress Bar
              LinearProgressIndicator(
                value: (questionsProvider.currentIndex + 1) /
                    questionsProvider.questions.length,
              ),
              
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Category Badge
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Chip(
                          label: Text(
                            _getCategoryName(currentQuestion.category.value),
                          ),
                          backgroundColor:
                              _getCategoryColor(context, currentQuestion.category.value),
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Question Text
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(20.0),
                          child: Text(
                            _getQuestionText(currentQuestion.key),
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 32),
                      
                      // Slider with Labels
                      Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                '1',
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              Text(
                                currentResponse?.toString() ?? '-',
                                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                      color: Theme.of(context).colorScheme.primary,
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                              Text(
                                '5',
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                            ],
                          ),
                          
                          Slider(
                            value: currentResponse?.toDouble() ?? 3.0,
                            min: 1,
                            max: 5,
                            divisions: 4,
                            label: currentResponse?.toString(),
                            onChanged: (value) {
                              questionsProvider.setResponse(
                                currentQuestion.key,
                                value.round(),
                              );
                            },
                          ),
                          
                          // Labels
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 12.0),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  'Trifft nicht zu',
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                                Text(
                                  'Trifft voll zu',
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 32),
                      
                      // Quick Response Buttons
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        alignment: WrapAlignment.center,
                        children: List.generate(5, (index) {
                          final value = index + 1;
                          final isSelected = currentResponse == value;
                          
                          return ActionChip(
                            label: Text(value.toString()),
                            backgroundColor: isSelected
                                ? Theme.of(context).colorScheme.primary
                                : null,
                            labelStyle: TextStyle(
                              color: isSelected
                                  ? Theme.of(context).colorScheme.onPrimary
                                  : null,
                            ),
                            onPressed: () {
                              questionsProvider.setResponse(
                                currentQuestion.key,
                                value,
                              );
                            },
                          );
                        }),
                      ),
                    ],
                  ),
                ),
              ),
              
              // Bottom Navigation
              Container(
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surface,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 4,
                      offset: const Offset(0, -2),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    if (questionsProvider.currentIndex > 0)
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: questionsProvider.previousQuestion,
                          icon: const Icon(Icons.arrow_back),
                          label: const Text('Zurück'),
                        ),
                      ),
                    
                    const SizedBox(width: 16),
                    
                    Expanded(
                      flex: 2,
                      child: questionsProvider.currentIndex <
                              questionsProvider.questions.length - 1
                          ? FilledButton.icon(
                              onPressed: currentResponse != null
                                  ? questionsProvider.nextQuestion
                                  : null,
                              icon: const Icon(Icons.arrow_forward),
                              label: const Text('Weiter'),
                            )
                          : FilledButton.icon(
                              onPressed: questionsProvider.validateComplete()
                                  ? () => _submit(context)
                                  : null,
                              icon: const Icon(Icons.check),
                              label: const Text('Abschließen'),
                            ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  String _getQuestionText(String key) {
    // Simplified - in production would use l10n
    final texts = {
      'father_absence': 'Sie ist zum größten Teil in ihrem Leben ohne biologischen Vater aufgewachsen.',
      'bad_father_relationship': 'Sie hat eine schlechte Beziehung zu ihrem Vater.',
      // Add more as needed - for now using key as fallback
    };
    return texts[key] ?? key.replaceAll('_', ' ');
  }

  String _getCategoryName(String category) {
    switch (category) {
      case 'TRUST':
        return 'Vertrauen';
      case 'BEHAVIOR':
        return 'Verhalten';
      case 'VALUES':
        return 'Werte';
      case 'DYNAMICS':
        return 'Dynamik';
      default:
        return category;
    }
  }

  Color _getCategoryColor(BuildContext context, String category) {
    switch (category) {
      case 'TRUST':
        return Colors.blue.shade100;
      case 'BEHAVIOR':
        return Colors.green.shade100;
      case 'VALUES':
        return Colors.orange.shade100;
      case 'DYNAMICS':
        return Colors.purple.shade100;
      default:
        return Colors.grey.shade100;
    }
  }

  void _showInfo(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Information'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Bewerten Sie jede Aussage von 1-5:'),
            const SizedBox(height: 12),
            const Text('1 = Trifft überhaupt nicht zu'),
            const Text('2 = Trifft eher nicht zu'),
            const Text('3 = Neutral'),
            const Text('4 = Trifft eher zu'),
            const Text('5 = Trifft voll und ganz zu'),
            const SizedBox(height: 16),
            Text(
              'Ihr Fortschritt wird automatisch gespeichert.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
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

  Future<void> _submit(BuildContext context) async {
    final questionsProvider = context.read<QuestionsProvider>();
    final analysisProvider = context.read<AnalysisProvider>();
    final authProvider = context.read<AuthProvider>();

    // Check if user is authenticated
    if (!authProvider.isAuthenticated) {
      final shouldLogin = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Anmelden erforderlich'),
          content: const Text(
            'Um die Analyse zu speichern und zu sehen, müssen Sie sich anmelden. '
            'Möchten Sie sich jetzt anmelden?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Abbrechen'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Anmelden'),
            ),
          ],
        ),
      );

      if (shouldLogin == true && mounted) {
        await Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => const LoginScreen(),
          ),
        );
        
        // Check again after login
        if (!authProvider.isAuthenticated) {
          return;
        }
      } else {
        return;
      }
    }

    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );

    // Submit analysis
    final responses = questionsProvider.getResponsesForSubmission();
    final analysis = await analysisProvider.createAnalysis(responses);

    // Hide loading
    if (mounted) Navigator.pop(context);

    if (analysis != null && mounted) {
      // Clear questionnaire
      await questionsProvider.reset();
      
      // Navigate to results
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) => const ResultsScreen(),
        ),
      );
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            analysisProvider.errorMessage ?? 'Fehler beim Erstellen der Analyse',
          ),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }
}
