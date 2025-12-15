"""
Interface d'administration (GUI Tkinter) pour gérer l'ajout et la suppression de films et des séances.
Utilisation des utilitaires de `database.py` pour charger et sauvegarder les JSON.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import subprocess
import sys
from PIL import Image

from database import (
	load_films,
	load_salles,
	load_seances,
	save_seances,
	save_films,
)
from models import Film, Seance

''' constantes des chemins de la base de données '''
DB_FILMS = "Database/Films.json"
DB_SALLES = "Database/Salles.json"
DB_SEANCES = "Database/Seances.json"
COVERS_DIR = "media/images/covers"


class AdminApp:
	def __init__(self, root):  
		self.root = root
		self.root.title("Administration - Gestion Cinéma")
		self.root.state('zoomed')  # plein écran

		# charger les données
		self.films = load_films(DB_FILMS)
		self.salles = load_salles(DB_SALLES)
		self.seances = load_seances(DB_SEANCES)

		# notebook
		self.nb = ttk.Notebook(root)
		self.nb.pack(fill=tk.BOTH, expand=True)

		# onglets
		self.tab_films = ttk.Frame(self.nb)
		self.tab_seances = ttk.Frame(self.nb)

		self.nb.add(self.tab_films, text="Films")
		self.nb.add(self.tab_seances, text="Séances")

		self._build_films_tab()
		self._build_seances_tab()

		# bouton "Valider la journée" en bas
		footer_frame = tk.Frame(root)
		footer_frame.pack(fill=tk.X, padx=10, pady=10)

		tk.Button(
			footer_frame,
			text="Valider la journée",
			command=self.validate_and_open_ui,
			bg="#4CAF50",
			fg="white",
			font=("Arial", 12, "bold"),
			height=2
		).pack()

	# ---------- Films ----------
	def _build_films_tab(self):
		frame = self.tab_films

		left = tk.Frame(frame)
		left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

		self.films_listbox = tk.Listbox(left)
		self.films_listbox.pack(fill=tk.BOTH, expand=True)
		self._refresh_films_list()

		btn_frame = tk.Frame(left)
		btn_frame.pack(fill=tk.X, pady=6)

		tk.Button(btn_frame, text="Supprimer un film", command=self.delete_selected_film).pack(side=tk.LEFT)

		# formulaire ajout
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
		self.films_listbox.delete(0, tk.END)
		for f in self.films:
			self.films_listbox.insert(tk.END, f"{f.id} — {f.nom} ({f.genre})")

	def add_film(self):
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

		# copier la cover dans media/images/covers si fournie
		cover_path = None
		if cover_source:
			try:
				if not os.path.exists(COVERS_DIR):
					os.makedirs(COVERS_DIR)
				# extraire le nom du fichier
				filename = os.path.basename(cover_source)
				dest_path = os.path.join(COVERS_DIR, filename)
				# traiter l'image (vérifier le ratio et recadrer si nécessaire, 
				                                # par exemple si l'image est plutôt carrée ça la coupe un peu pour qu'elle s'affiche bien)
				self._crop_image_if_needed(cover_source, dest_path, ratio_threshold=0.7)
				# sauvegarder le chemin relatif
				cover_path = f"./{COVERS_DIR}/{filename}".replace("\\", "/")
			except Exception as e:
				messagebox.showerror("Erreur", f"Impossible de copier/traiter la cover: {e}")
				return

		# calculer nouvel id
		max_id = max((f.id for f in self.films if f.id is not None), default=0)
		new_id = max_id + 1

		film = Film(id=new_id, nom=nom, realisateur=rea or None, duree=duree_val, genre=genre or None, cover=cover_path)
		self.films.append(film)
		save_films(DB_FILMS, self.films)
		self._refresh_films_list()
		# synchroniser le combo des films dans l'onglet séances
		self._refresh_film_combo()

		# clear form
		self.entry_nom.delete(0, tk.END)
		self.entry_rea.delete(0, tk.END)
		self.entry_duree.delete(0, tk.END)
		self.entry_genre.delete(0, tk.END)
		self.entry_cover.delete(0, tk.END)

	def delete_selected_film(self):
		sel = self.films_listbox.curselection()
		if not sel:
			return
		idx = sel[0]
		film = self.films[idx]

		if not messagebox.askyesno("Confirmer", f"Supprimer le film '{film.nom}' ?"):
			return

		# supprimer l'image de cover si elle existe
		if film.cover:
			try:
				# convertir le chemin relatif en chemin absolu
				cover_path = film.cover.replace("./", "").replace("\\", "/")
				if os.path.exists(cover_path):
					os.remove(cover_path)
			except Exception as e:
				# log l'erreur mais continue la suppression du film
				print(f"Erreur lors de la suppression de l'image: {e}")

		# supprimer toutes les séances associées à ce film
		self.seances = [s for s in self.seances if s.filmId != film.id]
		save_seances(DB_SEANCES, self.seances)

		# supprimer et sauvegarder
		del self.films[idx]
		save_films(DB_FILMS, self.films)
		self._refresh_films_list()
		# synchroniser le combo des films dans l'onglet séances
		self._refresh_film_combo()
		# rafraîchir la liste et l'emploi du temps des séances
		self._refresh_seances_list()
		self.show_schedule_for_day()

	def select_cover_file(self):
		"""Ouvre un dialog de sélection de fichier et remplit entry_cover avec le chemin choisi."""
		file_path = filedialog.askopenfilename(
			title="Sélectionner une image de cover",
			filetypes=[("Images", "*.jpg *.jpeg *.png *.gif"), ("Tous les fichiers", "*.*")]
		)
		if file_path:
			self.entry_cover.delete(0, tk.END)
			self.entry_cover.insert(0, file_path)

	def _crop_image_if_needed(self, source_path, dest_path, ratio_threshold=0.7):
		"""Vérifie le ratio d'aspect et recadre l'image si nécessaire.

		Si largeur/hauteur > ratio_threshold, coupe les bords gauche/droite
		pour obtenir un format plus portrait.
		"""
		try:
			img = Image.open(source_path)
			width, height = img.size
			ratio = width / height if height > 0 else 1.0

			if ratio > ratio_threshold:
				# recadrer en gardant la hauteur, réduire la largeur
				new_width = int(height * ratio_threshold)
				left = (width - new_width) // 2
				top = 0
				right = left + new_width
				bottom = height
				img = img.crop((left, top, right, bottom))

			# sauvegarder l'image (avec conversion automatique du format)
			img.save(dest_path, quality=90)
		except Exception as e:
			raise Exception(f"Erreur lors du traitement de l'image: {e}")

	# ---------- Séances ----------
	def _build_seances_tab(self):
		frame = self.tab_seances

		# frame supérieur : liste + formulaire côte à côte
		top_frame = tk.Frame(frame)
		top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

		# côté gauche : liste des séances
		left = tk.Frame(top_frame)
		left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

		tk.Label(left, text="Séances", font=("Arial", 10, "bold")).pack()

		self.seances_listbox = tk.Listbox(left)
		self.seances_listbox.pack(fill=tk.BOTH, expand=True)
		self._refresh_seances_list()

		btn_frame = tk.Frame(left)
		btn_frame.pack(fill=tk.X, pady=6)

		tk.Button(btn_frame, text="Supprimer une séance", command=self.delete_selected_seance).pack(side=tk.LEFT)

		# côté droit : formulaire ajout séance
		right = tk.Frame(top_frame)
		right.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

		tk.Label(right, text="Ajouter une séance", font=("Arial", 10, "bold")).pack()

		tk.Label(right, text="Film:").pack(anchor=tk.W)
		self.combo_film = ttk.Combobox(right, state="readonly")
		self.combo_film.pack()
		self._refresh_film_combo()

		tk.Label(right, text="Salle:").pack(anchor=tk.W)
		self.combo_salle = ttk.Combobox(right, state="readonly")
		self.combo_salle.pack()
		self._refresh_salle_combo()

		tk.Label(right, text="Horaire (ex: 20:30):").pack(anchor=tk.W)
		self.entry_horaire = tk.Entry(right, width=20)
		self.entry_horaire.pack()

		tk.Button(right, text="Ajouter une séance", command=self.add_seance).pack(pady=8)

		# frame inférieur : emploi du temps pleine largeur
		bottom_frame = tk.Frame(frame)
		bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

		tk.Label(bottom_frame, text="Emploi du temps de la journée", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

		# cadre pour l'emploi du temps (scrollable horizontalement si besoin)
		self.schedule_container = tk.Frame(bottom_frame)
		self.schedule_container.pack(fill=tk.BOTH, expand=True, pady=6)
		# afficher l'emploi du temps dès le chargement de l'onglet
		self.show_schedule_for_day()

	def _refresh_seances_list(self):
		self.seances = load_seances(DB_SEANCES)
		self.seances_listbox.delete(0, tk.END)
		for s in self.seances:
			filmname = next((f.nom for f in self.films if f.id == s.filmId), "—")
			self.seances_listbox.insert(tk.END, f"{s.id} — {s.jour} {s.horaire} — {filmname} — Salle {s.salleNum}")

	def show_schedule_for_day(self):
		"""Affiche l'emploi du temps avec TOUTES les séances, sans filtrer par date."""
		self.seances = load_seances(DB_SEANCES)
		self._render_schedule(None)  # None = ignorer la date, afficher toutes les séances

	def _render_schedule(self, day):
		"""Affiche un tableau salles x créneaux pour le jour donné.

		Les colonnes sont les horaires présents, les lignes sont les salles.
		On ignore complètement la date (paramètre day) et on prend toutes les séances, comme on garde le même emploi du temps pour chaque jour.
		Une ligne d'horaires au-dessus de chaque salle, puis les séances.
		"""
		# vider l'ancien contenu
		for w in self.schedule_container.winfo_children():
			w.destroy()

		# prendre TOUTES les séances, peu importe la date
		day_seances = list(self.seances)
		if not day_seances:
			tk.Label(self.schedule_container, text="Aucune séance disponible.").pack()
			return

		# normaliser tous les horaires au format HH:MM:SS avant de les utiliser
		for seance in day_seances:
			try:
				seance.horaire = self._normalize_horaire(seance.horaire)
			except ValueError:
				pass  # Garder l'horaire tel quel s'il ne peut pas être normalisé

		times = sorted({s.horaire for s in day_seances})
		salles = sorted(self.salles, key=lambda s: s.numSalle)

		# Frame principal avec scrollbars
		main_frame = tk.Frame(self.schedule_container)
		main_frame.pack(fill=tk.BOTH, expand=True)

		# Canvas avec scrollbars
		canvas = tk.Canvas(main_frame, height=500, bg='white')
		vbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
		
		inner = tk.Frame(canvas, bg='white')
		canvas.create_window((0, 0), window=inner, anchor='nw')
		canvas.configure(yscrollcommand=vbar.set)

		# rows (avec ligne d'horaires avant chaque salle)
		row_idx = 0
		for salle in salles:
			# ligne d'horaires pour cette salle
			lbl = tk.Label(inner, text='', width=10, height=1)
			lbl.grid(row=row_idx, column=0, sticky='nsew')
			
			for c_idx, t in enumerate(times, start=1):
				se = next((s for s in day_seances if s.salleNum == salle.numSalle and s.horaire == t), None)
				if se:
					# extraire horaires pour cette séance
					film_obj = next((f for f in self.films if f.id == se.filmId), None)
					duree = film_obj.duree if film_obj and film_obj.duree else 90
					
					try:
						h, m, s = map(int, se.horaire.split(':'))
						debut_min = h * 60 + m
						fin_min = debut_min + duree
						h_fin = fin_min // 60
						m_fin = fin_min % 60
						horaire_text = f"{h:02d}:{m:02d}-{h_fin:02d}:{m_fin:02d}"
					except (ValueError, AttributeError):
						horaire_text = se.horaire
					
					lbl = tk.Label(inner, text=horaire_text, borderwidth=1, relief='solid', width=12, height=1, font=("Arial", 8), bg='lightyellow')
				else:
					lbl = tk.Label(inner, text='', bg='white', width=12, height=1)
				lbl.grid(row=row_idx, column=c_idx, sticky='nsew')
			row_idx += 1
			
			# ligne salle + séances (sans horaires)
			lbl = tk.Label(inner, text=f"Salle {salle.numSalle}", borderwidth=1, relief='solid', width=10, height=5, font=("Arial", 10), bg='lightgray')
			lbl.grid(row=row_idx, column=0, sticky='nsew')
			for c_idx, t in enumerate(times, start=1):
				se = next((s for s in day_seances if s.salleNum == salle.numSalle and s.horaire == t), None)
				if se:
					# avec bordure pour séances existantes, affiche seulement le film (pas d'horaires)
					film = next((f.nom for f in self.films if f.id == se.filmId), '—')
					lbl = tk.Label(inner, text=film, borderwidth=1, relief='solid', width=12, height=5, font=("Arial", 9), wraplength=80, justify='center')
				else:
					# sans bordure pour cases vides (juste fond blanc)
					lbl = tk.Label(inner, text='', bg='white', width=12, height=5)
				lbl.grid(row=row_idx, column=c_idx, sticky='nsew')
			row_idx += 1

		inner.update_idletasks()
		canvas.config(scrollregion=canvas.bbox("all"))
		
		# Grid layout pour la scrollbar
		canvas.grid(row=0, column=0, sticky='nsew')
		vbar.grid(row=0, column=1, sticky='ns')
		
		main_frame.grid_rowconfigure(0, weight=1)
		main_frame.grid_columnconfigure(0, weight=1)
	
	def _refresh_film_combo(self):
		self.films = load_films(DB_FILMS)
		values = [f"{f.id} - {f.nom}" for f in self.films]
		self.combo_film['values'] = values
		if values:
			self.combo_film.current(0)

	def _refresh_salle_combo(self):
		self.salles = load_salles(DB_SALLES)
		values = [str(s.numSalle) for s in self.salles]
		self.combo_salle['values'] = values
		if values:
			self.combo_salle.current(0)

	def _normalize_horaire(self, horaire):
		"""Normalise un horaire au format HH:MM:SS."""
		try:
			if ':' in horaire:
				parts = horaire.split(':')
				if len(parts) == 2:
					# format HH:MM -> HH:MM:00
					return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:00"
				elif len(parts) == 3:
					# format HH:MM:SS
					return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:{parts[2].zfill(2)}"
			raise ValueError("Horaire invalide")
		except (ValueError, IndexError):
			raise ValueError("Format d'horaire invalide (utilisez HH:MM ou HH:MM:SS).")

	def _get_next_available_slot(self, salle_num, horaire_debut, film_duration):
		"""Vérifie les conflits et décale récursivement les séances impactées.
		
		Retourne un tuple (horaire_final, seances_a_decaler, accepte)
		- horaire_final: horaire où le film peut être inséré
		- seances_a_decaler: liste des séances à décaler [(seance, nouvel_horaire), ...]
		- accepte: True si l'utilisateur accepte les modifications, False sinon
		"""
		try:
			h, m, s = map(int, horaire_debut.split(':'))
			debut_min = h * 60 + m
		except (ValueError, AttributeError):
			return (None, [], False)
		
		fin_min = debut_min + film_duration + 20  # +20 min buffer
		
		# convertir minutes en HH:MM:SS
		def min_to_horaire(minutes):
			h = minutes // 60
			m = minutes % 60
			return f"{h:02d}:{m:02d}:00"
		
		# Étape 1: vérifier s'il y a un conflit avec l'horaire demandé
		conflit_seance = None
		for seance in self.seances:
			if seance.salleNum != salle_num:
				continue
			
			try:
				sh, sm, ss = map(int, seance.horaire.split(':'))
				s_debut_min = sh * 60 + sm
				
				film_obj = next((f for f in self.films if f.id == seance.filmId), None)
				s_duree = film_obj.duree if film_obj else 90
				s_fin_min = s_debut_min + s_duree + 20
				
				# si l'horaire demandé chevauche cette séance
				if not (fin_min <= s_debut_min or debut_min >= s_fin_min):
					conflit_seance = (seance, s_debut_min, s_fin_min)
					break
			except (ValueError, AttributeError):
				continue
		
		# s'il n'y a pas de conflit, pas de modifications
		if conflit_seance is None:
			return (horaire_debut, [], False)
		
		# Étape 2: il y a un conflit, proposer l'horaire de fin de la séance qui chevauche
		conflicting_seance, _, s_fin_min = conflit_seance
		proposed_debut_min = s_fin_min
		proposed_fin_min = proposed_debut_min + film_duration + 20
		proposed_horaire = min_to_horaire(proposed_debut_min)
		
		# Étape 3: vérifier récursivement si ce nouvel horaire impacte les séances suivantes
		seances_a_decaler = []
		
		def find_cascading_shifts(current_debut_min, current_fin_min, processed_seances=None):
			"""Trouve récursivement les séances à décaler."""
			if processed_seances is None:
				processed_seances = set()
			
			shifts = []
			
			for seance in self.seances:
				if seance.salleNum != salle_num or id(seance) in processed_seances:
					continue
				
				try:
					sh, sm, ss = map(int, seance.horaire.split(':'))
					s_debut_min = sh * 60 + sm
					
					film_obj = next((f for f in self.films if f.id == seance.filmId), None)
					s_duree = film_obj.duree if film_obj else 90
					s_fin_min = s_debut_min + s_duree + 20
					
					# si cette séance chevauche l'horaire proposé
					if not (current_fin_min <= s_debut_min or current_debut_min >= s_fin_min):
						# décaler cette séance après le nouvel horaire
						processed_seances.add(id(seance))
						new_debut_min = current_fin_min
						new_fin_min = new_debut_min + s_duree + 20
						
						shifts.append((seance, min_to_horaire(new_debut_min)))
						
						# vérifier récursivement les séances suivantes
						further_shifts = find_cascading_shifts(new_debut_min, new_fin_min, processed_seances)
						shifts.extend(further_shifts)
				except (ValueError, AttributeError):
					continue
			
			return shifts
		
		seances_a_decaler = find_cascading_shifts(proposed_debut_min, proposed_fin_min)
		
		# Étape 4: afficher un message de confirmation seulement s'il y a des décalages
		if not seances_a_decaler:
			# pas de décalages nécessaires, utiliser l'horaire proposé
			return (proposed_horaire, [], False)
		
		# des décalages sont nécessaires, demander confirmation
		msg = "Conflit détecté !\n\n"
		msg += f"Horaire demandé: {horaire_debut}\n"
		msg += f"Horaire proposé (fin du film conflictuel): {proposed_horaire}\n\n"
		msg += f"Séances à décaler:\n"
		for seance, new_horaire in seances_a_decaler:
			film_name = next((f.nom for f in self.films if f.id == seance.filmId), "?")
			msg += f"  • {film_name}: {seance.horaire} → {new_horaire}\n"
		msg += f"\nAccepter ces modifications ?"
		
		result = messagebox.askyesno("Décalage de séances", msg)
		
		if result:
			# appliquer les changements
			for seance, new_horaire in seances_a_decaler:
				seance.horaire = new_horaire
			return (proposed_horaire, seances_a_decaler, True)
		else:
			# l'utilisateur refuse, revenir au choix manuel
			return (None, [], False)

	def add_seance(self):
		film_sel = self.combo_film.get()
		salle_sel = self.combo_salle.get()
		horaire = self.entry_horaire.get().strip()

		if not film_sel or not salle_sel or not horaire:
			messagebox.showerror("Erreur", "Tous les champs sont obligatoires pour ajouter une séance.")
			return

		film_id = int(film_sel.split(" - ")[0])
		salle_num = int(salle_sel)

		# normaliser l'horaire au format HH:MM:SS
		try:
			horaire = self._normalize_horaire(horaire)
		except ValueError as e:
			messagebox.showerror("Erreur", str(e))
			return

		# vérifier les conflits et proposer des solutions
		film_obj = next((f for f in self.films if f.id == film_id), None)
		film_duree = film_obj.duree if film_obj else 90
		
		final_horaire, seances_a_decaler, accepte_decalage = self._get_next_available_slot(salle_num, horaire, film_duree)
		
		if final_horaire is None:
			# utilisateur a refusé toutes les solutions
			return
		
		# si des séances doivent être décalées, les modifier
		if seances_a_decaler:
			for seance, new_horaire in seances_a_decaler:
				seance.horaire = new_horaire
			save_seances(DB_SEANCES, self.seances)

		max_id = max((s.id for s in self.seances if s.id is not None), default=0)
		new_id = max_id + 1

		# créer la nouvelle séance
		jour = "01-01-2000"
		seance = Seance(id=new_id, jour=jour, horaire=final_horaire, filmId=film_id, salleNum=salle_num)
		self.seances.append(seance)
		save_seances(DB_SEANCES, self.seances)
		self._refresh_seances_list()
		# synchroniser l'emploi du temps
		self.show_schedule_for_day()

		# clear inputs
		self.entry_horaire.delete(0, tk.END)

	def delete_selected_seance(self):
		sel = self.seances_listbox.curselection()
		if not sel:
			return
		idx = sel[0]
		seance = self.seances[idx]

		if not messagebox.askyesno("Confirmer", f"Supprimer la séance {seance.jour} {seance.horaire} ?"):
			return

		del self.seances[idx]
		save_seances(DB_SEANCES, self.seances)
		self._refresh_seances_list()
		# synchroniser l'emploi du temps
		self.show_schedule_for_day()

	def validate_and_open_ui(self):
		"""Ferme l'interface admin et ouvre l'interface client (réservation)."""
		messagebox.showinfo("Journée validée", "Passage à l'interface client de réservation...")
		
		# fermer la fenêtre d'administration
		self.root.destroy()
		
		# lancer l'interface de réservation (ui.py)
		try:
			subprocess.Popen([sys.executable, "ui.py"])
		except Exception as e:
			messagebox.showerror("Erreur", f"Impossible de lancer l'interface client: {e}")


def main():
	root = tk.Tk()
	app = AdminApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
