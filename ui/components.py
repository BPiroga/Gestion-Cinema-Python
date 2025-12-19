"""
Composants réutilisables de l'interface graphique.
"""
import tkinter as tk
from PIL import Image, ImageTk
import os


def create_film_card(parent, film, on_select_callback):
    """Crée une carte de film avec cover et titre.
    
    Args:
        parent: Widget parent
        film: Objet Film
        on_select_callback: Fonction callback appelée lors de la sélection
    
    Returns:
        Frame de la carte du film
    """
    card = tk.Frame(parent, bg="#2a2a2a", relief=tk.RAISED, borderwidth=2, width=230, height=480)
    card.pack_propagate(False)  # Empêcher le frame de se redimensionner
    
    # Frame interne pour le contenu (cover, titre, info)
    content_frame = tk.Frame(card, bg="#2a2a2a")
    content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)
    
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
            
            cover_label = tk.Label(content_frame, image=photo, bg="#2a2a2a")
            cover_label.image = photo  # Garder une référence
            cover_label.pack(pady=5)
        except Exception as e:
            # Si erreur de chargement, afficher un placeholder
            placeholder = tk.Label(
                content_frame, 
                text="Pas d'image", 
                width=25, 
                height=15,
                bg="#3a3a3a",
                fg="white"
            )
            placeholder.pack(pady=5)
    else:
        placeholder = tk.Label(
            content_frame, 
            text="Pas d'image", 
            width=25, 
            height=15,
            bg="#3a3a3a",
            fg="white"
        )
        placeholder.pack(pady=5)
    
    # Titre du film
    title = tk.Label(
        content_frame, 
        text=film.nom, 
        font=("Arial", 12, "bold"),
        bg="#2a2a2a",
        fg="white",
        wraplength=200,
        justify=tk.CENTER
    )
    title.pack(pady=2, padx=5, fill=tk.X)

    # Informations du film (réalisateur, genre, durée)
    heures = film.duree // 60
    minutes = film.duree % 60
    duree_formatee = f"{heures}h {minutes}min" if heures > 0 else f"{minutes}min"
    info_text = f"{film.realisateur}\n{film.genre}\n{duree_formatee}"
    info = tk.Label( 
        content_frame,
        text=info_text,
        font=("Arial", 9),
        bg="#2a2a2a",
        fg="#aaa",
        wraplength=200,
        justify=tk.CENTER
    )
    info.pack(pady=2, padx=5, fill=tk.X)
    
    # Bouton de sélection - fixé en bas de la carte
    btn = tk.Button(
        card,
        text="Voir les séances",
        command=lambda: on_select_callback(film),
        bg="#d32f2f",
        fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2"
    )
    btn.pack(side=tk.BOTTOM, pady=5, padx=5, fill=tk.X)
    
    return card


def validate_email(email):
    """Valide le format d'un email.
    
    Args:
        email: String email à valider
    
    Returns:
        tuple (bool, str): (est_valide, message_erreur)
    """
    if not email:
        return False, "L'email est requis"
    
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Format invalide: utilisez example@domaine.com"
    
    return True, "✓ Valide"
