import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import 'auth/login_screen.dart';
import 'questionnaire/questionnaire_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Consumer<AuthProvider>(
          builder: (context, authProvider, _) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 40),
                  
                  // Logo/Icon
                  Icon(
                    Icons.favorite_border,
                    size: 80,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Title
                  Text(
                    'RedFlag Analyzer',
                    style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                    textAlign: TextAlign.center,
                  ),
                  
                  const SizedBox(height: 12),
                  
                  // Subtitle
                  Text(
                    'Objektive Beurteilung von Beziehungen',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                    textAlign: TextAlign.center,
                  ),
                  
                  const SizedBox(height: 48),
                  
                  // Info Card
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.info_outline,
                                color: Theme.of(context).colorScheme.primary,
                              ),
                              const SizedBox(width: 12),
                              Text(
                                'Wie funktioniert es?',
                                style: Theme.of(context).textTheme.titleLarge,
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          _buildInfoItem(
                            context,
                            Icons.question_answer,
                            '65 Fragen beantworten',
                            'Bewerte Aussagen von 1 (trifft nicht zu) bis 5 (trifft voll zu)',
                          ),
                          _buildInfoItem(
                            context,
                            Icons.analytics,
                            'Analyse erhalten',
                            'Detaillierte Auswertung mit Gesamtscore und Kategorien',
                          ),
                          _buildInfoItem(
                            context,
                            Icons.share,
                            'Ergebnis teilen',
                            'PDF exportieren und mit Freunden teilen',
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // Credits Info (if authenticated)
                  if (authProvider.isAuthenticated) ...[
                    Card(
                      color: Theme.of(context).colorScheme.primaryContainer,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Row(
                          children: [
                            Icon(
                              Icons.stars,
                              color: Theme.of(context).colorScheme.onPrimaryContainer,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'Credits: ${authProvider.credits}',
                                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                                    ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                  ],
                  
                  // CTA Button
                  FilledButton.icon(
                    onPressed: () => _startAnalysis(context, authProvider),
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Jetzt starten'),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Login Button (if not authenticated)
                  if (!authProvider.isAuthenticated)
                    OutlinedButton.icon(
                      onPressed: () => _navigateToLogin(context),
                      icon: const Icon(Icons.login),
                      label: const Text('Bereits registriert? Anmelden'),
                    ),
                  
                  // Logout Button (if authenticated)
                  if (authProvider.isAuthenticated)
                    OutlinedButton.icon(
                      onPressed: () => _logout(context, authProvider),
                      icon: const Icon(Icons.logout),
                      label: const Text('Abmelden'),
                    ),
                  
                  const SizedBox(height: 32),
                  
                  // Footer Info
                  Center(
                    child: Text(
                      '1 kostenlose Analyse • Weitere Analysen: 5€',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context).colorScheme.onSurfaceVariant,
                          ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildInfoItem(
    BuildContext context,
    IconData icon,
    String title,
    String description,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            icon,
            size: 24,
            color: Theme.of(context).colorScheme.secondary,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _startAnalysis(BuildContext context, AuthProvider authProvider) {
    if (authProvider.isAuthenticated) {
      // Navigate to questionnaire
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => const QuestionnaireScreen(),
        ),
      );
    } else {
      // Show dialog: Login or continue as guest
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Analyse starten'),
          content: const Text(
            'Möchten Sie sich anmelden, um Ihre Analysen zu speichern, '
            'oder als Gast fortfahren?',
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const QuestionnaireScreen(),
                  ),
                );
              },
              child: const Text('Als Gast'),
            ),
            FilledButton(
              onPressed: () {
                Navigator.pop(context);
                _navigateToLogin(context);
              },
              child: const Text('Anmelden'),
            ),
          ],
        ),
      );
    }
  }

  void _navigateToLogin(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const LoginScreen(),
      ),
    );
  }

  Future<void> _logout(BuildContext context, AuthProvider authProvider) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Abmelden'),
        content: const Text('Möchten Sie sich wirklich abmelden?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Abmelden'),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      await authProvider.logout();
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Erfolgreich abgemeldet')),
        );
      }
    }
  }
}
