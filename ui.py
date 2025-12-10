"""
Interface graphique (GUI) avec Tkinter pour le système de réservation de cinéma.
Affiche les films avec leurs covers, permet de sélectionner une séance, 
choisir une place, saisir les informations et finaliser la réservation.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import shutil

from database import load_films, load_salles, load_seances
from services import (
    find_salle,
    load_salle_data,
    get_or_create_places,
    save_reservation_data,
    generate_ticket_code
)
from models import Personne

# Chemins des fichiers
DB_FILMS = "Database/Films.json"
DB_SALLES = "Database/Salles.json"
DB_SEANCES = "Database/Seances.json"
DB_RESERVATIONS = "Database/cache/reservations.json"
COVERS_DIR = "media/images/covers"
CACHE_DIR = "Database/cache"


def clear_cache():
    """Vide le dossier cache à la fermeture de l'application."""
    if os.path.exists(CACHE_DIR):
        # Supprimer tous les fichiers dans le cache
        for filename in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Erreur lors de la suppression de {file_path}: {e}")


class CinemaApp:
    """Application principale de réservation de cinéma avec interface graphique."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Réservation Cinéma")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1a1a1a")
        
        # Configurer le nettoyage du cache à la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Données
        self.films = load_films(DB_FILMS)
        self.salles = load_salles(DB_SALLES)
        self.seances = load_seances(DB_SEANCES)
        
        # Variables de session
        self.selected_film = None
        self.selected_seance = None
        self.selected_place = None
        self.places = None
        self.places_file_path = None
        self.salle = None
        self.salle_data = None
        
        # Conteneur principal
        self.main_frame = tk.Frame(root, bg="#1a1a1a")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Afficher la liste des films
        self.show_films()
    
    def clear_frame(self):
        """Efface le contenu du frame principal."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_films(self):
        """Affiche la grille de films avec leurs covers."""
        self.clear_frame()
        
        # Titre
        title = tk.Label(
            self.main_frame, 
            text="Choisissez votre film", 
            font=("Arial", 24, "bold"),
            bg="#1a1a1a",
            fg="white"
        )
        title.pack(pady=20)
        
        # Frame scrollable pour les films
        canvas = tk.Canvas(self.main_frame, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grille de films (3 colonnes)
        row, col = 0, 0
        for film in self.films:
            film_frame = self.create_film_card(scrollable_frame, film)
            film_frame.grid(row=row, column=col, padx=15, pady=15)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_film_card(self, parent, film):
        """Crée une carte de film avec cover et titre."""
        card = tk.Frame(parent, bg="#2a2a2a", relief=tk.RAISED, borderwidth=2)
        
        # Charger le cover (gérer les chemins relatifs avec ./)
        if film.cover:
            # Enlever le ./ au début si présent
            cover_file = film.cover.replace("./", "").replace("\\", "/")
            cover_path = cover_file
        else:
            cover_path = None
            
        if cover_path and os.path.exists(cover_path):
            try:
                img = Image.open(cover_path)
                img = img.resize((200, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                cover_label = tk.Label(card, image=photo, bg="#2a2a2a")
                cover_label.image = photo  # Garder une référence
                cover_label.pack(pady=5)
            except Exception as e:
                # Si erreur de chargement, afficher un placeholder
                placeholder = tk.Label(
                    card, 
                    text="Pas d'image", 
                    width=25, 
                    height=15,
                    bg="#3a3a3a",
                    fg="white"
                )
                placeholder.pack(pady=5)
        else:
            placeholder = tk.Label(
                card, 
                text="Pas d'image", 
                width=25, 
                height=15,
                bg="#3a3a3a",
                fg="white"
            )
            placeholder.pack(pady=5)
        
        # Titre du film
        title = tk.Label(
            card, 
            text=film.nom, 
            font=("Arial", 12, "bold"),
            bg="#2a2a2a",
            fg="white",
            wraplength=200
        )
        title.pack(pady=5)
        
        # Bouton de sélection
        btn = tk.Button(
            card,
            text="Voir les séances",
            command=lambda: self.select_film(film),
            bg="#d32f2f",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        btn.pack(pady=10)
        
        return card
    
    def select_film(self, film):
        """Sélectionne un film et affiche ses séances."""
        self.selected_film = film
        self.show_seances()
    
    def show_seances(self):
        """Affiche les séances disponibles pour le film sélectionné."""
        self.clear_frame()
        
        # Titre
        title = tk.Label(
            self.main_frame,
            text=f"Séances pour : {self.selected_film.nom}",
            font=("Arial", 20, "bold"),
            bg="#1a1a1a",
            fg="white"
        )
        title.pack(pady=20)
        
        # Filtrer les séances pour ce film
        film_seances = [
            s for s in self.seances
            if s.filmId == self.selected_film.id
            and s.salleNum is not None
        ]
        
        if not film_seances:
            tk.Label(
                self.main_frame,
                text="Aucune séance disponible pour ce film.",
                font=("Arial", 14),
                bg="#1a1a1a",
                fg="white"
            ).pack(pady=20)
            
            tk.Button(
                self.main_frame,
                text="← Retour aux films",
                command=self.show_films,
                bg="#555",
                fg="white",
                font=("Arial", 12)
            ).pack(pady=10)
            return
        
        # Liste des séances
        seances_frame = tk.Frame(self.main_frame, bg="#1a1a1a")
        seances_frame.pack(pady=20)
        
        for seance in film_seances:
            btn = tk.Button(
                seances_frame,
                text=f"{seance.jour} à {seance.horaire} - Salle {seance.salleNum}",
                command=lambda s=seance: self.select_seance(s),
                bg="#2a2a2a",
                fg="white",
                font=("Arial", 12),
                width=40,
                height=2,
                cursor="hand2"
            )
            btn.pack(pady=5)
        
        # Bouton retour
        tk.Button(
            self.main_frame,
            text="← Retour aux films",
            command=self.show_films,
            bg="#555",
            fg="white",
            font=("Arial", 12)
        ).pack(pady=20)
    
    def select_seance(self, seance):
        """Sélectionne une séance et prépare la sélection de place."""
        self.selected_seance = seance
        
        # Trouver la salle
        self.salle = find_salle(self.salles, seance)
        if not self.salle:
            messagebox.showerror("Erreur", "Salle introuvable pour cette séance.")
            return
        
        self.salle_data = load_salle_data(self.salle, DB_SALLES)
        if not self.salle_data:
            messagebox.showerror("Erreur", "Impossible de charger les informations de la salle.")
            return
        
        # Charger ou créer les places
        self.places, self.places_file_path = get_or_create_places(seance, self.salle_data)
        
        self.show_places()
    
    def show_places(self):
        """Affiche la grille des places disponibles."""
        self.clear_frame()
        
        rows = self.salle_data.get("row", 10)
        cols = self.salle_data.get("column", 10)
        
        # Titre
        title = tk.Label(
            self.main_frame,
            text=f"Choisissez votre place - {self.selected_film.nom}",
            font=("Arial", 18, "bold"),
            bg="#1a1a1a",
            fg="white"
        )
        title.pack(pady=10)
        
        info = tk.Label(
            self.main_frame,
            text=f"Séance: {self.selected_seance.jour} {self.selected_seance.horaire} - Salle {self.salle.numSalle}",
            font=("Arial", 12),
            bg="#1a1a1a",
            fg="#aaa"
        )
        info.pack()
        
        # Écran
        ecran = tk.Label(
            self.main_frame,
            text="═══════════ ÉCRAN ═══════════",
            font=("Arial", 14, "bold"),
            bg="#1a1a1a",
            fg="#666"
        )
        ecran.pack(pady=20)
        
        # Grille de places
        places_frame = tk.Frame(self.main_frame, bg="#1a1a1a")
        places_frame.pack()
        
        for r in range(1, rows + 1):
            row_frame = tk.Frame(places_frame, bg="#1a1a1a")
            row_frame.pack()
            
            # Numéro de rangée
            tk.Label(
                row_frame,
                text=f"R{r}",
                font=("Arial", 10),
                bg="#1a1a1a",
                fg="white",
                width=3
            ).pack(side=tk.LEFT)
            
            for c in range(1, cols + 1):
                place = next((p for p in self.places if p.row == r and p.column == c), None)
                
                if place and place.estOccupee:
                    # Place occupée
                    btn = tk.Button(
                        row_frame,
                        text="X",
                        width=3,
                        height=1,
                        bg="#d32f2f",
                        fg="white",
                        state=tk.DISABLED
                    )
                else:
                    # Place disponible
                    btn = tk.Button(
                        row_frame,
                        text="○",
                        width=3,
                        height=1,
                        bg="#4CAF50",
                        fg="white",
                        cursor="hand2",
                        command=lambda p=place: self.select_place(p)
                    )
                
                btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Légende
        legend_frame = tk.Frame(self.main_frame, bg="#1a1a1a")
        legend_frame.pack(pady=20)
        
        tk.Label(legend_frame, text="○ Disponible", bg="#4CAF50", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        tk.Label(legend_frame, text="X Occupée", bg="#d32f2f", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        
        # Bouton retour
        tk.Button(
            self.main_frame,
            text="← Retour aux séances",
            command=self.show_seances,
            bg="#555",
            fg="white",
            font=("Arial", 12)
        ).pack(pady=10)
    
    def select_place(self, place):
        """Sélectionne une place et passe à la saisie des informations."""
        self.selected_place = place
        self.show_user_info()
    
    def show_user_info(self):
        """Affiche le formulaire de saisie des informations utilisateur."""
        self.clear_frame()
        
        # Prix selon le type de salle
        type_tarif = {"Standard": 10.0, "3D": 12.0, "Imax": 15.0}
        self.prix = type_tarif.get(self.salle.type, 10.0)
        
        # Titre
        title = tk.Label(
            self.main_frame,
            text="Vos informations",
            font=("Arial", 20, "bold"),
            bg="#1a1a1a",
            fg="white"
        )
        title.pack(pady=20)
        
        # Récapitulatif
        recap = tk.Label(
            self.main_frame,
            text=f"Film: {self.selected_film.nom}\n"
                 f"Séance: {self.selected_seance.jour} {self.selected_seance.horaire}\n"
                 f"Place: Rangée {self.selected_place.row}, Colonne {self.selected_place.column}\n"
                 f"Prix: {self.prix:.2f} € (salle {self.salle.type})",
            font=("Arial", 12),
            bg="#2a2a2a",
            fg="white",
            justify=tk.LEFT,
            padx=20,
            pady=15
        )
        recap.pack(pady=20)
        
        # Formulaire
        form_frame = tk.Frame(self.main_frame, bg="#1a1a1a")
        form_frame.pack(pady=20)
        
        # Email
        tk.Label(form_frame, text="E-mail:", font=("Arial", 12), bg="#1a1a1a", fg="white").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.email_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.email_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Catégorie
        tk.Label(form_frame, text="Catégorie:", font=("Arial", 12), bg="#1a1a1a", fg="white").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        self.categorie_var = tk.StringVar(value="adulte")
        categorie_frame = tk.Frame(form_frame, bg="#1a1a1a")
        categorie_frame.grid(row=1, column=1, sticky=tk.W)
        
        tk.Radiobutton(
            categorie_frame, 
            text="Adulte", 
            variable=self.categorie_var, 
            value="adulte",
            bg="#1a1a1a",
            fg="white",
            selectcolor="#2a2a2a",
            font=("Arial", 11)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            categorie_frame, 
            text="Étudiant", 
            variable=self.categorie_var, 
            value="etudiant",
            bg="#1a1a1a",
            fg="white",
            selectcolor="#2a2a2a",
            font=("Arial", 11)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            categorie_frame, 
            text="Enfant", 
            variable=self.categorie_var, 
            value="enfant",
            bg="#1a1a1a",
            fg="white",
            selectcolor="#2a2a2a",
            font=("Arial", 11)
        ).pack(side=tk.LEFT, padx=5)
        
        # Boutons
        buttons_frame = tk.Frame(self.main_frame, bg="#1a1a1a")
        buttons_frame.pack(pady=30)
        
        tk.Button(
            buttons_frame,
            text="← Retour",
            command=self.show_places,
            bg="#555",
            fg="white",
            font=("Arial", 12),
            width=15
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            buttons_frame,
            text="Payer et Réserver",
            command=self.process_payment,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20
        ).pack(side=tk.LEFT, padx=10)
    
    def process_payment(self):
        """Traite le paiement et finalise la réservation."""
        email = self.email_entry.get().strip()
        categorie = self.categorie_var.get()
        
        # Validation email simple
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showerror("Erreur", "Veuillez entrer un e-mail valide.")
            return
        
        # Générer le code de réservation
        code = generate_ticket_code()
        
        # Créer l'objet personne
        personne = Personne(mail=email, categorie=categorie)
        
        # Sauvegarder la réservation
        save_reservation_data(
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
        self.show_ticket(code, personne)
    
    def show_ticket(self, code, personne):
        """Affiche le ticket de réservation."""
        self.clear_frame()
        
        # Titre
        title = tk.Label(
            self.main_frame,
            text="✓ Réservation confirmée !",
            font=("Arial", 24, "bold"),
            bg="#1a1a1a",
            fg="#4CAF50"
        )
        title.pack(pady=30)
        
        # Ticket
        ticket_frame = tk.Frame(self.main_frame, bg="#2a2a2a", relief=tk.RAISED, borderwidth=3)
        ticket_frame.pack(pady=20, padx=50)
        
        ticket_content = f"""
        VOTRE TICKET DE RÉSERVATION
        
        CODE: {code}
        
        Film: {self.selected_film.nom}
        Séance: {self.selected_seance.jour} {self.selected_seance.horaire}
        Salle: {self.salle.numSalle} ({self.salle.type})
        Place: Rangée {self.selected_place.row}, Colonne {self.selected_place.column}
        
        Catégorie: {personne.categorie}
        Prix: {self.prix:.2f} €
        
        Présentez ce code à l'entrée pour scanner
        et accéder à la salle. Bon film !
        """
        
        tk.Label(
            ticket_frame,
            text=ticket_content,
            font=("Courier", 12),
            bg="#2a2a2a",
            fg="white",
            justify=tk.LEFT,
            padx=30,
            pady=30
        ).pack()
        
        # Bouton nouvelle réservation
        tk.Button(
            self.main_frame,
            text="Nouvelle réservation",
            command=self.reset,
            bg="#d32f2f",
            fg="white",
            font=("Arial", 14, "bold"),
            width=25,
            height=2
        ).pack(pady=30)
    
    def reset(self):
        """Réinitialise l'application pour une nouvelle réservation."""
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


def main():
    """Lance l'application de réservation de cinéma."""
    root = tk.Tk()
    app = CinemaApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
