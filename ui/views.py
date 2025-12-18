"""
Méthodes de vues pour l'interface graphique.
Contient toutes les fonctions d'affichage des différentes pages.
"""
import tkinter as tk
from tkinter import messagebox
import os
import sys

from database import load_seances
from services import find_salle, load_salle_data, get_or_create_places, save_reservation_data, generate_ticket_code
from models import Personne
from .utils import on_mousewheel, bind_mousewheel_recursive, DB_SEANCES, DB_RESERVATIONS
from .components import create_film_card


class CinemaViews:
    """Mixin contenant toutes les méthodes de vues."""
    
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
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="center")
        
        # Bind mouse wheel events for scrolling
        canvas.bind("<MouseWheel>", lambda e: on_mousewheel(e, canvas))
        canvas.bind("<Button-4>", lambda e: on_mousewheel(e, canvas))  # Linux scroll up
        canvas.bind("<Button-5>", lambda e: on_mousewheel(e, canvas))  # Linux scroll down
        scrollable_frame.bind("<MouseWheel>", lambda e: on_mousewheel(e, canvas))
        scrollable_frame.bind("<Button-4>", lambda e: on_mousewheel(e, canvas))
        scrollable_frame.bind("<Button-5>", lambda e: on_mousewheel(e, canvas))
        
        # Ajouter du padding à gauche
        scrollable_frame.columnconfigure(0, minsize=120)
        
        # Grille de films (5 colonnes)
        row, col = 0, 0
        for film in self.films:
            film_frame = create_film_card(scrollable_frame, film, self.select_film)
            film_frame.grid(row=row, column=col+1, padx=15, pady=15)
            
            col += 1
            if col >= 5:
                col = 0
                row += 1
        
        # Bind mousewheel to all child widgets after creation
        bind_mousewheel_recursive(scrollable_frame, canvas)
        
        canvas.pack(side="left", fill="both", expand=True)
    
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
            salle = find_salle(self.salles, seance)
            salle_type = salle.type if salle else "Standard"
            btn = tk.Button(
                seances_frame,
                text=f"{seance.jour} à {seance.horaire} - Salle {seance.salleNum} ({salle_type})",
                command=lambda s=seance: self.select_seance(s),
                bg="#2a2a2a",
                fg="white",
                font=("Arial", 12),
                width=50,
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
            text="═══════════════ ÉCRAN ═══════════════",
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
    
    def show_user_info(self):
        """Affiche le formulaire de saisie des informations utilisateur."""
        self.clear_frame()
        
        # Prix selon le type de salle sélectionné
        type_tarif = {"Standard": 10.0, "3D": 12.0, "Imax": 15.0}
        prix_base = type_tarif.get(self.salle.type, 10.0)
        
        # Réductions par catégorie
        reductions = {"adulte": 0.0, "etudiant": 0.2, "enfant": 0.5}
        
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
                 f"Salle: {self.salle.type}",
            font=("Arial", 12),
            bg="#2a2a2a",
            fg="white",
            justify=tk.LEFT,
            padx=20,
            pady=15
        )
        recap.pack(pady=20)
        
        # Label de prix dynamique
        self.prix_label = tk.Label(
            self.main_frame,
            text=f"Prix: {prix_base:.2f} €",
            font=("Arial", 14, "bold"),
            bg="#1a1a1a",
            fg="#4CAF50"
        )
        self.prix_label.pack(pady=10)
        
        # Formulaire
        form_frame = tk.Frame(self.main_frame, bg="#1a1a1a")
        form_frame.pack(pady=20)
        
        # Email
        tk.Label(form_frame, text="E-mail:", font=("Arial", 12), bg="#1a1a1a", fg="white").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.email_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.email_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Label d'erreur email
        self.email_error = tk.Label(form_frame, text="", font=("Arial", 10), bg="#1a1a1a", fg="#ff6b6b")
        self.email_error.grid(row=1, column=1, sticky=tk.W, padx=10)
        
        # Bind event pour valider l'email en temps réel
        self.email_entry.bind("<KeyRelease>", self.validate_email_realtime)
        
        # Catégorie
        tk.Label(form_frame, text="Catégorie:", font=("Arial", 12), bg="#1a1a1a", fg="white").grid(row=2, column=0, sticky=tk.W, pady=10)
        
        self.categorie_var = tk.StringVar(value="adulte")
        categorie_frame = tk.Frame(form_frame, bg="#1a1a1a")
        categorie_frame.grid(row=2, column=1, sticky=tk.W)
        
        def update_price(*args):
            """Met à jour le prix en fonction de la catégorie sélectionnée."""
            categorie = self.categorie_var.get()
            reduction = reductions.get(categorie, 0.0)
            prix_final = prix_base * (1 - reduction)
            self.prix = prix_final
            self.prix_label.config(text=f"Prix: {prix_final:.2f} €")
        
        tk.Radiobutton(
            categorie_frame, 
            text="Adulte", 
            variable=self.categorie_var, 
            value="adulte",
            bg="#1a1a1a",
            fg="white",
            selectcolor="#2a2a2a",
            font=("Arial", 11),
            command=update_price
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            categorie_frame, 
            text="Étudiant (-20%)", 
            variable=self.categorie_var, 
            value="etudiant",
            bg="#1a1a1a",
            fg="white",
            selectcolor="#2a2a2a",
            font=("Arial", 11),
            command=update_price
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            categorie_frame, 
            text="Enfant (-50%)", 
            variable=self.categorie_var, 
            value="enfant",
            bg="#1a1a1a",
            fg="white",
            selectcolor="#2a2a2a",
            font=("Arial", 11),
            command=update_price
        ).pack(side=tk.LEFT, padx=5)
        
        # Initialiser le prix
        self.prix = prix_base
        
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
    
    def show_ticket(self, code, personne, qrcode_path, pdf_path):
        """Affiche le ticket de réservation."""
        self.clear_frame()
        
        # Ouvrir automatiquement le PDF (il est déjà vérifié dans services.py)
        if pdf_path and os.path.exists(pdf_path):
            try:
                # Convertir en chemin absolu
                abs_pdf_path = os.path.abspath(pdf_path)
                
                if sys.platform == 'win32':
                    os.startfile(abs_pdf_path)
                elif sys.platform == 'darwin':  # macOS
                    os.system(f'open "{abs_pdf_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{abs_pdf_path}"')
            except Exception as e:
                print(f"Erreur lors de l'ouverture du PDF: {e}")
        
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
        
        Votre e-billet PDF a été ouvert automatiquement.
        Présentez-le à l'entrée pour accéder à la salle.
        Bon film !
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
        
        # Message de redirection
        redirect_msg = tk.Label(
            self.main_frame,
            text="Redirection automatique vers l'accueil dans 10 secondes...",
            font=("Arial", 10),
            bg="#1a1a1a",
            fg="#aaa"
        )
        redirect_msg.pack(pady=10)
        
        # Redirection automatique après 10 secondes
        self.redirect_timer = self.root.after(10000, self.reset)
        
        # Bouton nouvelle réservation (pour redirection immédiate)
        tk.Button(
            self.main_frame,
            text="Nouvelle réservation",
            command=self.cancel_and_reset,
            bg="#d32f2f",
            fg="white",
            font=("Arial", 14, "bold"),
            width=25,
            height=2
        ).pack(pady=20)
