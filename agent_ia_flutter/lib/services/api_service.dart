import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/query_response.dart';

/// Service pour communiquer avec l'API Django
class ApiService {
  // URL de l'API - à modifier selon l'environnement
  static const String baseUrl = const String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );
  
  /// Envoie une question à l'API et retourne la réponse
  Future<QueryResponse> askQuestion(String question) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/question/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({'question': question}),
      ).timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          throw Exception('La requête a expiré. Vérifiez votre connexion.');
        },
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return QueryResponse.fromJson(data);
      } else if (response.statusCode == 400) {
        final Map<String, dynamic> data = json.decode(response.body);
        return QueryResponse.fromJson(data);
      } else {
        throw Exception('Erreur serveur: ${response.statusCode}');
      }
    } catch (e) {
      if (e.toString().contains('SocketException')) {
        throw Exception(
          'Impossible de se connecter au serveur.\n'
          'Vérifiez que le serveur Django est démarré sur $baseUrl',
        );
      }
      rethrow;
    }
  }
}
