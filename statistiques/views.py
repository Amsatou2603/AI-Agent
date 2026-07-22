"""Vues de l'application statistiques."""

import json

# pyrefly: ignore [missing-import]
from django.http import JsonResponse
# pyrefly: ignore [missing-import]
from django.shortcuts import render
# pyrefly: ignore [missing-import]
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Avg
# pyrefly: ignore [missing-import]
from django.views.decorators.http import require_http_methods

from .models import StatistiqueRegionale
from .bonus_llm import proposer_intent_via_llm
from .moteur import executer_intention

def accueil(request):
    """Page d'accueil — statistiques clés et suggestions."""
    # Calcul de quelques données globales pour 2024
    pop_totale = StatistiqueRegionale.objects.filter(annee=2024).aggregate(total=Sum('population'))['total']
    tx_scol_moyen = StatistiqueRegionale.objects.filter(annee=2024).aggregate(avg=Avg('taux_scolarisation_pct'))['avg']
    
    # Formatage propre
    pop_m = f"{round((pop_totale or 18300000) / 1000000, 1)}M"
    scol_pct = f"{round(float(tx_scol_moyen or 74.5), 1)}%"

    contexte = {
        'pop_totale': pop_m,
        'tx_scolarisation': scol_pct,
        'croissance_pib': "8.1%", # Estimation
    }
    return render(request, "accueil.html", contexte)

def dashboard(request):
    """Tableau de bord national — agrégations et graphiques nationaux."""
    # Évolution nationale de la production céréalière
    evol_cereales = (
        StatistiqueRegionale.objects.values('annee')
        .annotate(total=Sum('production_cerealiere_tonnes'))
        .order_by('annee')
    )
    
    # Nombre total de centres de santé en 2024
    sante_2024 = StatistiqueRegionale.objects.filter(annee=2024).aggregate(total=Sum('centres_sante'))['total'] or 0

    # Zones géographiques pour éducation
    zone_dakar = StatistiqueRegionale.objects.filter(annee=2024, region='Dakar').aggregate(avg=Avg('taux_scolarisation_pct'))['avg'] or 0
    zone_thies = StatistiqueRegionale.objects.filter(annee=2024, region__in=['Thiès', 'Diourbel']).aggregate(avg=Avg('taux_scolarisation_pct'))['avg'] or 0
    zone_sud = StatistiqueRegionale.objects.filter(annee=2024, region__in=['Ziguinchor', 'Kolda', 'Sédhiou']).aggregate(avg=Avg('taux_scolarisation_pct'))['avg'] or 0
    zone_nord = StatistiqueRegionale.objects.filter(annee=2024, region__in=['Saint-Louis', 'Matam']).aggregate(avg=Avg('taux_scolarisation_pct'))['avg'] or 0

    contexte = {
        'evol_cereales': list(evol_cereales),
        'sante_total': sante_2024,
        'sante_medecins': "4.2", # Fictif
        'scol_dakar': round(float(zone_dakar), 1),
        'scol_thies': round(float(zone_thies), 1),
        'scol_sud': round(float(zone_sud), 1),
        'scol_nord': round(float(zone_nord), 1),
    }
    return render(request, "dashboard.html", contexte)

def regions(request):
    """Liste de toutes les régions avec filtre de recherche."""
    stats_2024 = StatistiqueRegionale.objects.filter(annee=2024).order_by('region')
    contexte = {
        'regions_data': stats_2024
    }
    return render(request, "regions.html", contexte)

def chat(request):
    """Interface de chat IA."""
    return render(request, "chat.html")

def profil(request):
    """Page profil."""
    return render(request, "profil.html")

@require_http_methods(["POST"])
@csrf_exempt  # CSRF désactivé pour l'API (utilisé par Flutter)
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
        
        # Étape 1 & 2 : Analyse de la question (avec fallback LLM si configuré) et exécution ORM
        intention = proposer_intent_via_llm(question)
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

