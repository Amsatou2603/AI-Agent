"""
Commande d'import CSV — Étape B.

Usage :
    python manage.py importer_statistiques chemin/vers/fichier.csv

Comportement :
  - Vérifie que le fichier possède les colonnes obligatoires.
  - Valide que les années sont comprises entre 2020 et 2024.
  - Valide que les pourcentages sont compris entre 0 et 100.
  - Utilise update_or_create pour un import idempotent (pas de doublon
    au second import sur le même couple région/année).
  - Affiche le nombre de lignes créées / mises à jour / rejetées.
"""

import csv
from decimal import Decimal, InvalidOperation

# pyrefly: ignore [missing-import]
from django.core.management.base import BaseCommand, CommandError

from statistiques.models import REGIONS_SENEGAL, StatistiqueRegionale

COLONNES_OBLIGATOIRES = [
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
]

ANNEE_MIN = 2020
ANNEE_MAX = 2024


class Command(BaseCommand):
    """Commande Django pour importer les statistiques depuis un fichier CSV."""

    help = (
        "Importe les statistiques régionales du Sénégal depuis un fichier CSV. "
        "Les lignes existantes (même région + année) sont mises à jour."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "chemin_csv",
            type=str,
            help="Chemin du fichier CSV à importer (ex. donnees.csv).",
        )

    def handle(self, *args, **options):
        chemin = options["chemin_csv"]
        self.stdout.write(f"Lecture du fichier : {chemin}")

        try:
            with open(chemin, "r", encoding="utf-8-sig") as fichier:
                lecteur = csv.DictReader(fichier)

                # Vérifier que toutes les colonnes obligatoires sont présentes
                colonnes_presentes = set(lecteur.fieldnames or [])
                colonnes_manquantes = set(COLONNES_OBLIGATOIRES) - colonnes_presentes
                if colonnes_manquantes:
                    raise CommandError(
                        f"Colonnes manquantes dans le CSV : {', '.join(colonnes_manquantes)}"
                    )

                nb_crees = 0
                nb_mis_a_jour = 0
                nb_rejetes = 0

                for num_ligne, ligne in enumerate(lecteur, start=2):
                    try:
                        donnees_valides = self._valider_ligne(ligne, num_ligne)
                        if donnees_valides is None:
                            nb_rejetes += 1
                            continue

                        # update_or_create crée ou met à jour selon le couple (region, annee)
                        _, cree = StatistiqueRegionale.objects.update_or_create(
                            region=donnees_valides["region"],
                            annee=donnees_valides["annee"],
                            defaults={
                                "population": donnees_valides["population"],
                                "taux_urbanisation_pct": donnees_valides["taux_urbanisation_pct"],
                                "taux_alphabetisation_pct": donnees_valides["taux_alphabetisation_pct"],
                                "taux_chomage_pct": donnees_valides["taux_chomage_pct"],
                                "taux_pauvrete_pct": donnees_valides["taux_pauvrete_pct"],
                                "acces_internet_pct": donnees_valides["acces_internet_pct"],
                                "centres_sante": donnees_valides["centres_sante"],
                                "taux_scolarisation_pct": donnees_valides["taux_scolarisation_pct"],
                                "production_cerealiere_tonnes": donnees_valides["production_cerealiere_tonnes"],
                            },
                        )

                        if cree:
                            nb_crees += 1
                        else:
                            nb_mis_a_jour += 1

                    except Exception as erreur:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Ligne {num_ligne} rejetée : {erreur}"
                            )
                        )
                        nb_rejetes += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nImport terminé : {nb_crees} créée(s), "
                        f"{nb_mis_a_jour} mise(s) à jour, {nb_rejetes} rejetée(s)."
                    )
                )

        except FileNotFoundError:
            raise CommandError(f"Le fichier {chemin} est introuvable.")
        except Exception as erreur:
            raise CommandError(f"Erreur lors de l'import : {erreur}")

    def _valider_ligne(self, ligne: dict, num_ligne: int) -> dict | None:
        """
        Valide une ligne CSV et retourne un dictionnaire de données prêt à
        être inséré, ou None si la ligne doit être rejetée.
        """
        # Vérifier la région (liste blanche)
        region = ligne["region"].strip()
        if region not in REGIONS_SENEGAL:
            self.stdout.write(
                self.style.WARNING(
                    f"Ligne {num_ligne} : région inconnue '{region}' (doit être l'une des 14 régions du Sénégal)."
                )
            )
            return None

        # Vérifier l'année
        try:
            annee = int(ligne["annee"])
            if not (ANNEE_MIN <= annee <= ANNEE_MAX):
                self.stdout.write(
                    self.style.WARNING(
                        f"Ligne {num_ligne} : année {annee} hors plage ({ANNEE_MIN}-{ANNEE_MAX})."
                    )
                )
                return None
        except ValueError:
            self.stdout.write(
                self.style.WARNING(
                    f"Ligne {num_ligne} : année invalide '{ligne['annee']}'."
                )
            )
            return None

        # Vérifier et convertir les entiers
        try:
            population = int(ligne["population"])
            centres_sante = int(ligne["centres_sante"])
            production_cerealiere_tonnes = int(ligne["production_cerealiere_tonnes"])
        except (ValueError, KeyError) as erreur:
            self.stdout.write(
                self.style.WARNING(
                    f"Ligne {num_ligne} : champ entier invalide ({erreur})."
                )
            )
            return None

        # Vérifier et convertir les pourcentages (décimaux entre 0 et 100)
        champs_pct = [
            "taux_urbanisation_pct",
            "taux_alphabetisation_pct",
            "taux_chomage_pct",
            "taux_pauvrete_pct",
            "acces_internet_pct",
            "taux_scolarisation_pct",
        ]
        pourcentages = {}
        for champ in champs_pct:
            try:
                valeur = Decimal(ligne[champ])
                if not (0 <= valeur <= 100):
                    self.stdout.write(
                        self.style.WARNING(
                            f"Ligne {num_ligne} : {champ} = {valeur} hors plage [0, 100]."
                        )
                    )
                    return None
                pourcentages[champ] = valeur
            except (ValueError, InvalidOperation, KeyError) as erreur:
                self.stdout.write(
                    self.style.WARNING(
                        f"Ligne {num_ligne} : {champ} invalide ({erreur})."
                    )
                )
                return None

        # Tout est bon : assembler les données validées
        return {
            "region": region,
            "annee": annee,
            "population": population,
            "centres_sante": centres_sante,
            "production_cerealiere_tonnes": production_cerealiere_tonnes,
            **pourcentages,
        }
