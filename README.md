# Gestion-Cinema-Python

Bienvenue sur notre programme de gestion d'un cinéma !

Grâce à nos deux interfaces graphiques, vous pouvez réserver une séance en tant que client via l’interface utilisateur, ainsi que gérer l’ajout et la suppression de films et de séances via l’interface administrateur.

Nous avons utilisé le format JSON pour la gestion de la base de données afin de sauvegarder les informations relatives aux films et aux séances, ainsi que Tkinter, une bibliothèque intégrée à Python, pour la création des interfaces graphiques.

La majorité des classes utilisées sont répertoriées dans le fichier models.py.

# GAI (interface graphique administrateur)
En exécutant le fichier main.py (ou directement le fichier d’administration), vous avez la possibilité de gérer les films et les séances. Un aperçu clair est disponible grâce à un tableau représentant les séances en fonction des salles.

# GUI (interfacte graphique utilisateur) :
Après validation de la journée dans l’interface administrateur, l’utilisateur peut accéder à la liste de tous les films disponibles. En sélectionnant un film, il peut choisir la séance qui l’intéresse et renseigner ses informations afin de réserver une place.
Enfin, un ticket récapitulatif contenant un QR code est généré.




### Installation

    Prérequis :
    - Installer les dépendances
    pip install -r requirements.txt
    - Pour lancer l'application : run -> main.py

