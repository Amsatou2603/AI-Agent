"""
Modèle de données pour l'agent IA de statistiques régionales du Sénégal.

Avertissement : ce jeu de données est strictement fictif. Il imite la
structure de données d'une agence comme l'ANSD mais ne contient aucune
donnée officielle. Voir templates/base.html pour la mention affichée
à l'utilisateur.
"""

# pyrefly: ignore [missing-import]
from django.db import models


# Liste blanche exacte des 14 régions du Sénégal.
# Utilisée à la fois comme choices Django et comme référence pour
# l'analyseur (statistiques/analyseur.py) et le moteur ORM (statistiques/moteur.py).
REGIONS_SENEGAL = [
    "Dakar",
    "Thiès",
    "Diourbel",
    "Fatick",
    "Kaolack",
    "Kaffrine",
    "Kolda",
    "Kédougou",
    "Louga",
    "Matam",
    "Saint-Louis",
    "Sédhiou",
    "Tambacounda",
    "Ziguinchor",
]

REGION_CHOICES = [(region, region) for region in REGIONS_SENEGAL]


class StatistiqueRegionale(models.Model):
    """
    Une ligne d'indicateurs statistiques pour une région et une année données.

    Contrainte métier : une seule ligne par couple (region, annee).
    """

    region = models.CharField(
        max_length=40,
        choices=REGION_CHOICES,
        help_text="Nom exact de la région (liste blanche des 14 régions du Sénégal).",
    )
    annee = models.PositiveSmallIntegerField(
        help_text="Année de l'observation (2020 à 2024).",
    )
    population = models.PositiveBigIntegerField(
        help_text="Population totale de la région (personnes).",
    )
    taux_urbanisation_pct = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Taux d'urbanisation (%).",
    )
    taux_alphabetisation_pct = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Taux d'alphabétisation (%).",
    )
    taux_chomage_pct = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Taux de chômage (%).",
    )
    taux_pauvrete_pct = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Taux de pauvreté (%).",
    )
    acces_internet_pct = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Taux d'accès à Internet (%).",
    )
    centres_sante = models.PositiveIntegerField(
        help_text="Nombre de centres de santé (établissements).",
    )
    taux_scolarisation_pct = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Taux de scolarisation (%).",
    )
    production_cerealiere_tonnes = models.PositiveIntegerField(
        help_text="Production céréalière (tonnes).",
    )

    class Meta:
        verbose_name = "Statistique régionale"
        verbose_name_plural = "Statistiques régionales"
        ordering = ["region", "annee"]
        constraints = [
            models.UniqueConstraint(
                fields=["region", "annee"],
                name="unique_region_annee",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.region} ({self.annee})"
