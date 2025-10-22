import json2object
answer = 'N'
while answer.lower() != 'y' :
    print("\n" * 100) 
    answer =input("Reserver une scéance ? Y/N \n")
print("\n" * 100) 
movies  =json2object.jsonToObject('Films')
clients = json2object.jsonToObject('Personnes')

while True :
    i=1
    for movie in movies :
        print(str(i) + ") ["+movie.nom+"] - "+movie.realisateur)
        i+=1
    choice = 0
    while choice < 1 or choice > i  :
        try :
            choice = int(input("\n"))
        except :
            choice = 0
            pass

    print("\n" * 100) 
    print(movies[choice].nom+"\n"+movies[choice].realisateur+"\n"+str(movies[choice].duree)+"min\n"+movies[choice].genre)
    confirm = input("Reserver ? Y/N \n")
    if confirm.lower() == 'y' :
        break
    else :
        print("\n"*100)
        pass


