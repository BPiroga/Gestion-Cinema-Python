"""
Module d'interface utilisateur (UI) pour le terminal.
Gère l'affichage et les interactions avec l'utilisateur.
"""
from models import Personne


def display_places_grid(places, rows, cols):
	"""Affiche une grille ASCII des places disponibles/occupées."""
	print("\n" + "="*50)
	print(" "*20 + "ÉCRAN")
	print("="*50 + "\n")
	
	for r in range(1, rows + 1):
		row_str = f"Rangée {r:2d}  "
		for c in range(1, cols + 1):
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
	"""Demande à l'utilisateur de choisir une place disponible."""
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
	"""Affiche une liste numérotée et permet à l'utilisateur de choisir un élément."""
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


def select_film(films):
	"""Affiche la liste des films et retourne le film choisi."""
	print("\nFilms disponibles:")
	film = choose_from_list(films, lambda f: f.nom if getattr(f, 'nom', None) else "(sans nom)")
	if film is None:
		print("Annulation")
		return None
	return film


def select_seance(seances, film):
	"""Affiche les séances pour un film et retourne la séance choisie."""
	film_seances = [
		s for s in seances
		if getattr(s, "filmId", None) is not None
		and getattr(s, "salleNum", None) is not None
		and getattr(film, "id", None) is not None
		and s.filmId == film.id
	]
	
	if not film_seances:
		print("Aucune séance trouvée pour ce film.")
		return None
	
	print(f"\nSéances pour {film.nom}:")
	seance = choose_from_list(film_seances, lambda s: f"{s.jour} {s.horaire} (salle {s.salleNum})")
	if seance is None:
		print("Annulation")
		return None
	
	return seance


def get_user_info(salle):
	"""Demande et valide l'email et la catégorie de l'utilisateur."""
	type_tarif = {"Standard": 10.0, "3D": 12.0, "Imax": 15.0}
	prix = type_tarif.get(getattr(salle, "type", "Standard"), 10.0)
	print(f"\nPrix pour la séance: {prix:.2f} € (salle {salle.type})")
	
	# Validation de l'e-mail
	while True:
		mail = input("Entrez votre e-mail (ou q pour annuler): ").strip()
		if mail.lower() == "q":
			print("Annulation")
			return None, None, None
		if "@" in mail and "." in mail.split("@")[-1]:
			break
		print("E-mail invalide. Il doit contenir un '@' et un domaine (ex: user@exemple.com). Réessayez.")
	
	# Validation de la catégorie
	valid_categories = ["adulte", "etudiant", "étudiant", "enfant"]
	while True:
		categorie = input("Entrez votre catégorie (adulte/etudiant/enfant): ").strip().lower()
		if categorie not in valid_categories:
			print("Catégorie invalide. Choisissez parmi: adulte, etudiant, enfant.")
		else:
			break
	
	personne = Personne(mail=mail, categorie=categorie)
	return personne, prix, mail


def confirm_payment():
	"""Demande confirmation du paiement."""
	print("\n--- Paiement (factice) ---")
	paiement = input("Appuyez sur Entrée pour simuler le paiement (ou q pour annuler): ")
	if paiement.lower() == "q":
		print("Annulation du paiement.")
		return False
	return True


def print_ticket(code, film, seance, salle, selected_place, personne, prix):
	"""Affiche le ticket de réservation."""
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
