/// Modèle de données pour la réponse de l'API
class QueryResponse {
  final String answer;
  final List<Map<String, dynamic>> table;
  final ChartData? chart;
  final Map<String, dynamic> metadata;

  QueryResponse({
    required this.answer,
    required this.table,
    this.chart,
    required this.metadata,
  });

  factory QueryResponse.fromJson(Map<String, dynamic> json) {
    return QueryResponse(
      answer: json['answer'] as String,
      table: (json['table'] as List<dynamic>)
          .map((item) => Map<String, dynamic>.from(item as Map))
          .toList(),
      chart: json['chart'] != null 
          ? ChartData.fromJson(json['chart'] as Map<String, dynamic>)
          : null,
      metadata: Map<String, dynamic>.from(json['metadata'] as Map),
    );
  }
}

/// Modèle de données pour les graphiques
class ChartData {
  final String type;
  final List<String> labels;
  final List<Dataset> datasets;

  ChartData({
    required this.type,
    required this.labels,
    required this.datasets,
  });

  factory ChartData.fromJson(Map<String, dynamic> json) {
    return ChartData(
      type: json['type'] as String,
      labels: (json['labels'] as List<dynamic>)
          .map((label) => label.toString())
          .toList(),
      datasets: (json['datasets'] as List<dynamic>)
          .map((dataset) => Dataset.fromJson(dataset as Map<String, dynamic>))
          .toList(),
    );
  }
}

/// Dataset pour un graphique
class Dataset {
  final String label;
  final List<double> data;

  Dataset({
    required this.label,
    required this.data,
  });

  factory Dataset.fromJson(Map<String, dynamic> json) {
    return Dataset(
      label: json['label'] as String,
      data: (json['data'] as List<dynamic>)
          .map((value) => (value as num).toDouble())
          .toList(),
    );
  }
}

/// Message de conversation
class ChatMessage {
  final String question;
  final QueryResponse? response;
  final bool isLoading;
  final String? error;

  ChatMessage({
    required this.question,
    this.response,
    this.isLoading = false,
    this.error,
  });
}
