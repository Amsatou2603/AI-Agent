"""
BONUS — optionnel : proposition de QueryIntent via un LLM externe.

Ce module est un complément à l'analyseur déterministe (analyseur.py),
PAS un remplacement. Le LLM ne fait JAMAIS que proposer un QueryIntent
JSON à schéma strict et température basse. Sa sortie est toujours
validée côté serveur (mêmes règles que l'analyseur : indicateur dans
CHAMPS_AUTORISES, région dans REGIONS_SENEGAL, année dans 2020-2024)
avant utilisation. En cas d'échec, de JSON invalide, de dépassement de
délai, ou de champ non conforme, on retombe automatiquement sur
analyser_question() : le LLM ne génère et n'exécute jamais de SQL, et
son indisponibilité ne casse jamais l'agent.
"""

from __future__ import annotations

import json
import os

import requests

from .analyseur import (
    ANNEE_MAX,
    ANNEE_MIN,
    OPERATIONS_VALIDES,
    QueryIntent,
    analyser_question,
)
from .models import REGIONS_SENEGAL
from .moteur import CHAMPS_AUTORISES

DELAI_EXPIRATION_SECONDES = 5

SCHEMA_ATTENDU = """
Réponds UNIQUEMENT avec un objet JSON (aucun texte autour), avec exactement
ces clés :
{
  "indicator": un champ parmi %s ou null,
  "regions": liste de régions parmi %s,
  "start_year": entier entre %d et %d ou null,
  "end_year": entier entre %d et %d ou null,
  "operation": une valeur parmi %s
}
""" % (
    list(CHAMPS_AUTORISES), REGIONS_SENEGAL, ANNEE_MIN, ANNEE_MAX,
    ANNEE_MIN, ANNEE_MAX, list(OPERATIONS_VALIDES),
)


def _valider_intent_llm(donnees: dict) -> QueryIntent:
    """
    Valide strictement le JSON renvoyé par le LLM contre les listes blanches
    de l'application. Lève ValueError si un champ n'est pas conforme —
    l'appelant doit alors se replier sur l'analyseur déterministe.
    """
    indicator = donnees.get("indicator")
    if indicator is not None and indicator not in CHAMPS_AUTORISES:
        raise ValueError(f"Indicateur proposé par le LLM non autorisé : {indicator!r}")

    regions = donnees.get("regions") or []
    if not isinstance(regions, list) or any(r not in REGIONS_SENEGAL for r in regions):
        raise ValueError(f"Région(s) proposée(s) par le LLM non autorisée(s) : {regions!r}")

    operation = donnees.get("operation", "value")
    if operation not in OPERATIONS_VALIDES:
        raise ValueError(f"Opération proposée par le LLM non autorisée : {operation!r}")

    for cle in ("start_year", "end_year"):
        valeur = donnees.get(cle)
        if valeur is not None and not (ANNEE_MIN <= int(valeur) <= ANNEE_MAX):
            raise ValueError(f"{cle} hors plage autorisée : {valeur!r}")

    return QueryIntent(
        indicator=indicator,
        regions=regions,
        start_year=donnees.get("start_year"),
        end_year=donnees.get("end_year"),
        operation=operation,
    )


def proposer_intent_via_llm(question: str) -> QueryIntent:
    """
    Interroge un LLM externe pour proposer un QueryIntent, avec repli
    automatique sur l'analyseur déterministe en cas d'échec.

    La clé API est lue depuis la variable d'environnement LLM_API_KEY
    (jamais codée en dur, jamais commitée). Seule la question de
    l'utilisateur et le schéma attendu sont envoyés au LLM : jamais la
    base de données complète.
    """
    cle_api = os.environ.get("LLM_API_KEY")
    url_api = os.environ.get("LLM_API_URL")

    if not cle_api or not url_api:
        return analyser_question(question)

    try:
        reponse = requests.post(
            url_api,
            headers={"Authorization": f"Bearer {cle_api}"},
            json={
                "temperature": 0.0,
                "messages": [
                    {"role": "system", "content": SCHEMA_ATTENDU},
                    {"role": "user", "content": question},
                ],
            },
            timeout=DELAI_EXPIRATION_SECONDES,
        )
        reponse.raise_for_status()
        contenu_texte = reponse.json()["choices"][0]["message"]["content"]
        donnees = json.loads(contenu_texte)
        intent = _valider_intent_llm(donnees)

        # On journalise l'intention validée (jamais la clé API ni les secrets).
        print(f"[bonus_llm] intention validée : {intent.to_dict()}")
        return intent

    except (
        requests.RequestException,
        json.JSONDecodeError,
        KeyError,
        ValueError,
        TypeError,
    ) as erreur:
        print(f"[bonus_llm] repli sur l'analyseur déterministe : {erreur}")
        return analyser_question(question)