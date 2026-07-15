"""Vues de l'application statistiques."""

import json

# pyrefly: ignore [missing-import]
from django.http import JsonResponse
# pyrefly: ignore [missing-import]
from django.shortcuts import render
# pyrefly: ignore [missing-import]
from django.views.decorators.csrf import csrf_exempt
# pyrefly: ignore [missing-import]
from django.views.decorators.http import require_http_methods

from .analyseur import analyser_question
from .moteur import executer_intention


def accueil(request):
    """Page d'accueil avec l'interface conversationnelle."""
    return render(request, "interface.html")


@require_http_methods(["POST"])
@csrf_exempt  # Pour simplifier les tests — en production, utiliser le jeton CSRF
def api_question(request):
    """
    Endpoint POST /api/question/
    
    Reçoit une question en JSON : {"question": "..."}
    Retourne une réponse structurée : {answer, table, chart, metadata}
    """
    try:
        donnees = json.loads(request.body)
        question = donnees.get("question", "").strip()
        
        if not question:
            return JsonResponse(
                {
                    "answer": "Merci de poser une question.",
                    "table": [],
                    "chart": None,
                    "metadata": {"fictitious": True, "rows_used": 0},
                },
                status=400,
            )
        
        # Étape 1 : Analyse de la question
        intention = analyser_question(question)
        
        # Étape 2 : Exécution de l'intention via le moteur ORM
        resultat = executer_intention(intention)
        
        return JsonResponse(resultat)
        
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "answer": "Format JSON invalide.",
                "table": [],
                "chart": None,
                "metadata": {"fictitious": True, "rows_used": 0},
            },
            status=400,
        )
    except Exception as erreur:
        return JsonResponse(
            {
                "answer": f"Erreur serveur : {str(erreur)}",
                "table": [],
                "chart": None,
                "metadata": {"fictitious": True, "rows_used": 0},
            },
            status=500,
        )
