"""
Module de gestion des opérations de base de données (fichiers JSON).
Responsable du chargement et de la sauvegarde des données.
"""
import json
import os
from models import Personne, Film, Salle, Seance, Place


def load_json(path):
	"""Charge un fichier JSON et retourne son contenu."""
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


def save_json(path, data):
	"""Sauvegarde des données dans un fichier JSON."""
	# Créer le dossier parent si nécessaire
	directory = os.path.dirname(path)
	if directory and not os.path.exists(directory):
		os.makedirs(directory)
	
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=2, ensure_ascii=False)


def load_personnes(path):
	"""Charge la liste des personnes depuis un fichier JSON."""
	data = load_json(str(path))
	return [Personne.from_dict(d) for d in data]


def load_films(path):
	"""Charge la liste des films depuis un fichier JSON."""
	data = load_json(str(path))
	return [Film.from_dict(d) for d in data]


def load_salles(path):
	"""Charge la liste des salles depuis un fichier JSON."""
	data = load_json(str(path))
	return [Salle.from_dict(d) for d in data]


def load_seances(path):
	"""Charge la liste des séances depuis un fichier JSON."""
	data = load_json(str(path))
	return [Seance.from_dict(d) for d in data]


def save_seances(path, seances):
	"""Sauvegarde la liste des séances dans un fichier JSON."""
	data = [s.to_dict() for s in seances]
	save_json(path, data)


def load_places(path):
	"""Charge le fichier des places pour une séance."""
	if path is None:
		return None
	try:
		data = load_json(path)
		return [Place.from_dict(p) for p in data]
	except FileNotFoundError:
		return None


def save_places(path, places):
	"""Sauvegarde les places dans un fichier JSON."""
	data = [p.to_dict() for p in places]
	save_json(path, data)


def save_reservation(path, reservation):
	"""Ajoute une nouvelle réservation au fichier JSON. Crée le fichier s'il n'existe pas."""
	# Créer le dossier parent si nécessaire
	directory = os.path.dirname(path)
	if directory and not os.path.exists(directory):
		os.makedirs(directory)
	
	# Charger les réservations existantes ou créer une liste vide
	try:
		reservations = load_json(path)
	except FileNotFoundError:
		reservations = []
	
	reservations.append(reservation)
	save_json(path, reservations)
