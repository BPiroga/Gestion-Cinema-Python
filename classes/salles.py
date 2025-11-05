class ScreeningRoom:
    def __init__(self, number, roomType, capacity):
        self.number = number
        self.roomType = roomType
        self.capacity = capacity
        self.availableSeats = capacity

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
