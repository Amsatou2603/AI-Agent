"""Vues de l'application statistiques."""

# pyrefly: ignore [missing-import]
from django.shortcuts import render


def accueil(request):
    """Page d'accueil — affiche le template de base du projet."""
    return render(request, "base.html")
