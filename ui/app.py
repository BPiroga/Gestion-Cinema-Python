"""
Classe principale de l'application de réservation de cinéma.
"""
import tkinter as tk
from tkinter import messagebox

from database import load_films, load_salles, load_seances
from services import find_salle, load_salle_data, get_or_create_places, save_reservation_data, generate_ticket_code
from models import Personne
from .utils import clear_cache, DB_SEANCES, DB_RESERVATIONS
from .views import CinemaViews


class CinemaApp(CinemaViews):
    """Application principale de réservation de cinéma avec interface graphique."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Réservation Cinéma")
        self.root.attributes('-fullscreen', True)  # Fullscreen sans barre de titre
        self.root.configure(bg="#1a1a1a")
        
        # Configurer le nettoyage du cache à la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Données
        self.films = load_films("Database/Films.json")
        self.salles = load_salles("Database/Salles.json")
        self.seances = load_seances(DB_SEANCES)
        
        # Variables de session
        self.selected_film = None
        self.selected_seance = None
        self.selected_place = None
        self.places = None
        self.places_file_path = None
        self.salle = None
        self.salle_data = None
        self.redirect_timer = None  # Timer pour la redirection automatique
        
        # Conteneur principal
        self.main_frame = tk.Frame(root, bg="#1a1a1a")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Afficher la liste des films
        self.show_films()
    
    def clear_frame(self):
        """Efface le contenu du frame principal."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def select_film(self, film):
        """Sélectionne un film et affiche ses séances."""
        self.selected_film = film
        self.show_seances()
    
    def select_seance(self, seance):
        """Sélectionne une séance et prépare la sélection de place."""
        self.selected_seance = seance
        
        # Trouver la salle
        self.salle = find_salle(self.salles, seance)
        if not self.salle:
            messagebox.showerror("Erreur", "Salle introuvable pour cette séance.")
            return
        
        self.salle_data = load_salle_data(self.salle, "Database/Salles.json")
        if not self.salle_data:
            messagebox.showerror("Erreur", "Impossible de charger les informations de la salle.")
            return
        
        # Charger ou créer les places
        self.places, self.places_file_path = get_or_create_places(seance, self.salle_data)
        
        self.show_places()
    
    def select_place(self, place):
        """Sélectionne une place et passe à la saisie des informations."""
        self.selected_place = place
        self.show_user_info()
    
    def validate_email_realtime(self, event):
        """Valide l'email en temps réel et affiche les erreurs."""
        email = self.email_entry.get().strip()
        
        if not email:
            self.email_error.config(text="", fg="#ff6b6b")
            return
        
        # Vérifier format email
        if "@" not in email or "." not in email.split("@")[-1]:
            self.email_error.config(text="Format invalide: utilisez example@domaine.com", fg="#ff6b6b")
        else:
            self.email_error.config(text="✓ Valide", fg="#4CAF50")
    
    def process_payment(self):
        """Traite le paiement et finalise la réservation."""
        email = self.email_entry.get().strip()
        categorie = self.categorie_var.get()
        
        # Validation email
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            # Focus sur le champ et affiche l'erreur
            self.email_error.config(text="Format invalide: utilisez example@domaine.com", fg="#ff6b6b")
            self.email_entry.focus()
            return
        
        # Générer le code de réservation
        code = generate_ticket_code()
        
        # Créer l'objet personne
        personne = Personne(mail=email, categorie=categorie)
        
        # Sauvegarder la réservation et récupérer le chemin du QR code et du PDF
        qrcode_path, pdf_path = save_reservation_data(
            self.selected_seance,
            self.places_file_path,
            self.places,
            self.selected_place,
            code,
            self.selected_film,
            self.salle,
            personne,
            self.prix,
            DB_SEANCES,
            DB_RESERVATIONS
        )
        
        # Afficher le ticket
        self.show_ticket(code, personne, qrcode_path, pdf_path)
    
    def cancel_and_reset(self):
        """Annule le timer de redirection et réinitialise l'application."""
        # Annuler la redirection automatique si elle existe
        if self.redirect_timer:
            self.root.after_cancel(self.redirect_timer)
            self.redirect_timer = None
        # Réinitialiser l'application
        self.reset()
    
    def reset(self):
        """Réinitialise l'application pour une nouvelle réservation."""
        # Annuler le timer s'il existe encore
        if self.redirect_timer:
            self.root.after_cancel(self.redirect_timer)
            self.redirect_timer = None
            
        self.selected_film = None
        self.selected_seance = None
        self.selected_place = None
        self.places = None
        self.places_file_path = None
        self.salle = None
        self.salle_data = None
        
        # Recharger les données (pour avoir les places mises à jour)
        self.seances = load_seances(DB_SEANCES)
        
        self.show_films()
    
    def on_closing(self):
        """Gère la fermeture de l'application en vidant le cache."""
        # Vider le cache
        clear_cache()
        # Fermer la fenêtre
        self.root.destroy()
