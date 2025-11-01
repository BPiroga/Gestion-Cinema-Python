#8. Application de gestion de cinéma
#Description : Système de réservation de places, avec gestion des séances.
#Objectifs : Interactions entre classes et exceptions personnalisées.
#Classes proposées : Film, Salle, Reservation.
#Exceptions à gérer : Salle pleine, film inexistant.
#Niveau : Avancé.

import json2object
from enum import Enum #ça c'est pour pouvoir créer REGULAR et DISCOUNTED des variables globales

def price(category,roomType):
    regularPrices={"standard": 11,"3D": 14,"IMAX": 19}
    discountedPrices = {"standard": 7,"3D": 10,"IMAX": 15}
    if category==TariffCategory.REGULAR:
        return regularPrices[roomType]
    elif category==TariffCategory.DISCOUNTED:
        return discountedPrices[roomType]
    else:
        raise ValueError("Catégorie tarifaire inconnue")

def downloadFilms():
    #charge les films depuis films.json et les convertit en objets film
    raw_movies=json2object.jsonToObject("Films")
    films=[]
    for movie in raw_movies:
        films.append(
            Film(
                movie.nom,
                movie.realisateur,
                movie.duree,
                movie.genre,
                movie.seances
            )
        )
    return films

room=[]
#room.append(ScreeningRoom(0,"rien",0)) #pour ne pas se prendre la tête avec le fait que l'énumeration des listes commence à 0
room.append(ScreeningRoom(1,"standard",190))
room.append(ScreeningRoom(2,"standard",190))
room.append(ScreeningRoom(3,"standard",190))
room.append(ScreeningRoom(4,"3D",250))
room.append(ScreeningRoom(5,"3D",250))
room.append(ScreeningRoom(6,"IMAX",400))

if __name__ == "__main__":
    interface()



#d'abbord on affiche tous les films du jour puis les seances horaire et type de salle puis on a les infos personne avec l'age 
 
#séparer les fichiers classes et le fichier interface     trouver la meilleure interface      afficher les places disponibles sur le terminal