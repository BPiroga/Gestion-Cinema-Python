"""
Module utilitaire pour la gestion des dialogues et des conversions horaires.
"""
import tkinter as tk
from tkinter import ttk


class ScheduleDialog:
	"""Dialogue personnalisée pour gérer les conflits d'horaires."""
	
	def __init__(self, root):
		self.root = root
		self.result = 0
	
	def show(self, message, title, has_option_2=True):
		"""
		Affiche une boîte de dialogue avec des boutons pour les options de conflit.
		Retourne:
		- 1 si "Option 1" (décaler après) est cliquée
		- 2 si "Option 2" (placer avant) est cliquée
		- 0 si "Annuler" est cliquée
		"""
		dialog = tk.Toplevel(self.root)
		dialog.title(title)
		dialog.geometry("600x400")
		dialog.resizable(False, False)
		dialog.transient(self.root)
		dialog.grab_set()
		
		# Centrer la fenêtre par rapport à la fenêtre parent
		dialog.update_idletasks()
		x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
		y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
		dialog.geometry(f"+{x}+{y}")
		
		# Zone de texte avec scrollbar
		frame_text = ttk.Frame(dialog)
		frame_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		scrollbar = ttk.Scrollbar(frame_text)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		text_widget = tk.Text(frame_text, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=15, width=70)
		text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.config(command=text_widget.yview)
		
		text_widget.insert(tk.END, message)
		text_widget.config(state=tk.DISABLED)
		
		# Frame pour les boutons
		frame_buttons = ttk.Frame(dialog)
		frame_buttons.pack(fill=tk.X, padx=10, pady=10)
		
		result_var = tk.IntVar(value=0)
		
		def on_option1():
			result_var.set(1)
			dialog.destroy()
		
		def on_option2():
			result_var.set(2)
			dialog.destroy()
		
		def on_cancel():
			result_var.set(0)
			dialog.destroy()
		
		btn_option1 = ttk.Button(frame_buttons, text="Option 1", command=on_option1)
		btn_option1.pack(side=tk.LEFT, padx=5)
		
		if has_option_2:
			btn_option2 = ttk.Button(frame_buttons, text="Option 2", command=on_option2)
			btn_option2.pack(side=tk.LEFT, padx=5)
		
		btn_cancel = ttk.Button(frame_buttons, text="Annuler", command=on_cancel)
		btn_cancel.pack(side=tk.RIGHT, padx=5)
		
		self.root.wait_window(dialog)
		return result_var.get()


class TimeConverter:
	"""Utilitaire pour convertir les horaires."""
	
	@staticmethod
	def normalize_horaire(horaire):
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
	
	@staticmethod
	def min_to_horaire(minutes, allow_overflow=False):
		"""
		Convertit les minutes (depuis minuit) en format HH:MM:SS.
		Si allow_overflow=True, on représente les heures > 24 (ex: 1500 min = 25:00)
		Sinon, on retourne None si dépassement de 24h.
		"""
		if minutes < 0:
			return None
		
		h = minutes // 60
		m = minutes % 60
		
		if not allow_overflow and h >= 24:
			return None  # Dépassement de 24h
		
		return f"{h:02d}:{m:02d}:00"
	
	@staticmethod
	def horaire_to_min(horaire):
		"""Convertit un horaire HH:MM:SS en minutes depuis minuit."""
		try:
			h, m, s = map(int, horaire.split(':'))
			return h * 60 + m
		except (ValueError, AttributeError):
			return None
