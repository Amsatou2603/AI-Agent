"""
Analyseur de questions (NLU déterministe) — Étape C.

Transforme une question en français libre en une structure `QueryIntent`
strictement typée, en s'appuyant uniquement sur des règles, des
expressions régulières et des dictionnaires de correspondance mots-clés.
Aucun nom de champ n'est jamais lu directement depuis le texte utilisateur :
seuls les alias reconnus dans INDICATOR_ALIASES peuvent aboutir à un nom
de champ, et ce nom de champ est ensuite revalidé par le moteur ORM
(statistiques/moteur.py) contre sa propre liste blanche avant tout usage
dans values()/order_by()/aggregate().
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional

from .models import REGIONS_SENEGAL

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

ANNEE_MIN = 2020
ANNEE_MAX = 2024

OPERATIONS_VALIDES = ("value", "compare", "trend", "ranking", "sum", "average")

# Table de correspondance mots usuels (normalisés, sans accent, en minuscule)
# -> nom de champ du modèle StatistiqueRegionale.
# Chaque champ peut avoir plusieurs alias (singulier/pluriel, avec/sans accent,
# formulations courantes en français).
INDICATOR_ALIASES: dict[str, str] = {
    # population
    "population": "population",
    "habitants": "population",
    "nombre d'habitants": "population",
    # urbanisation
    "urbanisation": "taux_urbanisation_pct",
    "taux d'urbanisation": "taux_urbanisation_pct",
    "urbain": "taux_urbanisation_pct",
    # alphabétisation
    "alphabetisation": "taux_alphabetisation_pct",
    "alphabétisation": "taux_alphabetisation_pct",
    "taux d'alphabetisation": "taux_alphabetisation_pct",
    "lettres": "taux_alphabetisation_pct",
    # chômage
    "chomage": "taux_chomage_pct",
    "chômage": "taux_chomage_pct",
    "taux de chomage": "taux_chomage_pct",
    "emploi": "taux_chomage_pct",
    # pauvreté
    "pauvrete": "taux_pauvrete_pct",
    "pauvreté": "taux_pauvrete_pct",
    "taux de pauvrete": "taux_pauvrete_pct",
    # internet
    "internet": "acces_internet_pct",
    "acces a internet": "acces_internet_pct",
    "accès à internet": "acces_internet_pct",
    "connexion internet": "acces_internet_pct",
    # santé
    "sante": "centres_sante",
    "santé": "centres_sante",
    "centres de sante": "centres_sante",
    "centre de sante": "centres_sante",
    "hopitaux": "centres_sante",
    "hôpitaux": "centres_sante",
    # scolarisation
    "scolarisation": "taux_scolarisation_pct",
    "taux de scolarisation": "taux_scolarisation_pct",
    "ecole": "taux_scolarisation_pct",
    "école": "taux_scolarisation_pct",
    # production céréalière
    "cereales": "production_cerealiere_tonnes",
    "céréales": "production_cerealiere_tonnes",
    "production": "production_cerealiere_tonnes",
    "production cerealiere": "production_cerealiere_tonnes",
    "production céréalière": "production_cerealiere_tonnes",
}

# Mots-clés déclenchant chaque opération (formes normalisées).
MOTS_CLES_OPERATION: dict[str, tuple[str, ...]] = {
    "compare": ("compare", "comparer", "comparaison", "versus", "vs", "par rapport a"),
    "trend": ("evolution", "évolution", "tendance", "progression", "au fil des annees", "entre"),
    "ranking": ("classement", "top", "classer", "meilleur", "meilleurs", "pire", "pires", "podium"),
    "sum": ("total", "somme", "cumul", "cumule"),
    "average": ("moyenne", "moyen", "moyenne nationale"),
}

# Mots signalant un thème hors périmètre (aucun rapport avec les statistiques
# régionales du modèle) — utilisés uniquement comme filet de sécurité
# supplémentaire quand ni indicateur ni région ne sont détectés.
MOTS_HORS_SUJET = (
    "meteo", "météo", "recette", "cuisine", "football", "musique",
    "film", "cinema", "cinéma", "blague", "horoscope",
)


# ---------------------------------------------------------------------------
# Structure QueryIntent
# ---------------------------------------------------------------------------

@dataclass
class QueryIntent:
    """
    Représentation structurée d'une question utilisateur.

    Les clés correspondent exactement au contrat partagé avec le reste
    de l'application (API, moteur ORM) :
    indicator, regions, start_year, end_year, operation, limit, chart_type.
    """

    indicator: Optional[str] = None
    regions: list[str] = field(default_factory=list)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    operation: str = "value"
    limit: Optional[int] = None
    chart_type: Optional[str] = None

    # Champs de contrôle, absents du contrat JSON final envoyé au front,
    # mais utiles à l'API pour décider s'il faut répondre ou clarifier.
    needs_clarification: bool = False
    clarification_message: Optional[str] = None
    hors_perimetre: bool = False
    hors_perimetre_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Sérialise l'intention en dictionnaire simple (JSON-compatible)."""
        return {
            "indicator": self.indicator,
            "regions": self.regions,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "operation": self.operation,
            "limit": self.limit,
            "chart_type": self.chart_type,
            "needs_clarification": self.needs_clarification,
            "clarification_message": self.clarification_message,
            "hors_perimetre": self.hors_perimetre,
            "hors_perimetre_message": self.hors_perimetre_message,
        }


# ---------------------------------------------------------------------------
# Normalisation de texte
# ---------------------------------------------------------------------------

def normaliser_texte(texte: str) -> str:
    """
    Normalise un texte pour une comparaison insensible à la casse et aux accents.

    Exemple : "Chômage à Kédougou" -> "chomage a kedougou"
    """
    texte = texte.lower().strip()
    texte = unicodedata.normalize("NFD", texte)
    texte = "".join(char for char in texte if unicodedata.category(char) != "Mn")
    texte = re.sub(r"\s+", " ", texte)
    return texte


# ---------------------------------------------------------------------------
# Détection de l'indicateur
# ---------------------------------------------------------------------------

def detecter_indicateur(texte_normalise: str) -> Optional[str]:
    """
    Cherche un alias d'indicateur dans le texte normalisé.

    Retourne le nom de champ du modèle correspondant, ou None si aucun
    alias n'est trouvé. Les alias les plus longs sont testés en premier
    pour éviter qu'un alias court masque une correspondance plus précise
    (ex. "production cerealiere" avant "production").
    """
    for alias in sorted(INDICATOR_ALIASES, key=len, reverse=True):
        alias_normalise = normaliser_texte(alias)
        if alias_normalise in texte_normalise:
            return INDICATOR_ALIASES[alias]
    return None


# ---------------------------------------------------------------------------
# Détection des régions
# ---------------------------------------------------------------------------

def detecter_regions(texte_normalise: str) -> list[str]:
    """
    Détecte les régions du Sénégal mentionnées dans le texte normalisé.

    Insensible à la casse et aux accents. Retourne les noms de région tels
    qu'ils apparaissent dans REGIONS_SENEGAL (liste blanche du modèle),
    dans leur ordre d'apparition dans la question, sans doublon.
    """
    regions_trouvees: list[str] = []
    for region in REGIONS_SENEGAL:
        region_normalisee = normaliser_texte(region)
        if re.search(rf"\b{re.escape(region_normalisee)}\b", texte_normalise):
            if region not in regions_trouvees:
                regions_trouvees.append(region)
    return regions_trouvees


# ---------------------------------------------------------------------------
# Extraction des années
# ---------------------------------------------------------------------------

def extraire_annees(texte_normalise: str) -> tuple[Optional[int], Optional[int]]:
    """
    Extrait une année seule ou une plage d'années (start_year, end_year).

    Gère :
      - une plage explicite : "entre 2020 et 2024" -> (2020, 2024)
      - une plage avec tiret : "2020-2024" ou "2020 a 2024" -> (2020, 2024)
      - une année seule : "en 2022" -> (2022, 2022)
      - aucune année : (None, None)

    Seules les années dans [ANNEE_MIN, ANNEE_MAX] sont retenues ; les autres
    sont ignorées comme si elles n'avaient pas été trouvées.
    """
    motif_plage = re.compile(
        r"entre\s+(\d{4})\s+et\s+(\d{4})|(\d{4})\s*(?:-|a)\s*(\d{4})"
    )
    correspondance_plage = motif_plage.search(texte_normalise)
    if correspondance_plage:
        groupes = [g for g in correspondance_plage.groups() if g is not None]
        if len(groupes) == 2:
            debut, fin = sorted(int(g) for g in groupes)
            debut = debut if ANNEE_MIN <= debut <= ANNEE_MAX else None
            fin = fin if ANNEE_MIN <= fin <= ANNEE_MAX else None
            if debut is not None and fin is not None:
                return debut, fin

    toutes_les_annees = [int(a) for a in re.findall(r"\b(\d{4})\b", texte_normalise)]
    annees_valides = [a for a in toutes_les_annees if ANNEE_MIN <= a <= ANNEE_MAX]

    if not annees_valides:
        return None, None
    if len(annees_valides) == 1:
        return annees_valides[0], annees_valides[0]

    debut, fin = min(annees_valides), max(annees_valides)
    return debut, fin


# ---------------------------------------------------------------------------
# Détection de l'opération
# ---------------------------------------------------------------------------

def detecter_operation(texte_normalise: str) -> str:
    """
    Détecte l'opération demandée à partir de mots-clés français.

    Retourne l'une des 6 opérations valides ; "value" par défaut si aucun
    mot-clé spécifique n'est trouvé.
    """
    for operation, mots_cles in MOTS_CLES_OPERATION.items():
        for mot_cle in mots_cles:
            if normaliser_texte(mot_cle) in texte_normalise:
                return operation
    return "value"


def deduire_chart_type(operation: str) -> Optional[str]:
    """Associe automatiquement un type de graphique à une opération."""
    correspondance = {
        "value": None,
        "compare": "bar",
        "trend": "line",
        "ranking": "bar",
        "sum": None,
        "average": None,
    }
    return correspondance.get(operation)


# ---------------------------------------------------------------------------
# Détection du classement (limit)
# ---------------------------------------------------------------------------

def detecter_limite(texte_normalise: str) -> Optional[int]:
    """
    Extrait une limite numérique pour un classement (ex. "top 5" -> 5).

    Retourne None si aucune limite explicite n'est trouvée (le moteur
    appliquera alors une valeur par défaut raisonnable pour "ranking").
    """
    correspondance = re.search(r"top\s*(\d+)", texte_normalise)
    if correspondance:
        return int(correspondance.group(1))
    return None


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def analyser_question(texte: str) -> QueryIntent:
    """
    Analyse une question en langage naturel et produit un QueryIntent.

    Étapes :
      1. Normalisation du texte (casse, accents).
      2. Détection de l'indicateur, des régions, des années, de l'opération.
      3. Détection des cas hors périmètre (aucun indicateur ET aucune région
         reconnus, ou thème manifestement étranger aux statistiques).
      4. Détection des cas ambigus nécessitant une clarification (indicateur
         absent, ou année indispensable absente pour une opération qui en a
         besoin comme "trend").

    Ne lève jamais d'exception : toute question imprévue aboutit à un
    QueryIntent avec needs_clarification=True ou hors_perimetre=True plutôt
    qu'à une erreur ou à une donnée inventée.
    """
    if not texte or not texte.strip():
        return QueryIntent(
            needs_clarification=True,
            clarification_message=(
                "Votre question est vide. Merci de préciser un indicateur "
                "(ex. chômage, internet, population) et éventuellement une "
                "région ou une année."
            ),
        )

    texte_normalise = normaliser_texte(texte)

    indicateur = detecter_indicateur(texte_normalise)
    regions = detecter_regions(texte_normalise)
    annee_debut, annee_fin = extraire_annees(texte_normalise)
    operation = detecter_operation(texte_normalise)
    limite = detecter_limite(texte_normalise)
    chart_type = deduire_chart_type(operation)

    # Cas hors périmètre : ni indicateur ni région reconnus, et un mot-clé
    # hors sujet est présent (ou aucun signal statistique du tout).
    aucun_signal_statistique = indicateur is None and not regions
    theme_hors_sujet = any(
        normaliser_texte(mot) in texte_normalise for mot in MOTS_HORS_SUJET
    )
    if aucun_signal_statistique and (theme_hors_sujet or annee_debut is None):
        return QueryIntent(
            regions=regions,
            operation=operation,
            hors_perimetre=True,
            hors_perimetre_message=(
                "Je ne peux répondre qu'à des questions sur les statistiques "
                "régionales du Sénégal (population, chômage, pauvreté, "
                "internet, santé, scolarisation, urbanisation, alphabétisation, "
                "production céréalière) sur la période 2020-2024. "
                "Pouvez-vous reformuler votre question sur ce sujet ?"
            ),
        )

    # Cas ambigu : aucun indicateur reconnu malgré une ou plusieurs régions.
    if indicateur is None:
        return QueryIntent(
            regions=regions,
            start_year=annee_debut,
            end_year=annee_fin,
            operation=operation,
            limit=limite,
            chart_type=chart_type,
            needs_clarification=True,
            clarification_message=(
                "Je n'ai pas identifié d'indicateur dans votre question. "
                "Voulez-vous parler du chômage, de la pauvreté, de l'accès à "
                "Internet, de la population, de la santé, de la scolarisation, "
                "de l'urbanisation, de l'alphabétisation ou de la production "
                "céréalière ?"
            ),
        )

    # Cas ambigu : une évolution ("trend") a été demandée mais aucune
    # année n'a pu être détectée pour construire une série temporelle.
    if operation == "trend" and annee_debut is None:
        return QueryIntent(
            indicator=indicateur,
            regions=regions,
            operation=operation,
            chart_type=chart_type,
            needs_clarification=True,
            clarification_message=(
                "Sur quelle période souhaitez-vous voir l'évolution "
                f"({ANNEE_MIN}-{ANNEE_MAX}) ? Précisez une année ou une plage, "
                "par exemple « entre 2020 et 2024 »."
            ),
        )

    return QueryIntent(
        indicator=indicateur,
        regions=regions,
        start_year=annee_debut,
        end_year=annee_fin,
        operation=operation,
        limit=limite,
        chart_type=chart_type,
    )