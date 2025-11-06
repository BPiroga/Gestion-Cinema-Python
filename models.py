from dataclasses import dataclass, field
import json


@dataclass
class Personne:
    mail: str = None
    categorie: str = None

    @staticmethod
    def from_dict(d):
        if d is None:
            return None
        return Personne(
            mail=d.get("mail"),
            categorie=d.get("categorie"),
        )

    def to_dict(self):
        return {"mail": self.mail, "categorie": self.categorie}


@dataclass
class Place:
    column: int = None
    row: int = None
    estOccupee: bool = False
    codeReservation: str = None

    @staticmethod
    def from_dict(d):
        return Place(
            column=d.get("column"),
            row=d.get("row"),
            estOccupee=bool(d.get("estOccupee", False)),
            codeReservation=d.get("codeReservation"),
        )

    def to_dict(self):
        return {
            "column": self.column,
            "row": self.row,
            "estOccupee": self.estOccupee,
            "codeReservation": self.codeReservation,
        }


@dataclass
class Salle:
    numSalle: int = None
    nbPlaces: int = None
    type: str = None
    places: list = field(default_factory=list)

    @staticmethod
    def from_dict(d):
        places = [Place.from_dict(p) for p in d.get("places", [])]
        return Salle(
            numSalle=d.get("numSalle"),
            nbPlaces=d.get("nbPlaces"),
            type=d.get("type"),
            places=places,
        )

    def to_dict(self):
        return {
            "numSalle": self.numSalle,
            "nbPlaces": self.nbPlaces,
            "type": self.type,
            "places": [p.to_dict() for p in self.places],
        }


@dataclass
class Film:
    id: int = None
    nom: str = None
    realisateur: str = None
    duree: int = None
    genre: str = None
    cover: str = None

    @staticmethod
    def from_dict(d):
        if d is None:
            return None
        return Film(
            id=d.get("id"),
            nom=d.get("nom"),
            realisateur=d.get("realisateur"),
            duree=d.get("duree"),
            genre=d.get("genre"),
            cover=d.get("cover"),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "realisateur": self.realisateur,
            "duree": self.duree,
            "genre": self.genre,
            "cover": self.cover,
        }


@dataclass
class Seance:
    id: int = None
    jour: str = None
    horaire: str = None
    filmId: int = None
    salleNum: int = None
    placesFile: str = None
    film = None
    salle = None

    @staticmethod
    def from_dict(d):
        if d is None:
            return None
        return Seance(
            id=d.get("id"),
            jour=d.get("jour"),
            horaire=d.get("horaire"),
            filmId=d.get("filmId"),
            salleNum=d.get("salleNum"),
            placesFile=d.get("placesFile"),
        )

    def to_dict(self):
        out = {
            "id": self.id,
            "jour": self.jour,
            "horaire": self.horaire,
        }
        if self.filmId is not None:
            out["filmId"] = self.filmId
        if self.salleNum is not None:
            out["salleNum"] = self.salleNum
        if self.placesFile is not None:
            out["placesFile"] = self.placesFile
        return out




# Helper loaders


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    """Sauvegarde des données JSON dans un fichier."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_personnes(path):
    data = load_json(str(path))
    return [Personne.from_dict(d) for d in data]


def load_films(path):
    data = load_json(str(path))
    return [Film.from_dict(d) for d in data]


def load_salles(path):
    data = load_json(str(path))
    return [Salle.from_dict(d) for d in data]


def load_seances(path):
    data = load_json(str(path))
    return [Seance.from_dict(d) for d in data]


def save_seances(path, seances):
    """Sauvegarde la liste des séances dans le fichier JSON."""
    data = [s.to_dict() for s in seances]
    save_json(path, data)


def load_places(path):
    """Charge le fichier des places pour une séance."""
    if path is None:
        return None
    try:
        data = load_json(path)
        return [Place.from_dict(p) for p in data]
    except FileNotFoundError:
        return None


def save_places(path, places):
    """Sauvegarde les places dans un fichier JSON."""
    data = [p.to_dict() for p in places]
    save_json(path, data)


def create_places_for_seance(seance, salle_data):
	"""Crée une grille de places vide pour une séance basée sur la salle.
	salle_data est un dict contenant row et column."""
	rows = salle_data.get("row", 10)  # valeur par défaut 10
	cols = salle_data.get("column", 10)
	places = []
	for r in range(1, rows + 1):
		for c in range(1, cols + 1):
			places.append(Place(row=r, column=c, estOccupee=False, codeReservation=None))
	return places

def save_reservation(path, reservation):
    """Ajoute une nouvelle réservation au fichier JSON. Crée le fichier s'il n'existe pas."""
    import os
    
    # Créer le dossier parent si nécessaire
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Charger les réservations existantes ou créer une liste vide
    try:
        reservations = load_json(path)
    except FileNotFoundError:
        reservations = []
    
    reservations.append(reservation)
    save_json(path, reservations)


def generate_ticket_code():
    import uuid
    return str(uuid.uuid4())
