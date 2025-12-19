"""
Module pour la gestion de la tab Films dans l'interface d'administration.
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import shutil
from PIL import Image

from admin_constants import COVERS_DIR, DB_FILMS, DB_SEANCES
from database import load_films, save_films, load_seances, save_seances


class FilmsTab:
	"""Gère la tab Films de l'interface d'administration."""
	
	def __init__(self, parent, admin_app):
		self.parent = parent
		self.admin_app = admin_app
		self.films = admin_app.films
		self.seances = admin_app.seances
		self.films_listbox = None
		self.entry_nom = None
		self.entry_rea = None
		self.entry_duree = None
		self.entry_genre = None
		self.entry_cover = None
	
	def build(self):
		"""Construit l'interface de la tab Films."""
		frame = self.parent
		
		left = tk.Frame(frame)
		left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		self.films_listbox = tk.Listbox(left)
		self.films_listbox.pack(fill=tk.BOTH, expand=True)
		self._refresh_films_list()
		
		btn_frame = tk.Frame(left)
		btn_frame.pack(fill=tk.X, pady=6)
		
		tk.Button(btn_frame, text="Supprimer un film", command=self.delete_selected_film).pack(side=tk.LEFT)
		
		# Formulaire ajout
		right = tk.Frame(frame)
		right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
		
		tk.Label(right, text="Ajouter un film").pack()
		
		tk.Label(right, text="Titre:").pack(anchor=tk.W)
		self.entry_nom = tk.Entry(right, width=30)
		self.entry_nom.pack()
		
		tk.Label(right, text="Réalisateur:").pack(anchor=tk.W)
		self.entry_rea = tk.Entry(right, width=30)
		self.entry_rea.pack()
		
		tk.Label(right, text="Durée (en minutes):").pack(anchor=tk.W)
		self.entry_duree = tk.Entry(right, width=10)
		self.entry_duree.pack()
		
		tk.Label(right, text="Genre:").pack(anchor=tk.W)
		self.entry_genre = tk.Entry(right, width=30)
		self.entry_genre.pack()
		
		tk.Label(right, text="Cover:").pack(anchor=tk.W)
		cover_frame = tk.Frame(right)
		cover_frame.pack(anchor=tk.W)
		self.entry_cover = tk.Entry(cover_frame, width=30)
		self.entry_cover.pack(side=tk.LEFT)
		tk.Button(cover_frame, text="Parcourir", command=self.select_cover_file).pack(side=tk.LEFT, padx=5)
		
		tk.Button(right, text="Ajouter", command=self.add_film).pack(pady=8)
	
	def _refresh_films_list(self):
		"""Rafraîchit la liste des films affichée."""
		self.films_listbox.delete(0, tk.END)
		for f in self.films:
			self.films_listbox.insert(tk.END, f"{f.id} — {f.nom} ({f.genre})")
	
	def add_film(self):
		"""Ajoute un film à la base de données."""
		nom = self.entry_nom.get().strip()
		rea = self.entry_rea.get().strip()
		duree = self.entry_duree.get().strip()
		genre = self.entry_genre.get().strip()
		cover_source = self.entry_cover.get().strip() or None
		
		if not nom:
			messagebox.showerror("Erreur", "Le titre est obligatoire.")
			return
		
		try:
			duree_val = int(duree) if duree else None
		except ValueError:
			messagebox.showerror("Erreur", "La durée doit être un entier (minutes).")
			return
		
		# Copier la cover dans media/images/covers si fournie
		cover_path = None
		if cover_source:
			try:
				if not os.path.exists(COVERS_DIR):
					os.makedirs(COVERS_DIR)
				filename = os.path.basename(cover_source)
				dest_path = os.path.join(COVERS_DIR, filename)
				self._crop_image_if_needed(cover_source, dest_path, ratio_threshold=0.7)
				cover_path = f"./{COVERS_DIR}/{filename}".replace("\\", "/")
			except Exception as e:
				messagebox.showerror("Erreur", f"Impossible de copier/traiter la cover: {e}")
				return
		
		# Calculer nouvel id
		from models import Film
		max_id = max((f.id for f in self.films if f.id is not None), default=0)
		new_id = max_id + 1
		
		film = Film(id=new_id, nom=nom, realisateur=rea or None, duree=duree_val, genre=genre or None, cover=cover_path)
		self.films.append(film)
		save_films(DB_FILMS, self.films)
		self._refresh_films_list()
		self.admin_app._refresh_film_combo()
		
		# Nettoyer le formulaire
		self.entry_nom.delete(0, tk.END)
		self.entry_rea.delete(0, tk.END)
		self.entry_duree.delete(0, tk.END)
		self.entry_genre.delete(0, tk.END)
		self.entry_cover.delete(0, tk.END)
	
	def delete_selected_film(self):
		"""Supprime le film sélectionné."""
		sel = self.films_listbox.curselection()
		if not sel:
			return
		idx = sel[0]
		film = self.films[idx]
		
		if not messagebox.askyesno("Confirmer", f"Supprimer le film '{film.nom}' ?"):
			return
		
		# Supprimer l'image de cover si elle existe
		if film.cover:
			try:
				cover_path = film.cover.replace("./", "").replace("\\", "/")
				if os.path.exists(cover_path):
					os.remove(cover_path)
			except Exception as e:
				print(f"Erreur lors de la suppression de l'image: {e}")
		
		# Supprimer toutes les séances associées à ce film
		self.seances = [s for s in self.seances if s.filmId != film.id]
		save_seances(DB_SEANCES, self.seances)
		
		# Supprimer et sauvegarder
		del self.films[idx]
		save_films(DB_FILMS, self.films)
		self._refresh_films_list()
		self.admin_app._refresh_film_combo()
		self.admin_app._refresh_seances_list()
		self.admin_app.show_schedule_for_day()
	
	def select_cover_file(self):
		"""Ouvre un dialog de sélection de fichier pour la cover."""
		file_path = filedialog.askopenfilename(
			title="Sélectionner une image de cover",
			filetypes=[("Images", "*.jpg *.jpeg *.png *.gif"), ("Tous les fichiers", "*.*")]
		)
		if file_path:
			self.entry_cover.delete(0, tk.END)
			self.entry_cover.insert(0, file_path)
	
	def _crop_image_if_needed(self, source_path, dest_path, ratio_threshold=0.7):
		"""Vérifie le ratio d'aspect et recadre l'image si nécessaire."""
		try:
			img = Image.open(source_path)
			width, height = img.size
			ratio = width / height if height > 0 else 1.0
			
			if ratio > ratio_threshold:
				# Recadrer en gardant la hauteur, réduire la largeur
				new_width = int(height * ratio_threshold)
				left = (width - new_width) // 2
				top = 0
				right = left + new_width
				bottom = height
				img = img.crop((left, top, right, bottom))
			
			# Sauvegarder l'image (avec conversion automatique du format)
			img.save(dest_path, quality=90)
		except Exception as e:
			raise Exception(f"Erreur lors du traitement de l'image: {e}")
