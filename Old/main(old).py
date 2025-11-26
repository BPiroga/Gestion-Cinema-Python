"""
Point d'entrée principal du système de réservation de cinéma.
Orchestre le flux de réservation en utilisant les modules database, services et ui.
"""
from database import (
    load_films, load_salles, load_seances
)
from services import (
	find_salle,
	load_salle_data,
	get_or_create_places,
	save_reservation_data,
	generate_ticket_code
)
from ui import (
	select_film,
	select_seance,
	choose_seat,
	get_user_info,
	confirm_payment,
	print_ticket
)


# Chemins des fichiers de base de données
DB_PERSONNES = "Database/Personnes.json"
DB_FILMS = "Database/Films.json"
DB_SALLES = "Database/Salles.json"
DB_SEANCES = "Database/Seances.json"
DB_RESERVATIONS = "Database/cache/reservations.json"


def cli():
	"""Fonction principale du système de réservation."""
	# Charger les données
	films = load_films(DB_FILMS)
	salles = load_salles(DB_SALLES)
	seances = load_seances(DB_SEANCES)

	print("Bienvenue — réservation terminal du cinéma")

	# Étape 1: Choisir un film
	film = select_film(films)
	if film is None:
		return

	# Étape 2: Choisir une séance
	seance = select_seance(seances, film)
	if seance is None:
		return

	# Étape 3: Trouver la salle
	salle = find_salle(salles, seance)
	if salle is None:
		print("Salle introuvable pour la séance sélectionnée.")
		return

	# Charger les informations de la salle (row/column)
	salle_data = load_salle_data(salle, DB_SALLES)
	if salle_data is None:
		print("Impossible de charger les informations de la salle.")
		return
	
	rows = salle_data.get("row", 10)
	cols = salle_data.get("column", 10)

	# Étape 4: Gérer les places
	places, places_file_path = get_or_create_places(seance, salle_data)
	
	# Étape 5: Choisir une place
	print(f"\nChoisissez votre place pour la séance:")
	selected_place = choose_seat(places, rows, cols)
	if selected_place is None:
		print("Annulation")
		return

	# Étape 6: Collecter les informations utilisateur
	personne, prix, mail = get_user_info(salle)
	if personne is None:
		return

	# Étape 7: Confirmer le paiement
	if not confirm_payment():
		return

	# Étape 8: Générer le code et sauvegarder
	code = generate_ticket_code()
	save_reservation_data(
		seance, places_file_path, places, selected_place, code,
		film, salle, personne, prix,
		DB_SEANCES, DB_RESERVATIONS
	)

	# Étape 9: Afficher le ticket
	print_ticket(code, film, seance, salle, selected_place, personne, prix)


if __name__ == "__main__":
	cli()



if __name__ == "__main__":
	cli()
