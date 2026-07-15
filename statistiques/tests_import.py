"""
Tests pour la commande d'import CSV (Étape B).
"""

import tempfile
from io import StringIO

# pyrefly: ignore [missing-import]
from django.core.management import call_command
# pyrefly: ignore [missing-import]
from django.test import TestCase

from .models import StatistiqueRegionale


class TestImportCSV(TestCase):
    """Tests de la commande importer_statistiques."""

    def test_import_csv_valide(self):
        """Test d'un import CSV valide avec 2 lignes."""
        contenu_csv = (
            "region,annee,population,taux_urbanisation_pct,taux_alphabetisation_pct,"
            "taux_chomage_pct,taux_pauvrete_pct,acces_internet_pct,centres_sante,"
            "taux_scolarisation_pct,production_cerealiere_tonnes\n"
            "Dakar,2020,3920000,97.2,80.5,14.8,9.1,74,138,91,18324\n"
            "Thiès,2021,2298240,52.4,68,13.8,27.4,60.2,104,84.9,158875\n"
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
            f.write(contenu_csv)
            chemin = f.name

        # Import initial
        sortie = StringIO()
        call_command("importer_statistiques", chemin, stdout=sortie)
        resultat = sortie.getvalue()

        self.assertIn("2 créée(s)", resultat)
        self.assertEqual(StatistiqueRegionale.objects.count(), 2)

        # Vérification d'une ligne
        ligne_dakar = StatistiqueRegionale.objects.get(region="Dakar", annee=2020)
        self.assertEqual(ligne_dakar.population, 3920000)
        self.assertEqual(float(ligne_dakar.taux_chomage_pct), 14.8)

    def test_import_idempotent(self):
        """Test que le second import ne crée pas de doublon (update_or_create)."""
        contenu_csv = (
            "region,annee,population,taux_urbanisation_pct,taux_alphabetisation_pct,"
            "taux_chomage_pct,taux_pauvrete_pct,acces_internet_pct,centres_sante,"
            "taux_scolarisation_pct,production_cerealiere_tonnes\n"
            "Dakar,2020,3920000,97.2,80.5,14.8,9.1,74,138,91,18324\n"
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
            f.write(contenu_csv)
            chemin = f.name

        # Premier import
        call_command("importer_statistiques", chemin, stdout=StringIO())
        self.assertEqual(StatistiqueRegionale.objects.count(), 1)

        # Second import (même fichier)
        sortie = StringIO()
        call_command("importer_statistiques", chemin, stdout=sortie)
        resultat = sortie.getvalue()

        self.assertIn("1 mise(s) à jour", resultat)
        self.assertEqual(StatistiqueRegionale.objects.count(), 1)  # Pas de doublon

    def test_import_rejete_pourcentage_invalide(self):
        """Test qu'un pourcentage hors plage [0, 100] est rejeté."""
        contenu_csv = (
            "region,annee,population,taux_urbanisation_pct,taux_alphabetisation_pct,"
            "taux_chomage_pct,taux_pauvrete_pct,acces_internet_pct,centres_sante,"
            "taux_scolarisation_pct,production_cerealiere_tonnes\n"
            "Dakar,2020,3920000,97.2,80.5,150,9.1,74,138,91,18324\n"
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
            f.write(contenu_csv)
            chemin = f.name

        sortie = StringIO()
        call_command("importer_statistiques", chemin, stdout=sortie)
        resultat = sortie.getvalue()

        self.assertIn("1 rejetée(s)", resultat)
        self.assertEqual(StatistiqueRegionale.objects.count(), 0)

    def test_import_rejete_region_inconnue(self):
        """Test qu'une région non reconnue est rejetée."""
        contenu_csv = (
            "region,annee,population,taux_urbanisation_pct,taux_alphabetisation_pct,"
            "taux_chomage_pct,taux_pauvrete_pct,acces_internet_pct,centres_sante,"
            "taux_scolarisation_pct,production_cerealiere_tonnes\n"
            "Inconnu,2020,3920000,97.2,80.5,14.8,9.1,74,138,91,18324\n"
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
            f.write(contenu_csv)
            chemin = f.name

        sortie = StringIO()
        call_command("importer_statistiques", chemin, stdout=sortie)
        resultat = sortie.getvalue()

        self.assertIn("1 rejetée(s)", resultat)
        self.assertEqual(StatistiqueRegionale.objects.count(), 0)

    def test_contrainte_unicite(self):
        """Test de la contrainte d'unicité (region, annee) au niveau du modèle."""
        StatistiqueRegionale.objects.create(
            region="Dakar",
            annee=2020,
            population=3920000,
            taux_urbanisation_pct=97.2,
            taux_alphabetisation_pct=80.5,
            taux_chomage_pct=14.8,
            taux_pauvrete_pct=9.1,
            acces_internet_pct=74,
            centres_sante=138,
            taux_scolarisation_pct=91,
            production_cerealiere_tonnes=18324,
        )

        # Tentative de créer un doublon (doit lever une exception)
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            StatistiqueRegionale.objects.create(
                region="Dakar",
                annee=2020,
                population=9999999,
                taux_urbanisation_pct=50,
                taux_alphabetisation_pct=50,
                taux_chomage_pct=10,
                taux_pauvrete_pct=10,
                acces_internet_pct=50,
                centres_sante=100,
                taux_scolarisation_pct=80,
                production_cerealiere_tonnes=10000,
            )
