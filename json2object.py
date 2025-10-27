import json
from types import SimpleNamespace
def jsonToObject (fileName) :
    try : 
        data = open("./Database/"+fileName+".json")
    #data = open("Films.json", encoding="utf-8")
    except :
        print("ERROR check if"+fileName+".json exists")
        exit()
    x = json.load(data , object_hook = SimpleNamespace) #fait un conversion json->dictionnaire->objet
    return x

#comme on ne peut pas mettre de méthode dans les fichier JSON il faudrait faire une fonction qui ajoute les méthodes
#après chaque conversion jsonToObject (et une qui permet de les enlever pour l'autre sens)

def objectToJson (obj,fileName): #testée seulement avec des tableaux d'objets
    try :
        with open("./Database/"+fileName+".json","w", encoding="utf-8") as f:
            f.write(json.dumps(obj,default=lambda o: vars(o))) #conversion objet -> dictionnaire -> json 
    except :
        print("Error with obj to json conversion")
        exit()
#print(type(jsonToObject('Films')))



#x =jsonToObject('Films')
#objectToJson(x,'Films')