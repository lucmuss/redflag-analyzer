import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'config/app_config.dart';
import 'services/api_service.dart';
import 'services/storage_service.dart';
import 'providers/auth_provider.dart';
import 'providers/questions_provider.dart';
import 'providers/analysis_provider.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize storage with error handling
  final storageService = StorageService();
  try {
    await storageService.init();
  } catch (e) {
    debugPrint('Storage initialization error: $e');
    // Continue anyway - app can work without storage
  }
  
  runApp(RedFlagAnalyzerApp(storageService: storageService));
}

class RedFlagAnalyzerApp extends StatelessWidget {
  final StorageService storageService;
  
  const RedFlagAnalyzerApp({
    super.key,
    required this.storageService,
  });

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Services
        Provider<StorageService>.value(value: storageService),
        Provider<ApiService>(create: (_) => ApiService()),
        
        // Providers
        ChangeNotifierProxyProvider<ApiService, AuthProvider>(
          create: (context) => AuthProvider(
            apiService: context.read<ApiService>(),
            storageService: storageService,
          )..init(),
          update: (context, apiService, previous) =>
              previous ?? AuthProvider(
                apiService: apiService,
                storageService: storageService,
              ),
        ),
        
        ChangeNotifierProxyProvider<ApiService, QuestionsProvider>(
          create: (context) => QuestionsProvider(
            apiService: context.read<ApiService>(),
            storageService: storageService,
          ),
          update: (context, apiService, previous) =>
              previous ?? QuestionsProvider(
                apiService: apiService,
                storageService: storageService,
              ),
        ),
        
        ChangeNotifierProxyProvider<ApiService, AnalysisProvider>(
          create: (context) => AnalysisProvider(
            apiService: context.read<ApiService>(),
          ),
          update: (context, apiService, previous) =>
              previous ?? AnalysisProvider(apiService: apiService),
        ),
      ],
      child: MaterialApp(
        title: AppConfig.appName,
        debugShowCheckedModeBanner: false,
        
        // Material Design 3 Theme
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.red,
            brightness: Brightness.light,
          ),
          appBarTheme: const AppBarTheme(
            centerTitle: true,
            elevation: 0,
          ),
          cardTheme: CardThemeData(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
          ),
          filledButtonTheme: FilledButtonThemeData(
            style: FilledButton.styleFrom(
              minimumSize: const Size.fromHeight(56),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
        
        // Dark Theme (optional)
        darkTheme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.red,
            brightness: Brightness.dark,
          ),
        ),
        
        // Start Screen
        home: const HomeScreen(),
        
        // Routes werden später hinzugefügt
        // routes: {
        //   '/login': (context) => LoginScreen(),
        //   '/register': (context) => RegisterScreen(),
        //   '/questionnaire': (context) => QuestionnaireScreen(),
        //   '/results': (context) => ResultsScreen(),
        // },
      ),
    );
  }
}
