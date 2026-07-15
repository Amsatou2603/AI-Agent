"""Tests du moteur de requêtes ORM (statistiques/moteur.py)."""

# pyrefly: ignore [missing-import]
from django.test import TestCase

from .analyseur import QueryIntent, analyser_question
from .models import StatistiqueRegionale
from .moteur import executer_intention


class TestMoteurORM(TestCase):
    """Insère un petit jeu de données en mémoire et teste chaque opération."""

    def setUp(self):
        donnees = [
            ("Kaolack", 2020, 1_200_000, 45.0, 55.0, 12.0, 40.0, 41.0, 20, 70.0, 50_000),
            ("Kaolack", 2021, 1_220_000, 46.0, 56.0, 12.5, 39.0, 45.2, 21, 71.0, 51_000),
            ("Kaolack", 2022, 1_240_000, 47.0, 57.0, 13.0, 38.0, 49.4, 22, 72.0, 52_000),
            ("Kaolack", 2023, 1_260_000, 48.0, 58.0, 13.5, 37.0, 53.6, 23, 73.0, 53_000),
            ("Kaolack", 2024, 1_280_000, 49.0, 59.0, 14.0, 36.0, 57.8, 24, 74.0, 54_000),
            ("Dakar", 2024, 4_300_000, 98.0, 85.0, 15.0, 6.0, 88.0, 150, 94.0, 20_000),
            ("Thiès", 2024, 2_000_000, 60.0, 70.0, 10.0, 25.0, 60.0, 60, 80.0, 30_000),
        ]
        champs = (
            "region", "annee", "population", "taux_urbanisation_pct",
            "taux_alphabetisation_pct", "taux_chomage_pct", "taux_pauvrete_pct",
            "acces_internet_pct", "centres_sante", "taux_scolarisation_pct",
            "production_cerealiere_tonnes",
        )
        for ligne in donnees:
            StatistiqueRegionale.objects.create(**dict(zip(champs, ligne)))

    def test_operation_value(self):
        intent = QueryIntent(
            indicator="acces_internet_pct", regions=["Kaolack"],
            start_year=2020, end_year=2020, operation="value",
        )
        resultat = executer_intention(intent)
        self.assertEqual(resultat["table"], [{"annee": 2020, "valeur": 41.0}])
        self.assertIn("Kaolack", resultat["answer"])
        self.assertIsNone(resultat["chart"])

    def test_operation_trend(self):
        intent = QueryIntent(
            indicator="acces_internet_pct", regions=["Kaolack"],
            start_year=2020, end_year=2024, operation="trend",
        )
        resultat = executer_intention(intent)
        self.assertEqual(len(resultat["table"]), 5)
        self.assertEqual(resultat["chart"]["type"], "line")
        self.assertEqual(resultat["chart"]["labels"], [2020, 2021, 2022, 2023, 2024])

    def test_operation_compare(self):
        intent = QueryIntent(
            indicator="taux_chomage_pct", regions=["Kaolack", "Dakar"],
            start_year=2024, end_year=2024, operation="compare",
        )
        resultat = executer_intention(intent)
        self.assertEqual(resultat["chart"]["type"], "bar")
        self.assertEqual(len(resultat["table"]), 2)

    def test_operation_ranking(self):
        intent = QueryIntent(
            indicator="acces_internet_pct", regions=[],
            start_year=2024, end_year=2024, operation="ranking", limit=2,
        )
        resultat = executer_intention(intent)
        self.assertEqual(len(resultat["table"]), 2)
        # Dakar (88.0) doit être premier, devant Thiès (60.0) et Kaolack (57.8)
        self.assertEqual(resultat["table"][0]["region"], "Dakar")

    def test_operation_sum(self):
        intent = QueryIntent(
            indicator="production_cerealiere_tonnes", regions=["Kaolack"],
            operation="sum",
        )
        resultat = executer_intention(intent)
        self.assertEqual(resultat["table"][0]["valeur"], 50_000 + 51_000 + 52_000 + 53_000 + 54_000)

    def test_operation_average(self):
        intent = QueryIntent(
            indicator="taux_chomage_pct", regions=["Kaolack"], operation="average",
        )
        resultat = executer_intention(intent)
        self.assertAlmostEqual(resultat["table"][0]["valeur"], 13.0, places=1)

    def test_region_inconnue_refus_poli(self):
        intent = QueryIntent(
            indicator="taux_chomage_pct", regions=["Paris"], operation="value",
        )
        resultat = executer_intention(intent)
        self.assertIn("non reconnue", resultat["answer"])
        self.assertEqual(resultat["table"], [])

    def test_annee_sans_donnee(self):
        intent = QueryIntent(
            indicator="taux_chomage_pct", regions=["Kaolack"],
            start_year=2099, end_year=2099, operation="value",
        )
        resultat = executer_intention(intent)
        self.assertEqual(resultat["table"], [])
        self.assertIn("Aucune donnée", resultat["answer"])

    def test_question_ambigue_de_bout_en_bout(self):
        intent = analyser_question("Parle-moi de Dakar")
        self.assertTrue(intent.needs_clarification)
        resultat = executer_intention(intent)
        self.assertEqual(resultat["table"], [])

    def test_question_hors_sujet_de_bout_en_bout(self):
        intent = analyser_question("Quel temps fait-il aujourd'hui ?")
        self.assertTrue(intent.hors_perimetre)
        resultat = executer_intention(intent)
        self.assertEqual(resultat["table"], [])

    def test_champ_non_autorise_refuse(self):
        # Vérifie que le moteur refuse toute valeur hors de sa liste blanche,
        # même si elle provient directement d'un QueryIntent construit à la main.
        intent = QueryIntent(
            indicator="mot_de_passe_admin", regions=["Kaolack"], operation="value",
        )
        resultat = executer_intention(intent)
        self.assertEqual(resultat["table"], [])
        self.assertIn("inconnu", resultat["answer"].lower())