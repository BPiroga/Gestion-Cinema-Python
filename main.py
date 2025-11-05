from models import (
	load_personnes,
	load_films,
	load_salles,
	load_seances,
	reserver_first_free_place,
	save_salles,
	generate_ticket_code,
	Personne,
)


DB_PERSONNES = "Database/Personnes.json"
DB_FILMS = "Database/Films.json"
DB_SALLES = "Database/Salles.json"
DB_SEANCES = "Database/Seances.json"


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
	personnes = load_personnes(DB_PERSONNES)
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
	for s in salles:
		if getattr(s, "numSalle", None) == getattr(seance, "salleNum", None):
			salle = s
			break
	if salle is None:
		print("Salle introuvable pour la séance sélectionnée.")
		return

	# 3) afficher le prix et demander mail + catégorie
	# prix simple selon type de salle
	type_tarif = {"Standard": 10.0, "3D": 12.0, "Imax": 15.0}
	prix = type_tarif.get(getattr(salle, "type", "Standard"), 10.0)
	print(f"\nPrix pour la séance: {prix:.2f} € (salle {salle.type})")
	mail = input("Entrez votre e-mail: ").strip()
	categorie = input("Entrez votre catégorie (adulte/etudiant/enfant): ").strip()

	# créer personne (id None)
	personne = Personne(id=None, mail=mail, categorie=categorie)

	# 4) phase de paiement factice
	print("\n--- Paiement (factice) ---")
	input("Appuyez sur Entrée pour simuler le paiement (ou q pour annuler): ")

	# 5) réservation automatique de la première place libre
	place = reserver_first_free_place(salle, personne)
	if place is None:
		print("Désolé, plus de places disponibles pour cette séance/salle.")
		return

	# sauvegarder les salles (persiste la réservation)
	save_salles(DB_SALLES, salles)

	# générer ticket
	code = generate_ticket_code()
	print("\nPaiement accepté ! Voici votre ticket :")
	print("------------------------------")
	print(f"CODE: {code}")
	print(f"Film: {film.nom}")
	print(f"Séance: {seance.jour} {seance.horaire}")
	print(f"Salle: {salle.numSalle} (type: {salle.type})")
	print(f"Place: colonne {place.column}, rangée {place.row}")
	print(f"Catégorie: {personne.categorie}")
	print("------------------------------")
	print("Présentez ce code à l'entrée pour scanner et accéder à la salle. Bon film !")


if __name__ == "__main__":
	cli()
