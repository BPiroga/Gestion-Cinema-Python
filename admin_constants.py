"""
Constantes partagées pour le module d'administration.
"""

# Chemins de la base de données
DB_FILMS = "Database/Films.json"
DB_SALLES = "Database/Salles.json"
DB_SEANCES = "Database/Seances.json"
COVERS_DIR = "media/images/covers"

# Gestion horaire
JOURNEE_START_MIN = 9 * 60    # 09:00 (540 minutes)
JOURNEE_END_MIN = 24 * 60     # 24:00 / 00:00 (1440 minutes)
MAX_HORAIRE_HEURE = 23        # 23:59 max
MAX_HORAIRE_MIN = 59
SLOT_DURATION = 30            # Durée des créneaux (minutes)
START_HOUR = 9
END_HOUR = 24
