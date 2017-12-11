
# coding: utf-8
from appJar import gui
import numpy, time, random, multiprocessing
class DaneStatkow():
    """
    Klasa odpowiadająca za załadowanie danych z plików tekstowych
    """
    def __init__(self, Dane, Dziala):
        """
        Konstruktor obiektu 'DaneStatkow'
        
        :param Dane: Sciezka pliku z danymi statków
        :param Dziala: Sciezka pliku z danymi na temat prawdopodobienstwa drugiego strzału
        :return: brak
        """
        with open(Dane) as f:
            self.lines = f.readlines()
        self.Dane = []
        for i in self.lines:
            self.Dane.append(i.rsplit())
        
        self.x = self.Dane 
        
        #Szybkie dziala
        with open(Dziala) as f:
            self.lines = f.readlines()
        self.Dziala = []
        for i in self.lines:
            self.Dziala.append(i.rsplit())
            
        #print self.x
            
    def GetDate(self, skrot):
        """
        Funkcja slużaca do zwrocenia danych konretnego typu statku
        
        :param skrot: zmienna przechowywujaca skróconą nazwe statku
        :return: Zwraca dane statku w liscie
        """
        Tab = []
        for i in range(len(self.x)):
            if self.x[i][0] == skrot:
                Tab.append(self.x[i][:])
        return Tab[0]
                    
    def GetDateSpeed(self):
        """
        Funkcja zwracająca dane na temat prawdopodobienstwa drugiego strzału
        
        :return: Zwraca liste tych danych"""
        return self.Dziala
    
    
class Statek():
    """
    Klasa Statek
    Przechowuje informacje na temat danej jednostki, jej wszystkie parametry
    """
    def __init__(self, dane, DaneStatkow):
        """
        Konstruktor klasy Statek, zapisuje wartosci danych z :param dane: i :param DaneStatkow: do własnej struktury
        
        :param dane: dane ktore wskazują na konkretny typ statku
        :param DaneStatkow: dane na temat samych parametrów statków
        :return: brak
        """
        TabDate = DaneStatkow.GetDate(dane)
        TabSpeed = DaneStatkow.GetDateSpeed()
        self.skrot = TabDate[0]
        self.nazwa = TabDate[1]
        self.pktstr = int(TabDate[2])
        self.oslona = int(TabDate[3])
        self.atak = int(TabDate[4])
        self.Default = TabDate
        self.SpeedC = TabSpeed
        
        #print self.skrot, self.nazwa, self.pktstr, self.oslona, self.atak
        
    def fire(self, Statek):
        """
        Funkcja fire odpowiadająca za sam strzał, czy wgl może nastapić, 
        odpowiednie odjęcie osłony lub pkt strukturalnych w atakowanym statku
        Sprawdzenie szans na ponowny strzał
        
        :param Statek: Parametr wprowadzający cel ataku statku
        :return: Zwraca True jeśli statek może ponownie strzelić, False gdy nie może
        """
        if self.atak > Statek.oslona/100:
            if Statek.oslona < self.atak:
                Pozatt = Statek.oslona - self.atak
                Statek.oslona = 0
                Pozatt = Pozatt*-1
                Statek.pktstr -= Pozatt
            else:
                Statek.oslona -= self.atak
            
        self.IsHit()
        #print 'xd'
        Statek.IsHit()
        
        chance = self.SpeedCompare(Statek)
        chance *= 100
        chance = int(chance)
        ch = random.randint(0, 100)
        if chance >= ch:
            return True
        else:
            return False
        
        #print self.skrot, self.nazwa, self.pktstr, self.oslona, self.atak
        #print Statek.skrot, Statek.nazwa, Statek.pktstr, Statek.oslona, Statek.atak
        
    def Destroy(self):
        """
        Funkcja odpowidajaca za zniszczenie statku
        
        :return: True jeśli statek jest zniszczony
        """
        self.pktstr = 0
        self.oslona = 0
        self.atak = 0
        return True
            
    def IsHit(self):
        """
        Funkcja sprwadza czy statek nie został zniszczony
        
        :return: True jeśli statek wybuchł i został zniszczony
        """
        #print self.pktstr, int(self.Default[2]) * 0.7
        if self.pktstr <= 0:
            return True
        elif self.pktstr < int(self.Default[2]) * 0.7:
            chance = 1.0-self.pktstr/float(int(self.Default[2]))
            #print chance
            chance *= 100
            chance = int(chance)
            ch = random.randint(0, 100)
            if chance >= ch:
                return True
                
    def SpeedCompare(self, Statek):
        """
        Funkcja sprawdzająca dane na temat szans na ponowny strzał anych statków
        
        :return: Zwraca szanse na ponowny strzał"""
        for i in range(len(self.SpeedC)):
            if self.SpeedC[0][i] == self.skrot:
                indexSelf = i
            if self.SpeedC[0][i] == Statek.skrot:
                indexStatek = i
            
        return self.SpeedC[indexStatek][indexSelf+1]
                
                
    def __str__(self):
        """
        Funkcja zwracająca dane parametry statku w formacie string
        
        :return: Zwrócenie paramterów danego statku w formacie string"""
        return self.skrot +' '+ self.nazwa + ' ' + str(self.pktstr) + ' ' + str(self.oslona) + ' ' + str(self.atak)
    
class Flota():
    """
    Klasa Flota odpowiadająca za stworzenie odpowiedniej ilości i typów statków
    """
    def __init__(self, Flota1, Flota2):
        """
        Konstruktor kalsy Flota, przyjmujący ścieżki do plików tekstowych zawierających dane na temat wielkości obu flot
        
        :param Flota1: ściezka do pliku z danymi o Flocie 1
        :param Flota2: ściezka do pliku z danymi o Flocie 2
        """

        self.obj1 = DaneStatkow('dane_statkow.txt', 'szybkie_dziala.txt')
        p1 = multiprocessing.Process(self.WczytanieDanychFlota1(Flota1))
        p2 = multiprocessing.Process(self.WczytanieDanychFlota2(Flota2))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
                
        self.Flota1Copy = self.Flota1[:]
        self.Flota2Copy = self.Flota2[:]  

    def WczytanieDanychFlota1(self, Plik):
        obj1 = DaneStatkow('dane_statkow.txt', 'szybkie_dziala.txt')
                # Flota1
        with open(Plik) as f:
            self.lines = f.readlines()
        self.Flota = []
        for i in self.lines:
            self.Flota.append(i.rsplit())
        self.Flota.pop(0)  
        self.Flota1 = []
        for i in range(len(self.Flota)):
            for j in range(int(self.Flota[i][1])):
                self.Flota1.append(Statek(str(self.Flota[i][0]), self.obj1))
                
    def WczytanieDanychFlota2(self, Plik):
        # Flota2
        with open(Plik) as f:
            self.lines = f.readlines()
        self.Flota = []
        for i in self.lines:
            self.Flota.append(i.rsplit())
        self.Flota.pop(0)    
        self.Flota2 = []
        for i in range(len(self.Flota)):
            for j in range(int(self.Flota[i][1])):
                self.Flota2.append(Statek(str(self.Flota[i][0]), self.obj1))
        
    def TotalWarBetter(self):
        """
        Funkcja odpowiadająca za bitwe
        
        :return: Zwraca liste pozostałych po bitwie Statków(obiektów)"""
        #print 'Ile Floty 2 ?', len(self.Flota2), 'Ile Floty 1 ?', len(self.Flota1), 'Przed walka \n',
        for i in range(6):
            #print 'Ile Floty 2 ?', len(self.Flota2), 'Ile Floty 1 ?', len(self.Flota1), 'Przed walka \n', i 
            self.Flota2Save = self.Flota2[:]
            #FLota1 atakuje 2
            for j in range(len(self.Flota1)):
                if len(self.Flota2) == 0:
                    break
                choice = random.randint(0, len(self.Flota2)-1)
                if self.Flota1[j].fire(self.Flota2[choice]) == True:
                    if self.Flota2[choice].IsHit() == True:
                        self.Flota2.pop(choice)
                        if len(self.Flota2) == 0:
                            break
                    choice = random.randint(0, len(self.Flota2)-1)
                    self.Flota1[j].fire(self.Flota2[choice])
                    if self.Flota2[choice].IsHit() == True:
                        self.Flota2.pop(choice)
                        if len(self.Flota2) == 0:
                            break
                else:
                    if self.Flota2[choice].IsHit() == True:
                        self.Flota2.pop(choice)
                        
            # Flota 2 atakuje 1
            #print len(self.Flota2Save)
            for j in range(len(self.Flota2Save)):
                if len(self.Flota1) == 0:
                    break
                choice = random.randint(0, len(self.Flota1)-1)
                if self.Flota2Save[j].fire(self.Flota1[choice]) == True:
                    if self.Flota1[choice].IsHit() == True:
                        self.Flota1.pop(choice)
                        if len(self.Flota1) == 0:
                            break
                    choice = random.randint(0, len(self.Flota1)-1)
                    self.Flota2Save[j].fire(self.Flota1[choice])
                    if self.Flota1[choice].IsHit() == True:
                        self.Flota1.pop(choice)
                        if len(self.Flota1) == 0:
                            break
                else:
                    if self.Flota1[choice].IsHit() == True:
                        self.Flota1.pop(choice)

            if len(self.Flota2) <= 0 or len(self.Flota1) <= 0:
                break
            else:
                for i in range(len(self.Flota1)):
                    self.Flota1[i].oslona = int(self.Flota1[i].Default[3])
                for i in range(len(self.Flota2)):
                    self.Flota2[i].oslona = int(self.Flota2[i].Default[3])
                        
            #print 'Ile Floty 2 ?', len(self.Flota2), 'Ile Floty 1 ?', len(self.Flota1), 'Przed walka \n',
        F1 = self.Flota1[:]
        F2 = self.Flota2[:]
        self.Flota1 = self.Flota1Copy[:]
        self.Flota2 = self.Flota2Copy[:]   
        return [F1, F2]
    
    
    def TotalWarOrginal(self):
        """
        Funkcja odpowiadająca za bitwe
        
        :return: Zwraca liste pozostałych po bitwie Statków(obiektów)"""
        #print 'Ile Floty 2 ?', len(self.Flota2), 'Ile Floty 1 ?', len(self.Flota1), 'Przed walka \n', i
        for i in range(6):
            #print 'Ile Floty 2 ?', len(self.Flota2), 'Ile Floty 1 ?', len(self.Flota1), 'Przed walka \n', i    
            self.Flota2Save = self.Flota2[:]
            #FLota1 atakuje 2
            for j in range(len(self.Flota1)):
                if len(self.Flota2) == 0:
                    break
                choice = random.randint(0, len(self.Flota2)-1)
                if self.Flota1[j].fire(self.Flota2[choice]) == True:
                    if self.Flota2[choice].IsHit() == True:
                        if len(self.Flota2) == 0:
                            break
                    choice = random.randint(0, len(self.Flota2)-1)
                    self.Flota1[j].fire(self.Flota2[choice])
                    if self.Flota2[choice].IsHit() == True:
                        pass
                        if len(self.Flota2) == 0:
                            break


            for j in range(len(self.Flota2Save)):
                if len(self.Flota1) == 0:
                    break
                choice = random.randint(0, len(self.Flota1)-1)
                if self.Flota2Save[j].fire(self.Flota1[choice]) == True:
                    if self.Flota1[choice].IsHit() == True:
                        if len(self.Flota1) == 0:
                            break
                    choice = random.randint(0, len(self.Flota1)-1)
                    self.Flota2Save[j].fire(self.Flota1[choice])
                    if self.Flota1[choice].IsHit() == True:
                        if len(self.Flota1) == 0:
                            break
               
                        
            if len(self.Flota2) <= 0 or len(self.Flota1) <= 0:
                break
            else:
                End = False
                i = 0

                while End == False:
                    if self.Flota1[i].pktstr <= 0:
                        self.Flota1.pop(i)
                    if i+1 >= len(self.Flota1)-1:
                        End = True
                    i += 1

                End = False
                i = 0

                while End == False:
                    if self.Flota2[i].pktstr <= 0:
                        self.Flota2.pop(i)
                    if i+1 >= len(self.Flota2)-1:
                        End = True
                    i += 1
                
                for i in range(len(self.Flota1)):
                    self.Flota1[i].oslona = int(self.Flota1[i].Default[3])
                for i in range(len(self.Flota2)):
                    self.Flota2[i].oslona = int(self.Flota2[i].Default[3])
                    
            
        F1 = self.Flota1[:]
        F2 = self.Flota2[:]
        self.Flota1 = self.Flota1Copy[:]
        self.Flota2 = self.Flota2Copy[:]     
        return [F1, F2]
    
    def prt(self):
        """
        Funkcja wypisuje wszystkie statki w danej flocie
        
        :return: brak"""
        for i in range(len(self.Flota1)):
            print self.Flota1[i].skrot +' '+ self.Flota1[i].nazwa + ' ' + str(self.Flota1[i].pktstr) + ' ' + str(self.Flota1[i].oslona) + ' ' + str(self.Flota1[i].atak)
        for i in range(len(self.Flota2)):
            print self.Flota2[i].skrot +' '+ self.Flota2[i].nazwa + ' ' + str(self.Flota2[i].pktstr) + ' ' + str(self.Flota2[i].oslona) + ' ' + str(self.Flota2[i].atak)
def testBetter(ilosc):
    """
    Funkcja odpowiadająca za test symulacji dla własnej funkcji
    
    :param ilosc: Zmianna określająca ilość przeprowadzonych symulacji"""
    X = [0,0] 
    obj1 = Flota('flota_1.txt', 'flota_2.txt') 
    t1 = time.time()
    for i in range(ilosc):
        z = obj1.TotalWarBetter()  
        X[0] += len(z[0])
        X[1] += len(z[1])
    print 'Ile FLoty 1? : ', X[1]/ilosc , 'Ile Floty 2? : ', X[0]/ilosc, 'Czas', time.time() - t1
    


def testOrginal(ilosc):
    """
    Funkcja odpowiadająca za test symulacji doa orginalnej funkcji
    
    :param ilosc: Zmianna określająca ilość przeprowadzonych symulacji"""
    X = [0,0] 
    obj1 = Flota('flota_1.txt', 'flota_2.txt')
    t1 = time.time()
    for i in range(ilosc):   
        z = obj1.TotalWarOrginal()  
        X[0] += len(z[0])
        X[1] += len(z[1])
    print 'Ile FLoty 1? : ', X[1]/ilosc , 'Ile Floty 2? : ', X[0]/ilosc, 'Czas', time.time() - t1

testBetter(1)    
#testOrginal(1)



