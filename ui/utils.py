"""
Fonctions utilitaires pour l'interface graphique.
"""
import os
import shutil

# Chemins des fichiers
DB_FILMS = "Database/Films.json"
DB_SALLES = "Database/Salles.json"
DB_SEANCES = "Database/Seances.json"
DB_RESERVATIONS = "Database/cache/reservations.json"
COVERS_DIR = "media/images/covers"
CACHE_DIR = "Database/cache"


def clear_cache():
    #Vide le dossier cache à la fermeture de l'application.
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


def on_mousewheel(event, canvas):
    #Gère le scroll de la molette de la souris.
    # Windows and macOS use delta
    if hasattr(event, 'delta'):
        if event.delta > 0:
            canvas.yview_scroll(-1, "units")
        else:
            canvas.yview_scroll(1, "units")
    # Linux uses num
    else:
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")


def bind_mousewheel_recursive(widget, canvas):
    #Bind la molette de la souris à un widget et tous ses enfants.
    widget.bind("<MouseWheel>", lambda e: on_mousewheel(e, canvas), add=True)
    widget.bind("<Button-4>", lambda e: on_mousewheel(e, canvas), add=True)
    widget.bind("<Button-5>", lambda e: on_mousewheel(e, canvas), add=True)
    
    for child in widget.winfo_children():
        bind_mousewheel_recursive(child, canvas)
