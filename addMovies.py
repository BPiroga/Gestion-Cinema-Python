import json2object 
movies = json2object.jsonToObject('Films')
class movie :
    def __init__(self,nom="",realisateur="",duree=0,genre="",cover=""):
        self.nom = nom
        self.realisateur  = realisateur
        self.duree = duree
        self.genre = genre
        self.cover = cover
    def newMovie(self) :   
        print('\n')
        self.nom = input('Nom du film: ')
        self.realisateur  = input('Realisateur: ')
        self.duree = int(input('duree en min: '))
        self.genre = input('genre: ')
        self.cover ="./media/images/covers/"+input('nom_de_la_cover.jpg: ')
        return self
    def __str__(self):
        return f"film : {self.nom}, Réalisateur : {self.realisateur}, Durée: {self.duree}min , Genre: {self.genre}"

new = movie()
new = new.newMovie()
movies.append(new)
json2object.objectToJson(movies,'Films')