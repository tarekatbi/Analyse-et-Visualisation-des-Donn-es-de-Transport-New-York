# Analyse et Visualisation des Données de Transport à New York

Ce projet vise à analyser et visualiser les données de transport à New York, couvrant les taxis jaunes, verts, et les services de VTC. L'application Streamlit permet d'explorer les données via des cartes interactives et des graphiques.

![1732566457076](image/README/1732566457076.png)

## Fonctionnalités

- Visualisation interactive des pick-ups et drop-offs sur une carte avec Kepler.gl.
- Filtres par type de service (Yellow, Green, VTC) et par date.
- Statistiques sur les trajets (distances parcourues, etc.).

## Regardez ma démo vidéo

[![Vidéo Démo](https://img.shields.io/badge/View%20Demo-blue)](assets/demo_app.mov)

## Prérequis

- **Python** (3.8 ou plus récent)
- **Git** (pour cloner le dépôt)

## Installation et Configuration

### Étape 1 : Cloner le dépôt

```bash
git clone https://github.com/tarekatbi/Analyse-et-Visualisation-des-Donn-es-de-Transport-New-York.git
cd Analyse-et-Visualisation-des-Donn-es-de-Transport-New-York
```

### Étape 2 : Créer un environnement virtuel

```bash
python -m venv env
```

### Étape 3 : Activer l'environnement virtuel

```bash
source env/bin/activate     #.\env\Scripts\activate For Windows
```

### Étape 4 : Installer les dépendances

Un fichier `requirements.txt` est fourni pour installer les packages nécessaires :

```bash
pip install -r requirements.txt

```

## Lancer l'application

Pour démarrer l'application Streamlit, exécutez la commande suivante :

```bash
streamlit run src/app.py
```
