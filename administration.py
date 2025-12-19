"""
Interface Graphique d'administration (GUI Tkinter) pour gérer l'ajout et la suppression de films et des séances.
Utilisation des utilitaires de `database.py` pour charger et sauvegarder les JSON.

Ce fichier contient la classe principale AdminApp qui gère l'interface générale.
Les onglets spécifiques (Films et Séances) sont délégués à leurs modules respectifs.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

from admin_constants import DB_FILMS, DB_SALLES, DB_SEANCES
from admin_films_tab import FilmsTab
from admin_seances_tab import SeancesTab
from database import load_films, load_salles, load_seances


class AdminApp:
	"""Application principale d'administration du cinéma."""
	
	def __init__(self, root):  
		self.root = root
		self.root.title("Administration - Gestion Cinéma")
		self.root.state('zoomed')  # plein écran

		# Charger les données
		self.films = load_films(DB_FILMS)
		self.salles = load_salles(DB_SALLES)
		self.seances = load_seances(DB_SEANCES)

		# Notebook (conteneur d'onglets)
		self.nb = ttk.Notebook(root)
		self.nb.pack(fill=tk.BOTH, expand=True)

		# Créer les onglets
		self.tab_films = ttk.Frame(self.nb)
		self.tab_seances = ttk.Frame(self.nb)

		self.nb.add(self.tab_films, text="Films")
		self.nb.add(self.tab_seances, text="Séances")

		# Initialiser les modules d'onglets
		self.films_tab = FilmsTab(self.tab_films, self)
		self.films_tab.build()

		self.seances_tab = SeancesTab(self.tab_seances, self)
		self.seances_tab.build()

		# Bouton "Valider la journée" en bas
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

	def _refresh_film_combo(self):
		"""Rafraîchit le combo des films de la tab séances."""
		self.seances_tab._refresh_film_combo()

	def _refresh_seances_list(self):
		"""Rafraîchit la liste des séances de la tab séances."""
		self.seances_tab._refresh_seances_list()

	def show_schedule_for_day(self):
		"""Affiche l'emploi du temps de la journée."""
		self.seances_tab.show_schedule_for_day()

	def validate_and_open_ui(self):
		"""Ferme l'interface admin et ouvre l'interface client (réservation)."""
		messagebox.showinfo("Journée validée", "Passage à l'interface client de réservation...")
		
		# Fermer la fenêtre d'administration
		self.root.destroy()
		
		# Lancer l'interface de réservation (ui.py)
		try:
			subprocess.Popen([sys.executable, "ui.py"])
		except Exception as e:
			messagebox.showerror("Erreur", f"Impossible de lancer l'interface client: {e}")


def main():
	"""Fonction principale pour lancer l'application."""
	root = tk.Tk()
	app = AdminApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
