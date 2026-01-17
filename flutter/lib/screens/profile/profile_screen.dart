import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/auth_provider.dart';
import '../../providers/analysis_provider.dart';
import '../../models/user.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _ageController = TextEditingController();
  final _countryController = TextEditingController();
  String? _selectedGender;

  @override
  void initState() {
    super.initState();
    _loadUserProfile();
  }

  void _loadUserProfile() {
    final authProvider = context.read<AuthProvider>();
    final profile = authProvider.currentUser?.profile;
    
    if (profile != null) {
      _ageController.text = profile.age?.toString() ?? '';
      _countryController.text = profile.country ?? '';
      _selectedGender = profile.gender;
    }
  }

  @override
  void dispose() {
    _ageController.dispose();
    _countryController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profil'),
      ),
      body: Consumer2<AuthProvider, AnalysisProvider>(
        builder: (context, authProvider, analysisProvider, _) {
          final user = authProvider.currentUser;
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // User Info Card
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      children: [
                        Icon(
                          Icons.account_circle,
                          size: 80,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          user?.email ?? 'Gast',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Mitglied seit ${user?.createdAt.toString().split(' ')[0] ?? 'Nicht angemeldet'}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Credits Card
                Card(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.stars,
                              color: Theme.of(context).colorScheme.onPrimaryContainer,
                            ),
                            const SizedBox(width: 12),
                            Text(
                              'Credits',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    color: Theme.of(context).colorScheme.onPrimaryContainer,
                                  ),
                            ),
                          ],
                        ),
                        Text(
                          '${authProvider.credits}',
                          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                color: Theme.of(context).colorScheme.onPrimaryContainer,
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Profile Form
                Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Profil bearbeiten',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 16),
                      
                      TextFormField(
                        controller: _ageController,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'Alter',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.cake),
                        ),
                        validator: (value) {
                          if (value != null && value.isNotEmpty) {
                            final age = int.tryParse(value);
                            if (age == null || age < 18 || age > 100) {
                              return 'Bitte gültiges Alter eingeben (18-100)';
                            }
                          }
                          return null;
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      TextFormField(
                        controller: _countryController,
                        decoration: const InputDecoration(
                          labelText: 'Land',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.public),
                        ),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      DropdownButtonFormField<String>(
                        value: _selectedGender,
                        decoration: const InputDecoration(
                          labelText: 'Geschlecht',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.person),
                        ),
                        items: const [
                          DropdownMenuItem(value: 'male', child: Text('Männlich')),
                          DropdownMenuItem(value: 'female', child: Text('Weiblich')),
                          DropdownMenuItem(value: 'other', child: Text('Divers')),
                          DropdownMenuItem(value: 'prefer_not_to_say', child: Text('Keine Angabe')),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _selectedGender = value;
                          });
                        },
                      ),
                      
                      const SizedBox(height: 24),
                      
                      FilledButton.icon(
                        onPressed: () => _saveProfile(authProvider),
                        icon: const Icon(Icons.save),
                        label: const Text('Profil speichern'),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 32),
                
                // Statistics
                Text(
                  'Statistiken',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 16),
                
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        _buildStatRow(
                          context,
                          Icons.analytics,
                          'Analysen gesamt',
                          '${analysisProvider.analyses.length}',
                        ),
                        const Divider(),
                        _buildStatRow(
                          context,
                          Icons.lock_open,
                          'Freigeschaltet',
                          '${analysisProvider.unlockedAnalyses.length}',
                        ),
                        const Divider(),
                        _buildStatRow(
                          context,
                          Icons.lock,
                          'Gesperrt',
                          '${analysisProvider.lockedAnalyses.length}',
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildStatRow(
    BuildContext context,
    IconData icon,
    String label,
    String value,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(icon, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
        ],
      ),
    );
  }

  Future<void> _saveProfile(AuthProvider authProvider) async {
    if (!_formKey.currentState!.validate()) return;

    final profile = UserProfile(
      age: _ageController.text.isNotEmpty 
          ? int.tryParse(_ageController.text) 
          : null,
      country: _countryController.text.isNotEmpty 
          ? _countryController.text 
          : null,
      gender: _selectedGender,
    );

    final success = await authProvider.updateProfile(profile);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            success 
                ? 'Profil erfolgreich gespeichert' 
                : 'Fehler beim Speichern',
          ),
          backgroundColor: success 
              ? Theme.of(context).colorScheme.primary 
              : Theme.of(context).colorScheme.error,
        ),
      );
    }
  }
}
