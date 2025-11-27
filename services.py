"""
Module de services métier pour la gestion du cinéma.
Contient la logique métier (réservations, places, salles, etc.).
"""
import json
import qrcode
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
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
	
	# Générer et sauvegarder le QR code
	qrcode_path = generate_qrcode(code, save_to_file=True)
	
	# Générer le PDF du billet
	pdf_path = generate_ticket_pdf(code, film, seance, salle, selected_place, personne, prix, qrcode_path)
	
	# Créer et sauvegarder la réservation
	reservation = {
		"code": code,
		"film": {"id": film.id, "nom": film.nom},
		"seance": {"id": seance.id, "jour": seance.jour, "horaire": seance.horaire},
		"salle": {"numSalle": salle.numSalle, "type": salle.type},
		"place": {"row": selected_place.row, "column": selected_place.column},
		"personne": {"mail": personne.mail, "categorie": personne.categorie},
		"prix": prix,
		"qrcode_path": qrcode_path,
		"pdf_path": pdf_path,
	}
	save_reservation(db_reservations_path, reservation)
	return qrcode_path, pdf_path


def generate_ticket_code():
	"""Génère un code unique pour un ticket de réservation."""
	import uuid
	return str(uuid.uuid4())


def generate_qrcode(code, save_to_file=False):
	"""
	Génère un QR code pour un code de réservation.
	
	Args:
		code: Le code de réservation à encoder
		save_to_file: Si True, sauvegarde le QR code dans le dossier qrcode
	
	Returns:
		Si save_to_file est True: le chemin du fichier sauvegardé
		Sinon: l'image du QR code
	"""
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_M,
		box_size=10,
		border=4,
	)
	qr.add_data(code)
	qr.make(fit=True)
	
	img = qr.make_image(fill_color="black", back_color="white")
	
	if save_to_file:
		# Créer le chemin du fichier dans le cache (sera supprimé à la fermeture)
		qrcode_dir = "Database/cache/qrcode"
		os.makedirs(qrcode_dir, exist_ok=True)
		output_path = f"{qrcode_dir}/{code}.png"
		img.save(output_path)
		return output_path
	
	return img


def generate_ticket_pdf(code, film, seance, salle, place, personne, prix, qrcode_path):
	"""
	Génère un PDF de billet de cinéma avec toutes les informations de réservation.
	
	Args:
		code: Code de réservation
		film: Objet Film
		seance: Objet Seance
		salle: Objet Salle
		place: Objet Place
		personne: Objet Personne
		prix: Prix de la réservation
		qrcode_path: Chemin vers l'image du QR code
	
	Returns:
		Le chemin du fichier PDF généré
	"""
	# Créer le dossier pour les billets PDF (permanents, ne seront pas supprimés)
	pdf_dir = "media/images/tickets"
	os.makedirs(pdf_dir, exist_ok=True)
	
	# Nom du fichier PDF avec timestamp
	timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
	pdf_path = f"{pdf_dir}/E-billet_{timestamp}.pdf"
	
	# Créer le PDF
	c = canvas.Canvas(pdf_path, pagesize=A4)
	width, height = A4
	
	# Couleurs et styles
	dark_bg = "#1a1a1a"
	accent_color = "#e50914"  # Rouge cinéma
	
	# En-tête avec fond sombre
	c.setFillColorRGB(0.1, 0.1, 0.1)
	c.rect(0, height - 100, width, 100, fill=True, stroke=False)
	
	# Titre
	c.setFillColorRGB(0.9, 0.04, 0.08)  # Rouge
	c.setFont("Helvetica-Bold", 28)
	c.drawCentredString(width/2, height - 45, "E-BILLET CINÉMA")
	
	c.setFillColorRGB(1, 1, 1)  # Blanc
	c.setFont("Helvetica", 10)
	c.drawCentredString(width/2, height - 70, f"Code de réservation: {code}")
	
	# Position de départ du contenu
	y_position = height - 130
	
	# Cover du film (si disponible)
	cover_height = 0
	if film.cover and os.path.exists(film.cover):
		try:
			cover_img = Image.open(film.cover)
			# Redimensionner proportionnellement
			max_width = 120
			max_height = 180
			cover_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
			
			# Centrer l'image
			img_reader = ImageReader(film.cover)
			img_width, img_height = cover_img.size
			cover_height = img_height
			x_pos = 50
			c.drawImage(img_reader, x_pos, y_position - img_height, 
					   width=img_width, height=img_height, preserveAspectRatio=True)
		except Exception as e:
			print(f"Erreur lors du chargement de la cover: {e}")
	
	# Informations du film (à droite de la cover)
	x_info = 190
	c.setFillColorRGB(0, 0, 0)
	c.setFont("Helvetica-Bold", 18)
	c.drawString(x_info, y_position, film.nom)
	
	y_position -= 25
	c.setFont("Helvetica", 11)
	c.drawString(x_info, y_position, f"Réalisateur: {film.realisateur}")
	
	y_position -= 18
	c.drawString(x_info, y_position, f"Genre: {film.genre}")
	
	y_position -= 18
	c.drawString(x_info, y_position, f"Durée: {film.duree} minutes")
	
	# Ajuster y_position pour éviter la superposition avec la cover
	# S'assurer qu'on est en dessous de la cover
	min_y_after_cover = (height - 130) - cover_height - 10
	if y_position > min_y_after_cover:
		y_position = min_y_after_cover
	
	# Ligne de séparation
	y_position -= 30
	c.setStrokeColorRGB(0.8, 0.8, 0.8)
	c.setLineWidth(1)
	c.line(50, y_position, width - 50, y_position)
	
	# Informations de la séance
	y_position -= 30
	c.setFont("Helvetica-Bold", 14)
	c.setFillColorRGB(0.9, 0.04, 0.08)
	c.drawString(50, y_position, "INFORMATIONS DE LA SÉANCE")
	
	y_position -= 25
	c.setFont("Helvetica", 11)
	c.setFillColorRGB(0, 0, 0)
	
	# Colonne gauche
	x_left = 50
	x_right = 320
	
	c.setFont("Helvetica-Bold", 11)
	c.drawString(x_left, y_position, "Date et heure:")
	c.setFont("Helvetica", 11)
	c.drawString(x_left + 100, y_position, f"{seance.jour} à {seance.horaire}")
	
	y_position -= 20
	c.setFont("Helvetica-Bold", 11)
	c.drawString(x_left, y_position, "Salle:")
	c.setFont("Helvetica", 11)
	c.drawString(x_left + 100, y_position, f"N°{salle.numSalle} ({salle.type})")
	
	y_position -= 20
	c.setFont("Helvetica-Bold", 11)
	c.drawString(x_left, y_position, "Place:")
	c.setFont("Helvetica", 11)
	c.drawString(x_left + 100, y_position, f"Rangée {place.row}, Siège {place.column}")
	
	# Ligne de séparation
	y_position -= 30
	c.setStrokeColorRGB(0.8, 0.8, 0.8)
	c.line(50, y_position, width - 50, y_position)
	
	# Informations du client
	y_position -= 30
	c.setFont("Helvetica-Bold", 14)
	c.setFillColorRGB(0.9, 0.04, 0.08)
	c.drawString(50, y_position, "INFORMATIONS CLIENT")
	
	y_position -= 25
	c.setFont("Helvetica-Bold", 11)
	c.setFillColorRGB(0, 0, 0)
	c.drawString(x_left, y_position, "Email:")
	c.setFont("Helvetica", 11)
	c.drawString(x_left + 100, y_position, personne.mail)
	
	y_position -= 20
	c.setFont("Helvetica-Bold", 11)
	c.drawString(x_left, y_position, "Catégorie:")
	c.setFont("Helvetica", 11)
	c.drawString(x_left + 100, y_position, personne.categorie)
	
	# Prix
	y_position -= 30
	c.setFont("Helvetica-Bold", 16)
	c.setFillColorRGB(0.9, 0.04, 0.08)
	c.drawString(50, y_position, f"PRIX: {prix:.2f} €")
	
	# QR Code
	if qrcode_path and os.path.exists(qrcode_path):
		try:
			qr_size = 150
			qr_x = width - qr_size - 50
			qr_y = y_position - qr_size - 20
			
			c.drawImage(qrcode_path, qr_x, qr_y, width=qr_size, height=qr_size)
			
			# Texte sous le QR code
			c.setFont("Helvetica-Bold", 10)
			c.setFillColorRGB(0, 0, 0)
			c.drawCentredString(qr_x + qr_size/2, qr_y - 15, "Présentez ce code à l'entrée")
		except Exception as e:
			print(f"Erreur lors de l'ajout du QR code au PDF: {e}")
	
	# Pied de page
	c.setFont("Helvetica-Oblique", 9)
	c.setFillColorRGB(0.5, 0.5, 0.5)
	c.drawCentredString(width/2, 40, "Merci de votre visite et bon film !")
	c.drawCentredString(width/2, 25, f"Billet généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
	
	# Sauvegarder le PDF
	c.save()
	
	# Vérification de sécurité que le fichier est bien créé et non vide
	if not os.path.exists(pdf_path):
		raise Exception(f"Le fichier PDF n'a pas été créé: {pdf_path}")
	
	file_size = os.path.getsize(pdf_path)
	if file_size == 0:
		raise Exception(f"Le fichier PDF est vide: {pdf_path}")
	
	return pdf_path