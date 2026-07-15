import 'package:flutter/material.dart';
import '../models/query_response.dart';
import '../theme/app_theme.dart';
import 'data_table_widget.dart';
import 'chart_widget.dart';

/// Widget pour afficher un message de conversation
class ChatMessageWidget extends StatelessWidget {
  final String question;
  final QueryResponse? response;
  final bool isLoading;
  final String? error;

  const ChatMessageWidget({
    super.key,
    required this.question,
    this.response,
    this.isLoading = false,
    this.error,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Question de l'utilisateur
        _buildQuestionBubble(),
        
        const SizedBox(height: AppTheme.paddingMedium),
        
        // Réponse ou chargement
        if (isLoading)
          _buildLoadingIndicator()
        else if (error != null)
          _buildErrorCard()
        else if (response != null)
          _buildResponseCard(),
      ],
    );
  }

  /// Bulle de question style Apple
  Widget _buildQuestionBubble() {
    return Align(
      alignment: Alignment.centerRight,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 300),
        padding: const EdgeInsets.symmetric(
          horizontal: AppTheme.paddingMedium,
          vertical: 12,
        ),
        decoration: BoxDecoration(
          color: AppTheme.primary,
          borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
          boxShadow: AppTheme.shadowLight,
        ),
        child: Text(
          question,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 15,
            height: 1.4,
          ),
        ),
      ),
    );
  }

  /// Indicateur de chargement
  Widget _buildLoadingIndicator() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.paddingLarge),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        boxShadow: AppTheme.shadowLight,
      ),
      child: Row(
        children: [
          SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2.5,
              valueColor: AlwaysStoppedAnimation<Color>(
                AppTheme.primary.withOpacity(0.8),
              ),
            ),
          ),
          const SizedBox(width: AppTheme.paddingMedium),
          Text(
            'Analyse en cours...',
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 15,
            ),
          ),
        ],
      ),
    );
  }

  /// Carte d'erreur
  Widget _buildErrorCard() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.paddingLarge),
      decoration: BoxDecoration(
        color: AppTheme.error.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        border: Border.all(color: AppTheme.error.withOpacity(0.3), width: 1),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.error_outline, color: AppTheme.error, size: 24),
          const SizedBox(width: AppTheme.paddingMedium),
          Expanded(
            child: Text(
              error!,
              style: const TextStyle(
                color: AppTheme.error,
                fontSize: 15,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Carte de réponse
  Widget _buildResponseCard() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.paddingLarge),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        boxShadow: AppTheme.shadowLight,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Réponse textuelle
          _buildAnswerText(),
          
          // Tableau de données
          if (response!.table.isNotEmpty) ...[
            const SizedBox(height: AppTheme.paddingLarge),
            const Divider(height: 1),
            const SizedBox(height: AppTheme.paddingLarge),
            DataTableWidget(data: response!.table),
          ],
          
          // Graphique
          if (response!.chart != null) ...[
            const SizedBox(height: AppTheme.paddingLarge),
            const Divider(height: 1),
            const SizedBox(height: AppTheme.paddingLarge),
            ChartWidget(chartData: response!.chart!),
          ],
        ],
      ),
    );
  }

  Widget _buildAnswerText() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppTheme.secondary.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(
            Icons.smart_toy_outlined,
            color: AppTheme.secondary,
            size: 20,
          ),
        ),
        const SizedBox(width: AppTheme.paddingMedium),
        Expanded(
          child: Text(
            response!.answer,
            style: const TextStyle(
              color: AppTheme.textPrimary,
              fontSize: 15,
              height: 1.6,
            ),
          ),
        ),
      ],
    );
  }
}
