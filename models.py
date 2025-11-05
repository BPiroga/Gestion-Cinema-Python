from __future__ import annotations
from dataclasses import dataclass, field
import json


@dataclass
class Personne:
    id: int = None
    mail: str = None
    categorie: str = None

    @staticmethod
    def from_dict(d):
        if d is None:
            return None
        return Personne(
            id=d.get("id"),
            mail=d.get("mail"),
            categorie=d.get("categorie"),
        )

    def to_dict(self):
        return {"id": self.id, "mail": self.mail, "categorie": self.categorie}


@dataclass
class Place:
    column: int = None
    row: int = None
    estOccupee: bool = False
    personne: object = None

    @staticmethod
    def from_dict(d):
        return Place(
            column=d.get("column"),
            row=d.get("row"),
            estOccupee=bool(d.get("estOccupee", False)),
            personne=Personne.from_dict(d.get("personne")) if d.get("personne") is not None else None,
        )

    def to_dict(self):
        return {
            "column": self.column,
            "row": self.row,
            "estOccupee": self.estOccupee,
            "personne": self.personne.to_dict() if self.personne is not None else None,
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
        return out


# Helper loaders
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


# Reservation / persistence helpers
def find_first_free_place(salle):
    """Retourne la première Place libre (objet Place) ou None."""
    for p in salle.places:
        if not getattr(p, "estOccupee", False):
            return p
    return None


def reserver_first_free_place(salle, personne):
    """Réserve la première place libre dans la salle pour la personne passée.
    Retourne la place réservée ou None si aucune place libre.
    """
    place = find_first_free_place(salle)
    if place is None:
        return None
    place.estOccupee = True
    place.personne = personne
    return place


def save_salles(path, salles):
    """Sauvegarde la liste de salles dans le fichier JSON (remplace le contenu)."""
    data = [s.to_dict() for s in salles]
    with open(str(path), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_ticket_code():
    import uuid
    return str(uuid.uuid4())
