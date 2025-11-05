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
