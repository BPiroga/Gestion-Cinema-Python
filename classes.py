class TariffCategory:
    REGULAR="Tarif normal"
    DISCOUNTED="Tarif réduit"

class Person:
    def __init__(self,email,category):
        self.email=email
        self.category=category

    def informationPerson(self):
            self.email=input("Entrez votre e-mail : ")
            while True:
                try:
                    age = int(input("Entrez votre âge : "))
                    if 0<age<130:
                        break
                    else:
                        print("Âge invalide, entrez un âge plausible : ")
                except ValueError:
                    print("ERREUR : entrez un nombre valide (0 < votre âge < 130) : ")
            self.priceCategory(age)
            print(f"Catégorie tarifaire assignée : {self.category}")

    def priceCategory(self,age):
        if age<=26 or age>=60:
            self.category=TariffCategory.DISCOUNTED #tarif réduit
        else:
            self.category=TariffCategory.REGULAR #tarif normal

class ScreeningRoom:
    def __init__(self, number, roomType, capacity):
        self.number = number
        self.roomType = roomType
        self.capacity = capacity
        self.availableSeats = capacity

class Film:
    def __init__(self,nom,realisateur,duree,genre,seances):
        self.nom=nom
        self.realisateur=realisateur
        self.duree=duree
        self.genre=genre
        self.seances=seances
    
    def displayScreenings(self):
        print(f"\n {self.nom} ({self.genre}) - Réalisé par {self.realisateur}")
        print(f"Durée : {self.duree} minutes")
        for i, (time,roomType) in enumerate(self.seances,start=1):
            print(f"  {i}. {time} - Salle {roomType}")

    def chooseScreening(self):
        self.displayScreenings()
        while True:
            try:
                choice=int(input("\nChoisissez la séance (numéro) : ")) - 1
                if 0<=choice<len(self.seances):
                    return self.seances[choice]
                else:
                    print("Numéro invalide.")
            except ValueError:
                print("Erreur : entrez un nombre correspondant à une séance valide.")