import json2object
import math
screeningRooms = json2object.jsonToObject('Salles')
def initRoom (room) :   #initialize un tableau 2D en fonction du nombre de place (on considère que le nombre de place est un carré parfait)
    width = math.ceil(math.sqrt(room.nbPlaces))       
    seats = [[0 for i in range(width)] for  j in range(width)]
    return seats

def printRoom(room) :  # a mettre en tant que méthode pour les salles 
    for i in range(len(room.seats)) :
        if i == (len(room.seats))-1 :
            print(str(i))
        elif i == 0 :
            print('   '+str(i)+'  ',end='')
        elif i>9 :
            print(str(i)+' ',end='')
        else :
            print(str(i)+'  ',end='')
    i = 0
    for row in room.seats :
        if i<10 :
            print(str(i)+' '+str(row))
        else :
            print(str(i)+str(row))
        i +=1

for room in screeningRooms :
    room.seats = initRoom(room)
    #for row in room.seats :
    #    print(row)

def roomInterface(room) :
    room =screeningRooms[int(input('Num Salle'))] #en attendant d'avoir de quoi savoir quelle scéance va dans quelle salle
    while True :
        #print('\n'*100)
        printRoom(room)
        seatChoiceX = int(input('Place Colonne'))
        seatChoiceY = int(input('Place ligne'))
        confirmSeat = input('Place : ('+str(seatChoiceX)+','+str(seatChoiceY)+')? Y/N')
        if confirmSeat.lower() == 'y' :
            (room.seats)[seatChoiceY][seatChoiceX] = 1 #remplacer 1 par un objet personne
            printRoom(room)
            break
        else :
            pass



