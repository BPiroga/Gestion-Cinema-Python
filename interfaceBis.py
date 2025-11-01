def interface():
    answer = "N"
    while answer.lower() != "y":
        print("\n" * 100)
        answer = input("Réserver une séance ? Y/N \n")
    print("\n" * 100)
    films = downloadFilms()
    while True:
        print("=====Films du jour=====\n")
        for i, movie in enumerate(films,start=1):
            print(f"{i}) [{movie.nom}] - {movie.realisateur}")
        choice = 0
        while choice < 1 or choice > len(films):
            try:
                choice = int(input("\nChoisissez un film (numéro) : "))
            except:
                choice = 0

        movie = films[choice - 1]
        print("\n" * 100)
        print(f"{movie.nom}\n{movie.realisateur}\n{movie.duree} min\n{movie.genre}")
        confirm = input("Réserver ? Y/N \n")

        if confirm.lower() == "y":
            print("\n" * 100)
            time, roomType = movie.chooseScreening()
            break
        else:
            print("\n" * 100)
        personne=Person("",None)
        personne.informationPerson()
        montant=price(personne.category,roomType)

        print("\n    Résumé    ")
        print(f"Film : {movie.nom}")
        print(f"Séance : {time} ({roomType})")
        print(f"E-mail : {personne.email}")
        print(f"Catégorie : {personne.category}")
        print(f"Prix du billet : {montant} €")
