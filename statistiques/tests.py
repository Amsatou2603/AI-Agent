"""Tests d'intégration de l'API Question."""

import json
# pyrefly: ignore [missing-import]
from django.test import TestCase, Client
# pyrefly: ignore [missing-import]
from django.urls import reverse

from .models import StatistiqueRegionale

class TestApiQuestion(TestCase):
    """Vérifie le fonctionnement de l'API /api/question/."""

    def setUp(self):
        self.client = Client()
        # Création d'un petit jeu de données pour Kaolack
        StatistiqueRegionale.objects.create(
            region="Kaolack",
            annee=2024,
            population=1280000,
            taux_urbanisation_pct=49.0,
            taux_alphabetisation_pct=59.0,
            taux_chomage_pct=14.0,
            taux_pauvrete_pct=36.0,
            acces_internet_pct=57.8,
            centres_sante=24,
            taux_scolarisation_pct=74.0,
            production_cerealiere_tonnes=54000
        )

    def test_api_question_valide(self):
        """Une question valide sur Kaolack en 2024 doit retourner un résultat 200."""
        reponse = self.client.post(
            reverse("api_question"),
            data=json.dumps({"question": "Quel est le taux de chômage à Kaolack en 2024 ?"}),
            content_type="application/json"
        )
        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.json()
        self.assertIn("answer", donnees)
        self.assertIn("table", donnees)
        self.assertIn("metadata", donnees)
        self.assertIn("Kaolack", donnees["answer"])

    def test_api_question_vide(self):
        """Une question vide doit retourner un code d'erreur 400."""
        reponse = self.client.post(
            reverse("api_question"),
            data=json.dumps({"question": ""}),
            content_type="application/json"
        )
        self.assertEqual(reponse.status_code, 400)
        donnees = reponse.json()
        self.assertIn("answer", donnees)
        self.assertEqual(donnees["table"], [])

    def test_api_question_json_invalide(self):
        """Un corps de requête invalide (non-JSON) doit retourner un code d'erreur 400."""
        reponse = self.client.post(
            reverse("api_question"),
            data="texte brut non-json",
            content_type="application/json"
        )
        self.assertEqual(reponse.status_code, 400)
        donnees = reponse.json()
        self.assertIn("answer", donnees)
        self.assertIn("invalide", donnees["answer"])
