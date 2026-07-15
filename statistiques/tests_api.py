"""
Tests pour l'API /api/question/ (Étape E).
"""

import json

# pyrefly: ignore [missing-import]
from django.test import Client, TestCase

from .models import StatistiqueRegionale


class TestAPIQuestion(TestCase):
    """Tests de l'endpoint POST /api/question/."""

    def setUp(self):
        """Prépare quelques données de test."""
        self.client = Client()

        # Créer des données de test
        StatistiqueRegionale.objects.create(
            region="Dakar",
            annee=2024,
            population=4343857,
            taux_urbanisation_pct=98.6,
            taux_alphabetisation_pct=84.7,
            taux_chomage_pct=13.8,
            taux_pauvrete_pct=6.5,
            acces_internet_pct=90.8,
            centres_sante=146,
            taux_scolarisation_pct=94.6,
            production_cerealiere_tonnes=19476,
        )
        StatistiqueRegionale.objects.create(
            region="Thiès",
            annee=2024,
            population=2482204,
            taux_urbanisation_pct=53.4,
            taux_alphabetisation_pct=71.2,
            taux_chomage_pct=12.0,
            taux_pauvrete_pct=25.4,
            acces_internet_pct=72.8,
            centres_sante=110,
            taux_scolarisation_pct=87.6,
            production_cerealiere_tonnes=170500,
        )
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

    def test_api_question_value(self):
        """Test d'une question simple (operation=value)."""
        reponse = self.client.post(
            "/api/question/",
            data=json.dumps({"question": "Quel est le taux de chômage à Dakar en 2024 ?"}),
            content_type="application/json",
        )

        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.json()

        self.assertIn("answer", donnees)
        self.assertIn("13.8", donnees["answer"])
        self.assertIsNotNone(donnees["table"])
        self.assertIsNone(donnees["chart"])
        self.assertEqual(donnees["metadata"]["fictitious"], True)

    def test_api_question_compare(self):
        """Test d'une comparaison entre deux régions."""
        reponse = self.client.post(
            "/api/question/",
            data=json.dumps({"question": "Compare l'accès à Internet entre Dakar et Thiès en 2024"}),
            content_type="application/json",
        )

        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.json()

        self.assertIn("answer", donnees)
        self.assertIsNotNone(donnees["chart"])
        self.assertEqual(donnees["chart"]["type"], "bar")
        self.assertTrue(len(donnees["table"]) >= 2)

    def test_api_question_trend(self):
        """Test d'une évolution temporelle (trend)."""
        # Ajouter des données supplémentaires pour l'évolution
        for annee in [2021, 2022, 2023]:
            StatistiqueRegionale.objects.create(
                region="Dakar",
                annee=annee,
                population=4000000 + (annee - 2020) * 100000,
                taux_urbanisation_pct=97.5,
                taux_alphabetisation_pct=82,
                taux_chomage_pct=14.5,
                taux_pauvrete_pct=8,
                acces_internet_pct=80,
                centres_sante=140,
                taux_scolarisation_pct=92,
                production_cerealiere_tonnes=18500,
            )

        reponse = self.client.post(
            "/api/question/",
            data=json.dumps({"question": "Évolution de la population à Dakar entre 2020 et 2024"}),
            content_type="application/json",
        )

        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.json()

        self.assertIn("answer", donnees)
        self.assertIsNotNone(donnees["chart"])
        self.assertEqual(donnees["chart"]["type"], "line")
        self.assertTrue(len(donnees["table"]) >= 2)

    def test_api_question_vide(self):
        """Test d'une question vide."""
        reponse = self.client.post(
            "/api/question/",
            data=json.dumps({"question": ""}),
            content_type="application/json",
        )

        self.assertEqual(reponse.status_code, 400)
        donnees = reponse.json()
        self.assertIn("Merci de poser une question", donnees["answer"])

    def test_api_json_invalide(self):
        """Test d'une requête avec un JSON malformé."""
        reponse = self.client.post(
            "/api/question/",
            data="ceci n'est pas du JSON",
            content_type="application/json",
        )

        self.assertEqual(reponse.status_code, 400)
        donnees = reponse.json()
        self.assertIn("Format JSON invalide", donnees["answer"])

    def test_api_question_ambigue(self):
        """Test d'une question ambiguë (sans indicateur reconnu)."""
        reponse = self.client.post(
            "/api/question/",
            data=json.dumps({"question": "Quelles sont les données pour Dakar ?"}),
            content_type="application/json",
        )

        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.json()

        self.assertIn("indicateur", donnees["answer"])
        self.assertEqual(len(donnees["table"]), 0)

    def test_api_question_hors_sujet(self):
        """Test d'une question hors sujet."""
        reponse = self.client.post(
            "/api/question/",
            data=json.dumps({"question": "Quelle est la météo aujourd'hui ?"}),
            content_type="application/json",
        )

        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.json()

        self.assertIn("statistiques régionales", donnees["answer"])
