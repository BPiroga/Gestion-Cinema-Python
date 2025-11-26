# Gestion-Cinema-Python


### Installation

    Prérequis :
    - Installer les dépendances
    pip install -r requirements.txt
    - Pour lancer l'application : run -> main.py

# TO DO

    # Administrateur
        - ouverture de l'interface sur l'ui admin (séparer de l'interface utilisateur)
        - Pour gérer les scéances :
                *faire un tableau avec dans les colonnes les horaires de la journée et dans les lignes les salles (à l'intérrieur sera afficher les films)
                *à côté mettre l'ajout de la séance : avec le choix du films (liste menu déroulant) et pour l'horaire mettre l'heure de début de film
                *gérer le test du créneau disponible pour la création de la séance
                *penser à la catégorie de la salle
        - Pour créer les films :
                *insérer les infos
                *importer une image (cover)
        - Pour l'interface générale mettre les boutons (gérer les séances, créer un film, valider la journée)

    # Ticket
        - Générer un ticket avec un qrcode
        - Créer en image ou en pdf
        - Le stocker dans un dossier
        - Ouvrir le pdf ou l'image
        - L'afficher aussi sur l'ui
        - Délai pour revenir sur l'accueil

    # Interface à améliorer:
        - Responsive ui
        - Scroll bar avec le pad
        - Visuel à améliorer (recentrer les éléments, arrondir le design)
        - Requète asynchrone (prix en fonction de la catégorie, erreur email)

    # Vérification
        - robustesse (test, test, test)
        - clareté du code
        - tester sur un nouvel environnement (VM)