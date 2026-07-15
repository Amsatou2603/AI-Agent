"""
Moteur de requêtes ORM sécurisé — Étape D.

Prend un QueryIntent déjà validé en entrée et retourne les données pour
l'une des 6 opérations (value, compare, trend, ranking, sum, average),
en n'utilisant que l'ORM Django (filter, values, order_by, aggregate).

RÈGLE DE SÉCURITÉ NON NÉGOCIABLE :
Le nom de champ utilisé dans values()/order_by()/aggregate() provient
TOUJOURS de CHAMPS_AUTORISES, une liste blanche codée en dur. Le champ
`indicator` d'un QueryIntent est revalidé ici (getattr sur cette liste
blanche uniquement) avant tout usage dans l'ORM, même s'il a déjà été
validé par l'analyseur — aucune requête SQL n'est jamais construite à
partir du texte libre de l'utilisateur.
"""

from __future__ import annotations

from typing import Optional

# pyrefly: ignore [missing-import]
from django.db.models import Avg, Sum

from .analyseur import QueryIntent
from .models import REGIONS_SENEGAL, StatistiqueRegionale

# ---------------------------------------------------------------------------
# Liste blanche des champs interrogeables (RÈGLE DE SÉCURITÉ)
# ---------------------------------------------------------------------------

CHAMPS_AUTORISES: tuple[str, ...] = (
    "population",
    "taux_urbanisation_pct",
    "taux_alphabetisation_pct",
    "taux_chomage_pct",
    "taux_pauvrete_pct",
    "acces_internet_pct",
    "centres_sante",
    "taux_scolarisation_pct",
    "production_cerealiere_tonnes",
)

# Libellés français pour construire des réponses lisibles.
LIBELLES_INDICATEURS: dict[str, str] = {
    "population": "la population",
    "taux_urbanisation_pct": "le taux d'urbanisation",
    "taux_alphabetisation_pct": "le taux d'alphabétisation",
    "taux_chomage_pct": "le taux de chômage",
    "taux_pauvrete_pct": "le taux de pauvreté",
    "acces_internet_pct": "l'accès à Internet",
    "centres_sante": "le nombre de centres de santé",
    "taux_scolarisation_pct": "le taux de scolarisation",
    "production_cerealiere_tonnes": "la production céréalière",
}

UNITES_INDICATEURS: dict[str, str] = {
    "population": "",
    "taux_urbanisation_pct": " %",
    "taux_alphabetisation_pct": " %",
    "taux_chomage_pct": " %",
    "taux_pauvrete_pct": " %",
    "acces_internet_pct": " %",
    "centres_sante": "",
    "taux_scolarisation_pct": " %",
    "production_cerealiere_tonnes": " tonnes",
}

LIMITE_RANKING_PAR_DEFAUT = 5


class ErreurMoteur(Exception):
    """Erreur métier attendue (jamais une exception non gérée côté appelant)."""


def _valider_champ(indicator: Optional[str]) -> str:
    """
    Vérifie que `indicator` fait bien partie de la liste blanche.

    C'est le seul point d'entrée par lequel un nom de champ peut être
    utilisé plus loin dans values()/order_by()/aggregate().
    """
    if indicator not in CHAMPS_AUTORISES:
        raise ErreurMoteur(
            f"Indicateur inconnu ou non autorisé : {indicator!r}."
        )
    return indicator


def _formater_valeur(valeur, champ: str) -> float:
    """Convertit une valeur Decimal/int en float arrondi pour le JSON."""
    if valeur is None:
        return 0.0
    return round(float(valeur), 2)


def _reponse_vide(message: str) -> dict:
    """Structure de réponse standard pour un résultat vide ou une erreur métier."""
    return {
        "answer": message,
        "table": [],
        "chart": None,
        "metadata": {"fictitious": True, "rows_used": 0},
    }


# ---------------------------------------------------------------------------
# Opération : value
# ---------------------------------------------------------------------------

def operation_value(intent: QueryIntent) -> dict:
    """Retourne la valeur d'un indicateur pour une région et une année données."""
    champ = _valider_champ(intent.indicator)

    if not intent.regions:
        return _reponse_vide("Merci de préciser une région pour cette question.")

    region = intent.regions[0]
    annee = intent.end_year or intent.start_year

    queryset = StatistiqueRegionale.objects.filter(region=region)
    if annee is not None:
        queryset = queryset.filter(annee=annee)
    else:
        queryset = queryset.order_by("-annee")

    ligne = queryset.values("annee", champ).first()

    if ligne is None:
        return _reponse_vide(
            f"Aucune donnée disponible pour {region}"
            + (f" en {annee}." if annee else ".")
        )

    valeur = _formater_valeur(ligne[champ], champ)
    unite = UNITES_INDICATEURS[champ]
    reponse_texte = (
        f"En {ligne['annee']}, {LIBELLES_INDICATEURS[champ]} à {region} "
        f"est de {valeur}{unite}."
    )

    return {
        "answer": reponse_texte,
        "table": [{"annee": ligne["annee"], "valeur": valeur}],
        "chart": None,
        "metadata": {"fictitious": True, "rows_used": 1},
    }


# ---------------------------------------------------------------------------
# Opération : compare
# ---------------------------------------------------------------------------

def operation_compare(intent: QueryIntent) -> dict:
    """Compare un indicateur entre plusieurs régions pour une année donnée."""
    champ = _valider_champ(intent.indicator)

    if len(intent.regions) < 2:
        return _reponse_vide(
            "Merci de préciser au moins deux régions à comparer."
        )

    annee = intent.end_year or intent.start_year
    queryset = StatistiqueRegionale.objects.filter(region__in=intent.regions)
    if annee is not None:
        queryset = queryset.filter(annee=annee)

    lignes = list(
        queryset.values("region", "annee", champ).order_by("region", "-annee")
    )

    if not lignes:
        return _reponse_vide(
            "Aucune donnée disponible pour comparer ces régions."
        )

    # On garde une seule ligne (la plus récente si pas d'année précise) par région.
    par_region: dict[str, dict] = {}
    for ligne in lignes:
        if ligne["region"] not in par_region:
            par_region[ligne["region"]] = ligne

    unite = UNITES_INDICATEURS[champ]
    table = []
    parties_texte = []
    for region in intent.regions:
        if region not in par_region:
            continue
        ligne = par_region[region]
        valeur = _formater_valeur(ligne[champ], champ)
        table.append({"region": region, "annee": ligne["annee"], "valeur": valeur})
        parties_texte.append(f"{region} : {valeur}{unite} ({ligne['annee']})")

    reponse_texte = (
        f"Comparaison de {LIBELLES_INDICATEURS[champ]} — " + ", ".join(parties_texte) + "."
    )

    chart = {
        "type": "bar",
        "labels": [ligne["region"] for ligne in table],
        "datasets": [
            {
                "label": LIBELLES_INDICATEURS[champ].capitalize(),
                "data": [ligne["valeur"] for ligne in table],
            }
        ],
    }

    return {
        "answer": reponse_texte,
        "table": table,
        "chart": chart,
        "metadata": {"fictitious": True, "rows_used": len(table)},
    }


# ---------------------------------------------------------------------------
# Opération : trend
# ---------------------------------------------------------------------------

def operation_trend(intent: QueryIntent) -> dict:
    """Retourne l'évolution d'un indicateur pour une région sur une plage d'années."""
    champ = _valider_champ(intent.indicator)

    if not intent.regions:
        return _reponse_vide("Merci de préciser une région pour voir son évolution.")

    region = intent.regions[0]
    debut = intent.start_year or 2020
    fin = intent.end_year or 2024

    lignes = list(
        StatistiqueRegionale.objects.filter(
            region=region, annee__gte=debut, annee__lte=fin
        )
        .order_by("annee")
        .values("annee", champ)
    )

    if not lignes:
        return _reponse_vide(
            f"Aucune donnée disponible pour {region} entre {debut} et {fin}."
        )

    table = [
        {"annee": ligne["annee"], "valeur": _formater_valeur(ligne[champ], champ)}
        for ligne in lignes
    ]
    unite = UNITES_INDICATEURS[champ]
    premiere, derniere = table[0], table[-1]

    reponse_texte = (
        f"À {region}, {LIBELLES_INDICATEURS[champ]} passe de "
        f"{premiere['valeur']}{unite} en {premiere['annee']} à "
        f"{derniere['valeur']}{unite} en {derniere['annee']}."
    )

    chart = {
        "type": "line",
        "labels": [ligne["annee"] for ligne in table],
        "datasets": [
            {
                "label": f"{LIBELLES_INDICATEURS[champ].capitalize()}{unite}",
                "data": [ligne["valeur"] for ligne in table],
            }
        ],
    }

    return {
        "answer": reponse_texte,
        "table": table,
        "chart": chart,
        "metadata": {"fictitious": True, "rows_used": len(table)},
    }


# ---------------------------------------------------------------------------
# Opération : ranking
# ---------------------------------------------------------------------------

def operation_ranking(intent: QueryIntent) -> dict:
    """Retourne le classement des 14 régions pour un indicateur et une année."""
    champ = _valider_champ(intent.indicator)

    annee = intent.end_year or intent.start_year
    queryset = StatistiqueRegionale.objects.all()
    if annee is not None:
        queryset = queryset.filter(annee=annee)
    else:
        queryset = queryset.filter(annee=2024)
        annee = 2024

    limite = intent.limit or LIMITE_RANKING_PAR_DEFAUT
    lignes = list(
        queryset.order_by(f"-{champ}").values("region", champ)[:limite]
    )

    if not lignes:
        return _reponse_vide(f"Aucune donnée disponible pour l'année {annee}.")

    unite = UNITES_INDICATEURS[champ]
    table = [
        {"region": ligne["region"], "valeur": _formater_valeur(ligne[champ], champ)}
        for ligne in lignes
    ]

    tete_de_classement = ", ".join(
        f"{i + 1}. {ligne['region']} ({ligne['valeur']}{unite})"
        for i, ligne in enumerate(table)
    )
    reponse_texte = (
        f"Classement des régions par {LIBELLES_INDICATEURS[champ]} en {annee} : "
        f"{tete_de_classement}."
    )

    chart = {
        "type": "bar",
        "labels": [ligne["region"] for ligne in table],
        "datasets": [
            {
                "label": f"{LIBELLES_INDICATEURS[champ].capitalize()}{unite} ({annee})",
                "data": [ligne["valeur"] for ligne in table],
            }
        ],
    }

    return {
        "answer": reponse_texte,
        "table": table,
        "chart": chart,
        "metadata": {"fictitious": True, "rows_used": len(table)},
    }


# ---------------------------------------------------------------------------
# Opération : sum
# ---------------------------------------------------------------------------

def operation_sum(intent: QueryIntent) -> dict:
    """Retourne la somme d'un indicateur, éventuellement filtrée par région/année."""
    champ = _valider_champ(intent.indicator)

    queryset = StatistiqueRegionale.objects.all()
    if intent.regions:
        queryset = queryset.filter(region__in=intent.regions)
    annee = intent.end_year or intent.start_year
    if annee is not None:
        queryset = queryset.filter(annee=annee)

    resultat = queryset.aggregate(total=Sum(champ))
    total = resultat["total"]

    if total is None:
        return _reponse_vide("Aucune donnée disponible pour ce calcul de total.")

    valeur = _formater_valeur(total, champ)
    unite = UNITES_INDICATEURS[champ]
    portee = f" pour {', '.join(intent.regions)}" if intent.regions else " (toutes régions)"
    portee += f" en {annee}" if annee else " (2020-2024)"

    reponse_texte = f"Total de {LIBELLES_INDICATEURS[champ]}{portee} : {valeur}{unite}."

    return {
        "answer": reponse_texte,
        "table": [{"valeur": valeur}],
        "chart": None,
        "metadata": {"fictitious": True, "rows_used": queryset.count()},
    }


# ---------------------------------------------------------------------------
# Opération : average
# ---------------------------------------------------------------------------

def operation_average(intent: QueryIntent) -> dict:
    """Retourne la moyenne d'un indicateur, éventuellement filtrée par région/année."""
    champ = _valider_champ(intent.indicator)

    queryset = StatistiqueRegionale.objects.all()
    if intent.regions:
        queryset = queryset.filter(region__in=intent.regions)
    annee = intent.end_year or intent.start_year
    if annee is not None:
        queryset = queryset.filter(annee=annee)

    resultat = queryset.aggregate(moyenne=Avg(champ))
    moyenne = resultat["moyenne"]

    if moyenne is None:
        return _reponse_vide("Aucune donnée disponible pour ce calcul de moyenne.")

    valeur = _formater_valeur(moyenne, champ)
    unite = UNITES_INDICATEURS[champ]
    portee = f" pour {', '.join(intent.regions)}" if intent.regions else " (toutes régions)"
    portee += f" en {annee}" if annee else " (2020-2024)"

    reponse_texte = f"Moyenne de {LIBELLES_INDICATEURS[champ]}{portee} : {valeur}{unite}."

    return {
        "answer": reponse_texte,
        "table": [{"valeur": valeur}],
        "chart": None,
        "metadata": {"fictitious": True, "rows_used": queryset.count()},
    }


# ---------------------------------------------------------------------------
# Répartiteur (dispatch)
# ---------------------------------------------------------------------------

_OPERATIONS: dict[str, callable] = {
    "value": operation_value,
    "compare": operation_compare,
    "trend": operation_trend,
    "ranking": operation_ranking,
    "sum": operation_sum,
    "average": operation_average,
}


def executer_intention(intent: QueryIntent) -> dict:
    """
    Point d'entrée unique du moteur : exécute l'opération demandée par
    un QueryIntent déjà produit par l'analyseur, et retourne un
    dictionnaire prêt à être sérialisé selon le contrat JSON
    (answer, table, chart, metadata).

    Ne lève jamais d'exception non gérée : les régions inconnues, années
    sans donnée ou résultats vides retournent un message clair via
    _reponse_vide plutôt qu'une erreur brute ou une donnée inventée.
    """
    if intent.hors_perimetre:
        return _reponse_vide(
            intent.hors_perimetre_message or "Cette question est hors périmètre."
        )
    if intent.needs_clarification:
        return _reponse_vide(
            intent.clarification_message or "Merci de préciser votre question."
        )

    regions_inconnues = [r for r in intent.regions if r not in REGIONS_SENEGAL]
    if regions_inconnues:
        return _reponse_vide(
            "Région(s) non reconnue(s) : " + ", ".join(regions_inconnues) + "."
        )

    fonction_operation = _OPERATIONS.get(intent.operation)
    if fonction_operation is None:
        return _reponse_vide(f"Opération non prise en charge : {intent.operation!r}.")

    try:
        return fonction_operation(intent)
    except ErreurMoteur as erreur:
        return _reponse_vide(str(erreur))