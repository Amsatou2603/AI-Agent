import 'package:flutter/material.dart';
import '../models/query_response.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/chat_message_widget.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  final TextEditingController _questionController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;

  // Exemples de questions
  final List<String> _exampleQuestions = [
    "Quel est le taux de chômage à Dakar en 2024 ?",
    "Compare l'accès à Internet entre Dakar et Thiès en 2024",
    "Évolution de la population à Saint-Louis entre 2020 et 2024",
    "Classement des régions par taux de scolarisation en 2024",
    "Moyenne du taux de pauvreté en 2024",
  ];

  @override
  void dispose() {
    _questionController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _askQuestion(String question) async {
    if (question.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
      _messages.add(ChatMessage(
        question: question,
        isLoading: true,
      ));
    });

    _questionController.clear();
    _scrollToBottom();

    try {
      final response = await _apiService.askQuestion(question);

      setState(() {
        _messages[_messages.length - 1] = ChatMessage(
          question: question,
          response: response,
        );
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages[_messages.length - 1] = ChatMessage(
          question: question,
          error: e.toString().replaceAll('Exception: ', ''),
        );
        _isLoading = false;
      });
    }

    _scrollToBottom();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            _buildWarningBanner(),
            Expanded(
              child: _messages.isEmpty
                  ? _buildEmptyState()
                  : _buildMessagesList(),
            ),
            _buildInputSection(),
          ],
        ),
      ),
    );
  }

  /// En-tête style Apple
  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.paddingLarge,
        vertical: AppTheme.paddingMedium,
      ),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [AppTheme.secondary, Color(0xFF2d6a4f)],
        ),
        boxShadow: AppTheme.shadowMedium,
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(22),
            ),
            child: const Center(
              child: Text(
                '🇸🇳',
                style: TextStyle(fontSize: 24),
              ),
            ),
          ),
          const SizedBox(width: AppTheme.paddingMedium),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Agent IA Sénégal',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    letterSpacing: -0.3,
                  ),
                ),
                Text(
                  '14 régions • 2020-2024',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.75),
                    fontSize: 13,
                    fontWeight: FontWeight.w300,
                  ),
                ),
              ],
            ),
          ),
          // Bouton pour vider l'historique
          if (_messages.isNotEmpty)
            Material(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
              child: InkWell(
                onTap: () {
                  setState(() {
                    _messages.clear();
                  });
                },
                borderRadius: BorderRadius.circular(20),
                child: Container(
                  padding: const EdgeInsets.all(8),
                  child: const Icon(
                    Icons.refresh_rounded,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  /// Bandeau d'avertissement
  Widget _buildWarningBanner() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.paddingMedium,
        vertical: 10,
      ),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppTheme.error,
            AppTheme.error.withOpacity(0.8),
          ],
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.warning_amber_rounded,
            color: Colors.white.withOpacity(0.9),
            size: 16,
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              'Données pédagogiques fictives — aucune donnée officielle',
              style: TextStyle(
                color: Colors.white.withOpacity(0.95),
                fontSize: 12,
                fontWeight: FontWeight.w500,
                letterSpacing: 0.1,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  /// État vide avec exemples
  Widget _buildEmptyState() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppTheme.paddingLarge),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: AppTheme.paddingXLarge),
          Center(
            child: Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: AppTheme.secondary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(50),
              ),
              child: const Icon(
                Icons.chat_bubble_outline,
                size: 50,
                color: AppTheme.secondary,
              ),
            ),
          ),
          const SizedBox(height: AppTheme.paddingLarge),
          Text(
            'Posez votre question',
            style: Theme.of(context).textTheme.displaySmall,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppTheme.paddingSmall),
          Text(
            'Interrogez les statistiques régionales du Sénégal en langage naturel',
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppTheme.paddingXLarge),
          Text(
            'Exemples de questions',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppTheme.secondary,
                ),
          ),
          const SizedBox(height: AppTheme.paddingMedium),
          ..._exampleQuestions.map((question) => _buildExampleCard(question)),
        ],
      ),
    );
  }

  /// Carte d'exemple de question
  Widget _buildExampleCard(String question) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.paddingSmall),
      child: Material(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        child: InkWell(
          onTap: () {
            _questionController.text = question;
            _askQuestion(question);
          },
          borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
          child: Container(
            padding: const EdgeInsets.all(AppTheme.paddingMedium),
            decoration: BoxDecoration(
              border: Border.all(
                color: AppTheme.secondary.withOpacity(0.2),
                width: 1,
              ),
              borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppTheme.secondary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.chat_bubble_outline,
                    size: 18,
                    color: AppTheme.secondary,
                  ),
                ),
                const SizedBox(width: AppTheme.paddingMedium),
                Expanded(
                  child: Text(
                    question,
                    style: const TextStyle(
                      fontSize: 14,
                      color: AppTheme.textPrimary,
                      height: 1.4,
                    ),
                  ),
                ),
                const Icon(
                  Icons.arrow_forward_ios,
                  size: 14,
                  color: AppTheme.textTertiary,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Liste des messages
  Widget _buildMessagesList() {
    return ListView.separated(
      controller: _scrollController,
      padding: const EdgeInsets.all(AppTheme.paddingLarge),
      itemCount: _messages.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: AppTheme.paddingLarge),
      itemBuilder: (context, index) {
        final message = _messages[index];
        return ChatMessageWidget(
          question: message.question,
          response: message.response,
          isLoading: message.isLoading,
          error: message.error,
        );
      },
    );
  }

  /// Section de saisie
  Widget _buildInputSection() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.paddingMedium),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(
            child: TextField(
              controller: _questionController,
              maxLines: null,
              textCapitalization: TextCapitalization.sentences,
              decoration: InputDecoration(
                hintText: 'Posez votre question...',
                hintStyle: TextStyle(
                  color: AppTheme.textTertiary,
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: AppTheme.paddingMedium,
                  vertical: 12,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
                  borderSide: BorderSide(
                    color: AppTheme.textTertiary.withOpacity(0.3),
                  ),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
                  borderSide: BorderSide(
                    color: AppTheme.textTertiary.withOpacity(0.3),
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
                  borderSide: const BorderSide(
                    color: AppTheme.secondary,
                    width: 2,
                  ),
                ),
              ),
              onSubmitted: (value) => _askQuestion(value),
            ),
          ),
          const SizedBox(width: AppTheme.paddingSmall),
          Material(
            color: _isLoading ? AppTheme.textTertiary : AppTheme.secondary,
            borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
            child: InkWell(
              onTap: _isLoading
                  ? null
                  : () => _askQuestion(_questionController.text),
              borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
              child: Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
                ),
                child: const Icon(
                  Icons.arrow_upward_rounded,
                  color: Colors.white,
                  size: 24,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
