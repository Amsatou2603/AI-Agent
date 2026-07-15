"""Configuration de l'interface d'administration Django."""

# pyrefly: ignore [missing-import]
from django.contrib import admin

from .models import StatistiqueRegionale


@admin.register(StatistiqueRegionale)
class StatistiqueRegionaleAdmin(admin.ModelAdmin):
    """Affichage et filtrage des statistiques régionales dans l'admin."""

    list_display = (
        "region",
        "annee",
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
    list_filter = ("region", "annee")
    search_fields = ("region",)
    ordering = ("region", "annee")
    list_per_page = 50
