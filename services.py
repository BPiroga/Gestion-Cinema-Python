"""
Module de services métier pour la gestion du cinéma.
Contient la logique métier (réservations, places, salles, etc.).
"""
import json
from models import Place
from database import load_seances, save_seances, save_places, save_reservation, load_places


def find_salle(salles, seance):
	"""Trouve et retourne la salle correspondant à une séance."""
	for s in salles:
		if getattr(s, "numSalle", None) == getattr(seance, "salleNum", None):
			return s
	return None


def load_salle_data(salle, db_salles_path):
	"""Charge les données brutes (row/column) d'une salle depuis le JSON."""
	with open(db_salles_path, "r", encoding="utf-8") as f:
		salles_json = json.load(f)
	salle_data = next((s for s in salles_json if s.get("numSalle") == salle.numSalle), None)
	return salle_data


def create_places_for_seance(seance, salle_data):
	"""Crée une grille de places vide pour une séance basée sur la salle."""
	rows = salle_data.get("row", 10)
	cols = salle_data.get("column", 10)
	places = []
	for r in range(1, rows + 1):
		for c in range(1, cols + 1):
			places.append(Place(row=r, column=c, estOccupee=False, codeReservation=None))
	return places


def get_or_create_places(seance, salle_data):
	"""Charge ou crée le fichier de places pour une séance."""
	places = None
	places_file_path = None
	
	if seance.placesFile is not None:
		places = load_places(seance.placesFile)
		places_file_path = seance.placesFile
	
	if places is None:
		places = create_places_for_seance(seance, salle_data)
		places_file_path = f"Database/cache/seance_{seance.id}_places.json"
	
	return places, places_file_path


def save_reservation_data(seance, places_file_path, places, selected_place, code, film, salle, personne, prix, db_seances_path, db_reservations_path):
	"""Sauvegarde les données de réservation (fichier places, séances, réservations)."""
	# Marquer la place comme occupée
	selected_place.estOccupee = True
	selected_place.codeReservation = code
	
	# Sauvegarder le fichier des places
	save_places(places_file_path, places)
	
	# Mettre à jour la séance avec le path du fichier places si nécessaire
	if seance.placesFile is None:
		seance.placesFile = places_file_path
		all_seances = load_seances(db_seances_path)
		for s in all_seances:
			if s.id == seance.id:
				s.placesFile = places_file_path
				break
		save_seances(db_seances_path, all_seances)
	
	# Créer et sauvegarder la réservation
	reservation = {
		"code": code,
		"film": {"id": film.id, "nom": film.nom},
		"seance": {"id": seance.id, "jour": seance.jour, "horaire": seance.horaire},
		"salle": {"numSalle": salle.numSalle, "type": salle.type},
		"place": {"row": selected_place.row, "column": selected_place.column},
		"personne": {"mail": personne.mail, "categorie": personne.categorie},
		"prix": prix,
	}
	save_reservation(db_reservations_path, reservation)


def generate_ticket_code():
	"""Génère un code unique pour un ticket de réservation."""
	import uuid
	return str(uuid.uuid4())
