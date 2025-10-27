#8. Application de gestion de cinéma
#Description : Système de réservation de places, avec gestion des séances.
#Objectifs : Interactions entre classes et exceptions personnalisées.
#Classes proposées : Film, Salle, Reservation.
#Exceptions à gérer : Salle pleine, film inexistant.
#Niveau : Avancé.

from enum import Enum #ça c'est pour pouvoir créer REGULAR et DISCOUNTED des variables fixes ?

class TariffCategory:
    REGULAR="Tarif normal"
    DISCOUNTED="Tarif réduit"

class Person:
    def __init__(self,email,category): #on pourraît éventuellement demander le nom \_O_/ si jamais on part du principe qu'ils peuvent le demandander à l'entrée (je ne sais pas) non
        self.email=email
        self.category=category

    def informationPerson(self):
            self.email=input("Entrez votre e-mail : ")
            age=int(input("Entrez votre âge : ")) #à rajouter une vérification pour redemander l'âge si une lettre est rentrée et mettre une condition âge inclu entre 0 et 130 (ar exemple)
            self.priceCategory(age)
            print(f"Catégorie tarifaire assignée : {self.category}")

    def priceCategory(self,age):
        if age<=26 or age>=60:
            self.category=TariffCategory.DISCOUNTED #tarif réduit
        else:
            self.category=TariffCategory.REGULAR #tarif normal

class ScreeningRoom: #salle
    def __init__(self,screenNumber,roomType,capacity):
        self.screenNumber=screenNumber
        self.roomType=roomType
        self.capacity=capacity
        self.availableSeats=capacity #places disponibles pour la fonction réservation que je n'ai pas encore faite
    
class Screening: #séance
    def __init__(self,day,time):
        self.day=day
        self.time=time

    def chooseScreening(self):
        moviesByGenre={ #liste des films par genre mais sans doute à modifier avec jason
            "D":["1","2"],
            "C":["1","2"],
            "S":["1","2"],
            "R":[],
            "AC":[],
            "AN":[],
            "H":[]
        }
        while True:
            choice=input("\nSi vous voulez choisir le film en fonction du jour ou du genre, choisissez : J (jour) / G (genre)").upper()
            if choice=="J":
             #   jour=input("Vous voulez choisir en fonction du jour, veuillez rentrer le jour jour/mois/année :") #je ne sais pas comment faire ça, faudrait décider si on a un programme de films par semaine ou par mois et comment on le laisse choisir, soit il rentre le jour et on affiche les disponibilités puis choisissez le film puis l'horaire soit on affiche direct toutes les propositions si jamais on a des jours quand le ciné est fermé
             #   if 
                print("à faire")
                break #à revoir
            elif choice=="G":
                print("\nVoici les genres disponibles :")
                print("Drame : genre qui met l’accent sur les émotions profondes et les conflits humains, souvent en explorant des situations graves ou sérieuses.")
                print("Comédie : genre dont l’objectif principal est de divertir le spectateur en suscitant le rire, par le biais de situations amusantes, exagérées ou inattendues.")
                print("Science-fiction : genre qui imagine des mondes futurs ou alternatifs, des technologies avancées et des événements qui dépassent les limites de la réalité contemporaine.")
                print("Romance : genre centré sur les relations amoureuses et les émotions liées à l’amour, souvent en explorant les liens et les sentiments des personnages.")
                print("Action : genre qui privilégie le rythme soutenu et les séquences spectaculaires, telles que les combats, les poursuites ou les aventures intenses.")
                print("Animation : genre utilisant des techniques de dessin ou d’images générées par ordinateur pour raconter des histoires, souvent avec une grande liberté imaginative.")
                print("Horreur : genre destiné à provoquer la peur, le suspense ou l’angoisse, en mettant en scène des situations effrayantes ou inquiétantes pour le spectateur.")
                genre=input("\nSélectionnez le genre : D(drame) / C(comédie) / S(science-fiction) / R(romance) / AC(action) / AN(animation) / H(horreur) :").upper()
                if genre in moviesByGenre:
                    print("\nVoici les films disponibles pour ce genre :")
                    for i, film in enumerate(moviesByGenre[genre],start=1):
                        print(f"{i}.{film}")
                    ChosenMovieNum=int(input("\nChoisissez le film (numéro) :"))-1
                    if 0<=ChosenMovieNum<len(moviesByGenre[genre]):
                        ChosenMovie=moviesByGenre[genre][ChosenMovieNum]
                        print(f"Film choisi : {ChosenMovie}")
                        print("\nChoisissez la séance :") #j'ai quand même l'impression que c'est un peu récursif, ou pas ?
                        break
                    else:
                        print("Veuillez changer le numéro du film, numéro choisi inéxistant")
                else:
                    print("Genre invalide, choisissez parmi les propositions.")
            else:
                print("Choix invalide, choisissez J(jour) ou G(genre).")



def price(category,roomType):
    regularPrices={
        "standard": 11,
        "3D": 14,
        "IMAX": 19}
    discountedPrices = {
        "standard": 7,
        "3D": 10,
        "IMAX": 15}
    if category==TariffCategory.REGULAR:
        return regularPrices[roomType]
    elif category==TariffCategory.DISCOUNTED:
        return discountedPrices[roomType]
    else:
        raise ValueError("Catégorie tarifaire inconnue")

room=[]
room.append(ScreeningRoom(0,"rien",0)) #pour ne pas se prendre la tête avec le fait que l'énumeration des listes commence à 0
room.append(ScreeningRoom(1,"standard",190))
room.append(ScreeningRoom(2,"standard",190))
room.append(ScreeningRoom(3,"standard",190))
room.append(ScreeningRoom(4,"3D",250))
room.append(ScreeningRoom(5,"3D",250))
room.append(ScreeningRoom(6,"IMAX",400))



personne=Person("", None)
personne.informationPerson()
choixSalle=6 #pour le test
seance = Screening(day="Lundi", time="20:00")  #jour et heure exemples
filmChoisi = seance.chooseScreening() #à développer
salleChoisie=room[choixSalle]
montant=price(personne.category, salleChoisie.roomType)

print("\n    Résumé    ")
print(f"E-mail : {personne.email}")
print(f"Salle choisie : {salleChoisie.roomType}")
print(f"Catégorie : {personne.category}")
print(f"Prix du billet : {montant} €")
#print(f"Séance : {seance}")
print(f"Film : {filmChoisi}")