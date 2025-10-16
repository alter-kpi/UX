# Analyse SUS – Application Streamlit

Cette application Streamlit permet d'importer un fichier Excel contenant les réponses à un questionnaire System Usability Scale (SUS), de calculer automatiquement les scores, de générer des visualisations interactives et de produire un rapport PDF prêt à être partagé.

## Prérequis

- Python 3.9 ou supérieur.
- `pip` pour installer les dépendances.

> 💡 Un fichier `template_sus.xlsx` est fourni à la racine du projet. Il peut servir de modèle pour saisir vos réponses et tester rapidement l'application.

## Installation

1. (Optionnel) Créez un environnement virtuel :

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # sous Windows : .venv\Scripts\activate
   ```

2. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

## Lancer l'application

1. Démarrez Streamlit :

   ```bash
   streamlit run app.py
   ```

2. Ouvrez l'URL fournie par Streamlit (généralement `http://localhost:8501`).

3. Dans l'interface :
   - Téléchargez le modèle Excel depuis le bouton dédié si besoin.
   - Chargez votre fichier de réponses via le téléverseur.
   - Explorez les graphiques, statistiques et exportez le rapport PDF.

## Comment tester les changements

Après avoir modifié le code :

1. Redémarrez l'application avec `streamlit run app.py` si elle était déjà lancée.
2. Téléversez un fichier de test (par exemple une copie du `template_sus.xlsx` complétée avec des valeurs fictives comprises entre 1 et 5).
3. Vérifiez que :
   - Le score moyen s'affiche correctement dans la jauge sur fond blanc avec texte noir.
   - Les histogrammes, graphiques radar et tableaux reflètent vos données de test.
   - Le bouton « Générer le rapport PDF » produit un document téléchargeable sans erreur.

Si des erreurs apparaissent, consultez les messages affichés dans Streamlit ou la console depuis laquelle vous avez lancé la commande `streamlit run` pour obtenir plus de détails.

## Dépannage

- Assurez-vous que le fichier Excel contient bien les colonnes `Question1` à `Question10` avec des valeurs numériques entre 1 et 5.
- Les colonnes facultatives (catégories) doivent se trouver entre les colonnes L et O du modèle.
- Si le PDF ne se télécharge pas, vérifiez qu'aucun caractère spécial non supporté n'est présent dans vos données.

## Licence

Ce projet est fourni à des fins de démonstration. Adaptez-le librement à vos besoins professionnels.

