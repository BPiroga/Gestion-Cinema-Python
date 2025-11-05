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
