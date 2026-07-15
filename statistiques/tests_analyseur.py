"""Tests unitaires de l'analyseur de questions (statistiques/analyseur.py)."""

# pyrefly: ignore [missing-import]
from django.test import TestCase

from .analyseur import (
    analyser_question,
    detecter_indicateur,
    extraire_annees,
    normaliser_texte,
)


class TestAliasIndicateurs(TestCase):
    """Vérifie que plusieurs formulations pointent vers le bon champ."""

    def test_alias_chomage(self):
        for phrase in ["le chômage à Dakar", "le chomage a Dakar", "taux de chomage"]:
            with self.subTest(phrase=phrase):
                self.assertEqual(
                    detecter_indicateur(normaliser_texte(phrase)), "taux_chomage_pct"
                )

    def test_alias_internet(self):
        for phrase in ["accès à Internet", "acces a internet", "connexion internet"]:
            with self.subTest(phrase=phrase):
                self.assertEqual(
                    detecter_indicateur(normaliser_texte(phrase)), "acces_internet_pct"
                )

    def test_alias_population(self):
        self.assertEqual(
            detecter_indicateur(normaliser_texte("la population de Kolda")),
            "population",
        )

    def test_alias_production_cerealiere_prioritaire(self):
        # "production cerealiere" doit être reconnu en entier, pas juste "production"
        self.assertEqual(
            detecter_indicateur(normaliser_texte("la production céréalière")),
            "production_cerealiere_tonnes",
        )

    def test_aucun_alias(self):
        self.assertIsNone(detecter_indicateur(normaliser_texte("bonjour comment vas-tu")))


class TestExtractionAnnees(TestCase):
    """Vérifie l'extraction d'année seule, de plage, et l'absence d'année."""

    def test_annee_seule(self):
        debut, fin = extraire_annees(normaliser_texte("le chômage en 2022"))
        self.assertEqual((debut, fin), (2022, 2022))

    def test_plage_entre(self):
        debut, fin = extraire_annees(normaliser_texte("entre 2020 et 2024"))
        self.assertEqual((debut, fin), (2020, 2024))

    def test_plage_tiret(self):
        debut, fin = extraire_annees(normaliser_texte("évolution 2020-2024"))
        self.assertEqual((debut, fin), (2020, 2024))

    def test_absence_annee(self):
        debut, fin = extraire_annees(normaliser_texte("le chômage à Dakar"))
        self.assertEqual((debut, fin), (None, None))

    def test_annee_hors_plage_ignoree(self):
        debut, fin = extraire_annees(normaliser_texte("le chômage en 2019"))
        self.assertEqual((debut, fin), (None, None))


class TestAnalyserQuestion(TestCase):
    """Tests d'intégration légers sur analyser_question."""

    def test_question_complete(self):
        intent = analyser_question("Quel est le taux de chômage à Kaolack en 2022 ?")
        self.assertEqual(intent.indicator, "taux_chomage_pct")
        self.assertEqual(intent.regions, ["Kaolack"])
        self.assertEqual(intent.start_year, 2022)
        self.assertFalse(intent.needs_clarification)
        self.assertFalse(intent.hors_perimetre)

    def test_question_evolution(self):
        intent = analyser_question(
            "Évolution de l'accès à Internet à Kaolack entre 2020 et 2024"
        )
        self.assertEqual(intent.operation, "trend")
        self.assertEqual(intent.chart_type, "line")
        self.assertEqual((intent.start_year, intent.end_year), (2020, 2024))

    def test_question_ambigue_sans_indicateur(self):
        intent = analyser_question("Parle-moi de Dakar")
        self.assertTrue(intent.needs_clarification)
        self.assertIsNotNone(intent.clarification_message)

    def test_question_evolution_sans_annee_demande_clarification(self):
        intent = analyser_question("Évolution du chômage à Thiès")
        self.assertTrue(intent.needs_clarification)

    def test_region_inconnue_pas_de_region_detectee(self):
        # "Paris" n'est pas une région du Sénégal : elle n'est simplement
        # pas détectée (aucune exception), la question reste traitable
        # si un indicateur est présent (ex. clarification demandée).
        intent = analyser_question("Quel est le chômage à Paris ?")
        self.assertEqual(intent.regions, [])
        self.assertEqual(intent.indicator, "taux_chomage_pct")

    def test_question_hors_sujet_refus_poli(self):
        intent = analyser_question("Quelle est la météo aujourd'hui ?")
        self.assertTrue(intent.hors_perimetre)
        self.assertIsNotNone(intent.hors_perimetre_message)

    def test_question_vide(self):
        intent = analyser_question("")
        self.assertTrue(intent.needs_clarification)

    def test_pas_d_exception_sur_texte_aleatoire(self):
        try:
            analyser_question("###!!! %%% azertyuiop 12345678901234")
        except Exception as erreur:  # pragma: no cover - garde-fou explicite
            self.fail(f"analyser_question a levé une exception inattendue : {erreur}")