from models import (
	Personne,
	load_films,
	load_salles,
	load_seances,
	save_seances,
	load_places,
	save_places,
	create_places_for_seance,
	save_reservation,
	generate_ticket_code
)


DB_PERSONNES = "Database/Personnes.json"
DB_FILMS = "Database/Films.json"
DB_SALLES = "Database/Salles.json"
DB_SEANCES = "Database/Seances.json"
DB_RESERVATIONS = "Database/cache/reservations.json"


def display_places_grid(places, rows, cols):
	"""
	Affiche une grille ASCII des places disponibles/occupées.
	[O] = place occupée
	[ ] = place disponible
	"""
	print("\n" + "="*50)
	print(" "*20 + "ÉCRAN")
	print("="*50 + "\n")
	
	for r in range(1, rows + 1):
		row_str = f"Rangée {r:2d}  "
		for c in range(1, cols + 1):
			# Trouver la place correspondante
			place = next((p for p in places if p.row == r and p.column == c), None)
			if place and place.estOccupee:
				row_str += "[X] "
			else:
				row_str += "[ ] "
		print(row_str)
	
	print("\n" + "="*50)
	print("[ ] = disponible  |  [X] = occupée")
	print("="*50 + "\n")


def choose_seat(places, rows, cols):
	"""
	Demande à l'utilisateur de choisir une place disponible.
	Retourne la place sélectionnée ou None si annulation.
	"""
	display_places_grid(places, rows, cols)
	
	while True:
		row_input = input(f"Choisir une rangée (1-{rows}) ou q pour annuler: ").strip()
		if row_input.lower() == "q":
			return None
		
		try:
			row = int(row_input)
			if not (1 <= row <= rows):
				print(f"Rangée invalide. Choisissez entre 1 et {rows}.")
				continue
		except ValueError:
			print("Entrée invalide. Entrez un numéro de rangée.")
			continue
		
		col_input = input(f"Choisir une colonne (1-{cols}) ou q pour annuler: ").strip()
		if col_input.lower() == "q":
			return None
		
		try:
			col = int(col_input)
			if not (1 <= col <= cols):
				print(f"Colonne invalide. Choisissez entre 1 et {cols}.")
				continue
		except ValueError:
			print("Entrée invalide. Entrez un numéro de colonne.")
			continue
		
		# Vérifier si la place existe et est disponible
		place = next((p for p in places if p.row == row and p.column == col), None)
		if place is None:
			print("Place introuvable.")
			continue
		
		if place.estOccupee:
			print(f"La place (rangée {row}, colonne {col}) est déjà occupée. Choisissez une autre place.")
			display_places_grid(places, rows, cols)
			continue
		
		return place


def choose_from_list(items, display_fn):
	for i, it in enumerate(items, start=1):
		print(f"{i}. {display_fn(it)}")
	while True:
		choice = input("Choisir un numéro (ou q pour quitter): ")
		if choice.lower() == "q":
			return None
		try:
			idx = int(choice)
			if 1 <= idx <= len(items):
				return items[idx - 1]
		except ValueError:
			pass
		print("Choix invalide, réessayez.")


def cli():
	films = load_films(DB_FILMS)
	salles = load_salles(DB_SALLES)
	seances = load_seances(DB_SEANCES)

	print("Bienvenue — réservation terminal du cinéma")

	# 1) afficher tous les films
	print("\nFilms disponibles:")
	film = choose_from_list(films, lambda f: f.nom if getattr(f, 'nom', None) else "(sans nom)")
	if film is None:
		print("Annulation")
		return

	# 2) afficher horaires des séances du film
	# filtrer seulement les séances qui ont un filmId valide et un numéro de salle
	film_seances = [
		s
		for s in seances
		if getattr(s, "filmId", None) is not None
		and getattr(s, "salleNum", None) is not None
		and getattr(film, "id", None) is not None
		and s.filmId == film.id
	]
	if not film_seances:
		print("Aucune séance trouvée pour ce film.")
		return
	print(f"\nSéances pour {film.nom}:")
	seance = choose_from_list(film_seances, lambda s: f"{s.jour} {s.horaire} (salle {s.salleNum})")
	if seance is None:
		print("Annulation")
		return

	# trouver la salle
	salle = None
	salle_data = None
	for s in salles:
		if getattr(s, "numSalle", None) == getattr(seance, "salleNum", None):
			salle = s
			break
	if salle is None:
		print("Salle introuvable pour la séance sélectionnée.")
		return

	# Charger les données JSON brutes de la salle pour avoir row/column
	import json
	with open(DB_SALLES, "r", encoding="utf-8") as f:
		salles_json = json.load(f)
	salle_data = next((s for s in salles_json if s.get("numSalle") == salle.numSalle), None)
	if salle_data is None:
		print("Impossible de charger les informations de la salle.")
		return
	
	rows = salle_data.get("row", 10)
	cols = salle_data.get("column", 10)

	# Gérer les places pour la séance
	places = None
	places_file_path = None
	
	if seance.placesFile is not None:
		# Fichier de places existe déjà
		places = load_places(seance.placesFile)
		places_file_path = seance.placesFile
	
	if places is None:
		# Pas de fichier de places, on en créera un après le paiement
		# Pour l'instant, créer une grille vide temporaire
		places = create_places_for_seance(seance, salle_data)
		# Le fichier sera créé après validation du paiement
		places_file_path = f"Database/cache/seance_{seance.id}_places.json"
	
	# 2bis) Choix de la place
	print(f"\nChoisissez votre place pour la séance:")
	selected_place = choose_seat(places, rows, cols)
	if selected_place is None:
		print("Annulation")
		return

	# 3) afficher le prix et demander mail + catégorie
	# prix simple selon type de salle
	type_tarif = {"Standard": 10.0, "3D": 12.0, "Imax": 15.0}
	prix = type_tarif.get(getattr(salle, "type", "Standard"), 10.0)
	print(f"\nPrix pour la séance: {prix:.2f} € (salle {salle.type})")
	# Validation de l'e-mail: simple check pour la présence de '@' et d'un domaine
	while True:
		mail = input("Entrez votre e-mail (ou q pour annuler): ").strip()
		if mail.lower() == "q":
			print("Annulation")
			return
		# vérification basique: présence de '@' et d'un point dans la partie domaine
		if "@" in mail and "." in mail.split("@")[-1]:
			break
		print("E-mail invalide. Il doit contenir un '@' et un domaine (ex: user@exemple.com). Réessayez.")

	# Validation stricte de la catégorie: n'accepter que les choix proposés
	valid_categories = ["adulte", "etudiant", "étudiant", "enfant"]
	while True:
		categorie = input("Entrez votre catégorie (adulte/etudiant/enfant): ").strip().lower()
		if categorie not in valid_categories:
			print("Catégorie invalide. Choisissez parmi: adulte, etudiant, enfant.")
		else:
			break

	# créer personne (id None)
	personne = Personne(mail=mail, categorie=categorie)

	# 4) phase de paiement factice
	print("\n--- Paiement (factice) ---")
	paiement = input("Appuyez sur Entrée pour simuler le paiement (ou q pour annuler): ")
	if paiement.lower() == "q":
		print("Annulation du paiement.")
		return

	# Code généré pour le ticket
	code = generate_ticket_code()

	# Marquer la place comme occupée et associer le code de réservation
	selected_place.estOccupee = True
	selected_place.codeReservation = code

	# Sauvegarder le fichier des places
	save_places(places_file_path, places)

	# Mettre à jour la séance avec le path du fichier places si ce n'était pas déjà fait
	if seance.placesFile is None:
		seance.placesFile = places_file_path
		# Recharger toutes les séances, mettre à jour celle-ci, et sauvegarder
		all_seances = load_seances(DB_SEANCES)
		for s in all_seances:
			if s.id == seance.id:
				s.placesFile = places_file_path
				break
		save_seances(DB_SEANCES, all_seances)

	# Créer l'enregistrement de réservation
	reservation = {
		"code": code,
		"film": {
			"id": film.id,
			"nom": film.nom,
		},
		"seance": {
			"id": seance.id,
			"jour": seance.jour,
			"horaire": seance.horaire,
		},
		"salle": {
			"numSalle": salle.numSalle,
			"type": salle.type,
		},
		"place": {
			"row": selected_place.row,
			"column": selected_place.column,
		},
		"personne": {
			"mail": personne.mail,
			"categorie": personne.categorie,
		},
		"prix": prix,
	}
	save_reservation(DB_RESERVATIONS, reservation)

	# générer ticket (en mémoire)
	print("\nPaiement accepté ! Voici votre ticket :")
	print("------------------------------")
	print(f"CODE: {code}")
	print(f"Film: {film.nom}")
	print(f"Séance: {seance.jour} {seance.horaire}")
	print(f"Salle: {salle.numSalle} (type: {salle.type})")
	print(f"Place: Rangée {selected_place.row}, Colonne {selected_place.column}")
	print(f"Catégorie: {personne.categorie}")
	print(f"Prix: {prix:.2f} €")
	print("------------------------------")
	print("Présentez ce code à l'entrée pour scanner et accéder à la salle. Bon film !")


if __name__ == "__main__":
	cli()
