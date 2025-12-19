"""
Module pour la gestion de la tab Séances dans l'interface d'administration.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from admin_constants import DB_SEANCES, JOURNEE_START_MIN, JOURNEE_END_MIN
from admin_dialogs import TimeConverter, ScheduleDialog
from database import load_seances, save_seances
from models import Seance


class SeancesTab:
	"""Gère la tab Séances de l'interface d'administration."""
	
	def __init__(self, parent, admin_app):
		self.parent = parent
		self.admin_app = admin_app
		self.films = admin_app.films
		self.salles = admin_app.salles
		self.seances = admin_app.seances
		self.combo_film = None
		self.combo_salle = None
		self.entry_horaire = None
		self.seances_listbox = None
		self.schedule_container = None
		self.time_converter = TimeConverter()
	
	def build(self):
		"""Construit l'interface de la tab Séances."""
		frame = self.parent
		
		# Frame supérieur : liste + formulaire côte à côte
		top_frame = tk.Frame(frame)
		top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		# Côté gauche : liste des séances
		left = tk.Frame(top_frame)
		left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
		
		tk.Label(left, text="Séances", font=("Arial", 10, "bold")).pack()
		
		self.seances_listbox = tk.Listbox(left)
		self.seances_listbox.pack(fill=tk.BOTH, expand=True)
		self._refresh_seances_list()
		
		btn_frame = tk.Frame(left)
		btn_frame.pack(fill=tk.X, pady=6)
		
		tk.Button(btn_frame, text="Supprimer une séance", command=self.delete_selected_seance).pack(side=tk.LEFT)
		
		# Côté droit : formulaire ajout séance
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
		
		# Frame inférieur : emploi du temps pleine largeur
		bottom_frame = tk.Frame(frame)
		bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
		
		tk.Label(bottom_frame, text="Emploi du temps de la journée", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
		
		self.schedule_container = tk.Frame(bottom_frame)
		self.schedule_container.pack(fill=tk.BOTH, expand=True, pady=6)
		self.show_schedule_for_day()
	
	def _refresh_seances_list(self):
		"""Rafraîchit la liste des séances affichée."""
		self.seances = load_seances(DB_SEANCES)
		self.seances_listbox.delete(0, tk.END)
		for s in self.seances:
			filmname = next((f.nom for f in self.films if f.id == s.filmId), "—")
			self.seances_listbox.insert(tk.END, f"{s.id} — {s.jour} {s.horaire} — {filmname} — Salle {s.salleNum}")
	
	def show_schedule_for_day(self):
		"""Affiche l'emploi du temps avec TOUTES les séances."""
		self.seances = load_seances(DB_SEANCES)
		self._render_schedule(None)
	
	def _render_schedule(self, day):
		"""Affiche un tableau salles x créneaux horaires avec gestion des chevauchements."""
		# Vider l'ancien contenu
		for w in self.schedule_container.winfo_children():
			w.destroy()
		
		day_seances = list(self.seances)
		if not day_seances:
			tk.Label(self.schedule_container, text="Aucune séance disponible.").pack()
			return
		
		# Normaliser tous les horaires
		for seance in day_seances:
			try:
				seance.horaire = self.time_converter.normalize_horaire(seance.horaire)
			except ValueError:
				pass
		
		salles = sorted(self.salles, key=lambda s: s.numSalle)
		
		# Créer les créneaux horaires
		from admin_constants import SLOT_DURATION, START_HOUR, END_HOUR
		time_slots = []
		for h in range(START_HOUR, END_HOUR):
			for m in [0, 30]:
				time_slots.append((h, m))
		
		# Frame principal avec scrollbars
		main_frame = tk.Frame(self.schedule_container)
		main_frame.pack(fill=tk.BOTH, expand=True)
		
		canvas = tk.Canvas(main_frame, height=500, bg='white')
		vbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
		hbar = ttk.Scrollbar(main_frame, orient='horizontal', command=canvas.xview)
		
		inner = tk.Frame(canvas, bg='white')
		canvas.create_window((0, 0), window=inner, anchor='nw')
		canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
		
		# En-tête avec les horaires
		tk.Label(inner, text="Salle", borderwidth=1, relief='solid', width=10, height=2, 
				font=("Arial", 10, "bold"), bg='lightgray').grid(row=0, column=0, sticky='nsew')
		
		for col_idx, (h, m) in enumerate(time_slots, start=1):
			tk.Label(inner, text=f"{h:02d}:{m:02d}", borderwidth=1, relief='solid', 
					width=6, height=2, font=("Arial", 8), bg='lightblue').grid(row=0, column=col_idx, sticky='nsew')
		
		# Pour chaque salle, afficher les séances
		for row_idx, salle in enumerate(salles, start=1):
			tk.Label(inner, text=f"Salle {salle.numSalle}", borderwidth=1, relief='solid', 
					width=10, height=3, font=("Arial", 10), bg='lightgray').grid(row=row_idx, column=0, sticky='nsew')
			
			salle_seances = [s for s in day_seances if s.salleNum == salle.numSalle]
			occupied_slots = set()
			
			for col_idx, (slot_h, slot_m) in enumerate(time_slots, start=1):
				slot_start_min = slot_h * 60 + slot_m
				seance_in_slot = None
				
				for se in salle_seances:
					try:
						h_deb, m_deb, s_deb = map(int, se.horaire.split(':'))
						debut_min = h_deb * 60 + m_deb
						
						film_obj = next((f for f in self.films if f.id == se.filmId), None)
						duree = film_obj.duree if film_obj and film_obj.duree else 90
						fin_min = debut_min + duree
						
						if debut_min <= slot_start_min < fin_min:
							seance_in_slot = se
							break
					except (ValueError, AttributeError):
						continue
				
				if seance_in_slot and col_idx not in occupied_slots:
					try:
						h_deb, m_deb, s_deb = map(int, seance_in_slot.horaire.split(':'))
						debut_min = h_deb * 60 + m_deb
						film_obj = next((f for f in self.films if f.id == seance_in_slot.filmId), None)
						duree = film_obj.duree if film_obj and film_obj.duree else 90
						fin_min = debut_min + duree
						
						nb_slots = max(1, (fin_min - debut_min + SLOT_DURATION - 1) // SLOT_DURATION)
						
						for i in range(nb_slots):
							occupied_slots.add(col_idx + i)
						
						film_nom = film_obj.nom if film_obj else "Film inconnu"
						h_fin = fin_min // 60
						m_fin = fin_min % 60
						
						lbl = tk.Label(inner, 
									text=f"{film_nom}\n{h_deb:02d}:{m_deb:02d}-{h_fin:02d}:{m_fin:02d}",
									borderwidth=2, relief='solid', 
									width=6*nb_slots, height=3, 
									font=("Arial", 8, "bold"), 
									bg='lightyellow',
									wraplength=6*nb_slots*7,
									justify='center')
						lbl.grid(row=row_idx, column=col_idx, columnspan=nb_slots, sticky='nsew')
					except (ValueError, AttributeError):
						lbl = tk.Label(inner, text='?', borderwidth=1, relief='solid', 
									width=6, height=3, bg='lightcoral')
						lbl.grid(row=row_idx, column=col_idx, sticky='nsew')
				elif col_idx not in occupied_slots:
					lbl = tk.Label(inner, text='', bg='white', width=6, height=3)
					lbl.grid(row=row_idx, column=col_idx, sticky='nsew')
		
		inner.update_idletasks()
		canvas.config(scrollregion=canvas.bbox("all"))
		
		canvas.grid(row=0, column=0, sticky='nsew')
		vbar.grid(row=0, column=1, sticky='ns')
		hbar.grid(row=1, column=0, sticky='ew')
		
		main_frame.grid_rowconfigure(0, weight=1)
		main_frame.grid_columnconfigure(0, weight=1)
	
	def _refresh_film_combo(self):
		"""Rafraîchit la combo des films."""
		from database import load_films
		from admin_constants import DB_FILMS
		self.films = load_films(DB_FILMS)
		values = [f"{f.id} - {f.nom}" for f in self.films]
		self.combo_film['values'] = values
		if values:
			self.combo_film.current(0)
	
	def _refresh_salle_combo(self):
		"""Rafraîchit la combo des salles."""
		from database import load_salles
		from admin_constants import DB_SALLES
		self.salles = load_salles(DB_SALLES)
		values = [str(s.numSalle) for s in self.salles]
		self.combo_salle['values'] = values
		if values:
			self.combo_salle.current(0)
	
	def add_seance(self):
		"""Ajoute une séance à la base de données."""
		film_sel = self.combo_film.get()
		salle_sel = self.combo_salle.get()
		horaire = self.entry_horaire.get().strip()
		
		if not film_sel or not salle_sel or not horaire:
			messagebox.showerror("Erreur", "Tous les champs sont obligatoires pour ajouter une séance.")
			return
		
		film_id = int(film_sel.split(" - ")[0])
		salle_num = int(salle_sel)
		
		# Normaliser l'horaire au format HH:MM:SS
		try:
			horaire = self.time_converter.normalize_horaire(horaire)
		except ValueError as e:
			messagebox.showerror("Erreur", str(e))
			return
		
		# Vérifier que l'horaire n'est pas avant 9h
		try:
			h, m, s = map(int, horaire.split(':'))
			horaire_min = h * 60 + m
			
			if horaire_min < JOURNEE_START_MIN:
				horaire_avant = horaire
				horaire = "09:00:00"
				msg = f"L'horaire demandé ({horaire_avant}) est avant 9h.\nIl sera décalé à 09:00:00."
				messagebox.showinfo("Ajustement d'horaire", msg)
		except (ValueError, AttributeError):
			pass
		
		# Vérifier les conflits et proposer des solutions
		film_obj = next((f for f in self.films if f.id == film_id), None)
		film_duree = film_obj.duree if film_obj else 90
		
		final_horaire, seances_a_decaler, accepte = self._get_next_available_slot(salle_num, horaire, film_duree)
		
		if final_horaire is None:
			return
		
		# Si des séances doivent être décalées, les modifier
		if seances_a_decaler:
			for seance, new_horaire in seances_a_decaler:
				seance.horaire = new_horaire
			save_seances(DB_SEANCES, self.seances)
		
		# Créer la nouvelle séance
		max_id = max((s.id for s in self.seances if s.id is not None), default=0)
		new_id = max_id + 1
		
		jour = "01-01-2000"
		seance = Seance(id=new_id, jour=jour, horaire=final_horaire, filmId=film_id, salleNum=salle_num)
		self.seances.append(seance)
		save_seances(DB_SEANCES, self.seances)
		self._refresh_seances_list()
		self.show_schedule_for_day()
		
		# Nettoyer
		self.entry_horaire.delete(0, tk.END)
	
	def delete_selected_seance(self):
		"""Supprime la séance sélectionnée."""
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
		self.show_schedule_for_day()
	
	def _get_next_available_slot(self, salle_num, horaire_debut, film_duration):
		"""Vérifie les conflits et gère le décalage des séances."""
		try:
			h, m, s = map(int, horaire_debut.split(':'))
			debut_min = h * 60 + m
		except (ValueError, AttributeError):
			return (None, [], False)
		
		fin_min = debut_min + film_duration + 20  # +20 min buffer
		
		# Vérifier que l'horaire de fin ne dépasse pas 24h
		if fin_min > JOURNEE_END_MIN:
			msg = f"Erreur: La séance se terminerait à {self.time_converter.min_to_horaire(fin_min, allow_overflow=True)}\n"
			msg += f"Elle dépasse la limite de 24h.\n\nVeuillez choisir un horaire antérieur."
			messagebox.showerror("Dépassement horaire", msg)
			return (None, [], False)
		
		# Étape 1: vérifier s'il y a un conflit
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
				
				if not (fin_min <= s_debut_min or debut_min >= s_fin_min):
					conflit_seance = (seance, s_debut_min, s_fin_min)
					break
			except (ValueError, AttributeError):
				continue
		
		if conflit_seance is None:
			msg = f"Pas de conflit détecté !\n\nSalle: {salle_num}\nHoraire: {horaire_debut}\nDurée: {film_duration} minutes\n"
			msg += f"Fin: {self.time_converter.min_to_horaire(fin_min)}\n\nAjouter la séance ?"
			
			result = messagebox.askyesno("Confirmation", msg)
			if result:
				return (horaire_debut, [], True)
			else:
				return (None, [], False)
		
		# Étape 2: Gérer le conflit
		conflicting_seance, s_debut_min_conflict, s_fin_min = conflit_seance
		
		proposed_debut_min_after = s_fin_min
		proposed_fin_min_after = proposed_debut_min_after + film_duration + 20
		proposed_horaire_after = self.time_converter.min_to_horaire(proposed_debut_min_after)
		
		option_after_valid = proposed_horaire_after is not None and proposed_fin_min_after <= JOURNEE_END_MIN
		
		# Option avant
		last_end_min_before = JOURNEE_START_MIN
		for seance in self.seances:
			if seance.salleNum != salle_num:
				continue
			
			try:
				sh, sm, ss = map(int, seance.horaire.split(':'))
				s_debut_min = sh * 60 + sm
				
				if s_debut_min < s_debut_min_conflict:
					film_obj = next((f for f in self.films if f.id == seance.filmId), None)
					s_duree = film_obj.duree if film_obj else 90
					s_fin_min_seance = s_debut_min + s_duree + 20
					
					if s_fin_min_seance > last_end_min_before:
						last_end_min_before = s_fin_min_seance
			except (ValueError, AttributeError):
				continue
		
		proposed_debut_min_before = last_end_min_before
		proposed_fin_min_before = proposed_debut_min_before + film_duration + 20
		
		option_before_available = (proposed_fin_min_before <= s_debut_min_conflict and 
								   proposed_fin_min_before <= JOURNEE_END_MIN and 
								   proposed_debut_min_before >= JOURNEE_START_MIN)
		proposed_horaire_before = self.time_converter.min_to_horaire(proposed_debut_min_before) if option_before_available else None
		
		# Afficher le dialogue
		conflicting_film_name = next((f.nom for f in self.films if f.id == conflicting_seance.filmId), "?")
		
		msg = f"Conflit détecté !\n\nFilm conflictuel: {conflicting_film_name} à {conflicting_seance.horaire}\n"
		msg += f"Horaire demandé: {horaire_debut}\n\n=== OPTIONS ===\n"
		
		if option_after_valid:
			msg += f"\nOption 1: Placer APRÈS le film conflictuel\nHoraire: {proposed_horaire_after}\n"
		else:
			msg += f"\nOption 1: Placer APRÈS le film conflictuel - NON DISPONIBLE\n"
		
		if option_before_available:
			msg += f"\nOption 2: Placer AVANT le film conflictuel\nHoraire: {proposed_horaire_before}\n"
		else:
			msg += f"\nOption 2: Placer AVANT le film conflictuel - NON DISPONIBLE\n"
		
		if not option_after_valid and not option_before_available:
			messagebox.showerror("Impossible", msg)
			return (None, [], False)
		
		dialog = ScheduleDialog(self.admin_app.root)
		result = dialog.show(msg, "Décalage de séances", has_option_2=option_before_available)
		
		if result == 1 and option_after_valid:
			return (proposed_horaire_after, [], True)
		elif result == 2 and option_before_available:
			return (proposed_horaire_before, [], True)
		else:
			return (None, [], False)
