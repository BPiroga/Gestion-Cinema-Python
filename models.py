"""
Module de définition des modèles de données (dataclasses).
Contient uniquement les classes et leurs méthodes de sérialisation.
"""
from dataclasses import dataclass, field


@dataclass
class Personne:
    mail: str = None
    categorie: str = None

    def to_dict(self):
        return {"mail": self.mail, "categorie": self.categorie}

    @staticmethod
    def from_dict(d):
        if d is None:
            return None
        return Personne(mail=d.get("mail"), categorie=d.get("categorie"))

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


# Note: Les fonctions load/save ont été déplacées vers database.py
# Les fonctions métier ont été déplacées vers services.py

