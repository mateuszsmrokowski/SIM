
# coding: utf-8
#from appJar import gui

import sys
sys.path.append("/home/student/eclipse-workspace/War/Main")
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
        if isinstance(Flota1, str) == True:
            p1 = multiprocessing.Process(self.WczytanieDanychFlota1(Flota1))
            p2 = multiprocessing.Process(self.WczytanieDanychFlota2(Flota2))
            p1.start()
            p2.start()
            p1.join()
            p2.join()
            
        else:
            self.Flota1 = []
            self.Flota2 = []
            for i in range(len(Flota1)):
                for j in range(int(Flota1[i][1])):
                    self.Flota1.append(Statek(str(Flota1[i][0]), self.obj1))
                
            for i in range(len(Flota2)):
                for j in range(int(Flota2[i][1])):
                    self.Flota2.append(Statek(str(Flota2[i][0]), self.obj1))
                
                
                
        self.Flota1Copy = self.Flota1[:]
        self.Flota2Copy = self.Flota2[:]  
        
        

    def WczytanieDanychFlota1(self, Plik):
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
            print 'Ile Floty 2 ?', len(self.Flota2), 'Ile Floty 1 ?', len(self.Flota1), 'Przed walka \n', i 
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
                        
        print 'Ile Floty 2 ?', len(self.Flota2), 'Ile Floty 1 ?', len(self.Flota1), 'Przed walka \n',
        F1 = self.Flota1[:]
        F2 = self.Flota2[:]
        self.Flota1 = self.Flota1Copy[:]
        self.Flota2 = self.Flota2Copy[:]   
        return [F1, F2]
    
    
    def TotalWarOrginal(self):
        class GetOutOfLoop( Exception ):
            pass
        """
        Funkcja odpowiadająca za bitwe
        
        :return: Zwraca liste pozostałych po bitwie Statków(obiektów)"""
        #print 'Ile Floty 2 ?', len(self.Flota2), 'Ile Floty 1 ?', len(self.Flota1), 'Przed walka \n', i
        try:
            for i in range(6):
                print 'Ile Floty 2 ?', len(self.Flota2), 'Ile Floty 1 ?', len(self.Flota1), 'Przed walka \n', i    
                self.Flota2Save = self.Flota2[:]
                #FLota1 atakuje 2
                for j in range(len(self.Flota1)):
                    if len(self.Flota2) == 0:
                        break
                        raise GetOutOfLoop
                    choice = random.randint(0, len(self.Flota2)-1)
                    if self.Flota1[j].fire(self.Flota2[choice]) == True:
                        if self.Flota2[choice].IsHit() == True:
                            if len(self.Flota2) == 0:
                                break
                                raise GetOutOfLoop
                        choice = random.randint(0, len(self.Flota2)-1)
                        self.Flota1[j].fire(self.Flota2[choice])
                        if self.Flota2[choice].IsHit() == True:
                            pass
                            if len(self.Flota2) == 0:
                                break
                                raise GetOutOfLoop
    
    
                for j in range(len(self.Flota2Save)):
                    if len(self.Flota1) == 0:
                        break
                        raise GetOutOfLoop
                    choice = random.randint(0, len(self.Flota1)-1)
                    if self.Flota2Save[j].fire(self.Flota1[choice]) == True:
                        if self.Flota1[choice].IsHit() == True:
                            if len(self.Flota1) == 0:
                                break
                                raise GetOutOfLoop
                        choice = random.randint(0, len(self.Flota1)-1)
                        self.Flota2Save[j].fire(self.Flota1[choice])
                        if self.Flota1[choice].IsHit() == True:
                            if len(self.Flota1) == 0:
                                break
                                raise GetOutOfLoop
                   
                            
                if len(self.Flota2) <= 0 or len(self.Flota1) <= 0:
                    break
                    raise GetOutOfLoop
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
                    
        except GetOutOfLoop:
            pass
        
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
def testBetter(ilosc, File='txt'):
    """
    Funkcja odpowiadająca za test symulacji dla własnej funkcji
    
    :param ilosc: Zmianna określająca ilość przeprowadzonych symulacji"""
    X = [0,0]
    if File == "txt":
        obj1 = Flota('flota_1.txt', 'flota_2.txt')
    else:
        Fl1 = []
        Fl2 = []
        x = app.getAllEntries()
        Temp = x.items()
        for i in range(len(Temp)):
            if '1' in Temp[i][0]:
                if Temp[i][1] == '':
                    Fl1.append([Temp[i][0], 0])
                else:    
                    Fl1.append([Temp[i][0], int(Temp[i][1])])
            else:
                if Temp[i][1] == '':
                    Fl2.append([Temp[i][0], 0])
                else:
                    Fl2.append([Temp[i][0], int(Temp[i][1])])
        #print Fl1, Fl2
        
        for i in range(len(Fl1)):
            x = Fl1[i][0] 
            x = x[:-1]
            Fl1[i][0] = x 
            
            x = Fl2[i][0] 
            x = x[:-1]
            Fl2[i][0] = x 
                
        obj1 = Flota(Fl1, Fl2)
        #print Fl1, Fl2
    t1 = time.time()
    for i in range(ilosc):
        z = obj1.TotalWarBetter()  
        X[0] += len(z[0])
        X[1] += len(z[1])
    return 'Ile FLoty 1? : '+ str(X[1]/ilosc) + ' Ile Floty 2? : '+ str(X[0]/ilosc) + ' Czas '+ str(time.time() - t1)
    


def testOrginal(ilosc, File='txt'):
    """
    Funkcja odpowiadająca za test symulacji doa orginalnej funkcji
    
    :param ilosc: Zmianna określająca ilość przeprowadzonych symulacji"""
    X = [0,0] 
    if File == "txt":
        obj1 = Flota('flota_1.txt', 'flota_2.txt')
    else:
        Fl1 = []
        Fl2 = []
        x = app.getAllEntries()
        Temp = x.items()
        for i in range(len(Temp)):
            if '1' in Temp[i][0]:
                if Temp[i][1] == '':
                    Fl1.append([Temp[i][0], 0])
                else:    
                    Fl1.append([Temp[i][0], int(Temp[i][1])])
            else:
                if Temp[i][1] == '':
                    Fl2.append([Temp[i][0], 0])
                else:
                    Fl2.append([Temp[i][0], int(Temp[i][1])])
        #print Fl1, Fl2
        
        for i in range(len(Fl1)):
            x = Fl1[i][0] 
            x = x[:-1]
            Fl1[i][0] = x 
            
            x = Fl2[i][0] 
            x = x[:-1]
            Fl2[i][0] = x 
                
        obj1 = Flota(Fl1, Fl2)
        
    t1 = time.time()
    for i in range(ilosc):   
        z = obj1.TotalWarOrginal()  #app = gui("Battle bitch! ", "400x200")
        X[0] += len(z[0])
        X[1] += len(z[1])
    return 'Ile FLoty 1? : '+ str(X[1]/ilosc) + 'Ile Floty 2? : '+ str(X[0]/ilosc) + 'Czas', str(time.time() - t1)

#testBetter(1)    
#testOrginal(1)
def press(button):
    if button == "Better":
        x = testBetter(1)
        app.setLabel("l1", x)
    if button == "Orginal":
        x = testOrginal(1)
        app.setLabel("l1", x)
        
app = gui()
app.setGeometry("450x600")
app.addLabel("title1", "Flota1 ", 0, 0, 1)
app.addLabel("title2", "Flota2 ", 0, 1, 2)
app.addLabelEntry("mt1", 1, 0)
app.addLabelEntry("dt1", 2, 0)
app.addLabelEntry("lm1", 3, 0)
app.addLabelEntry("cm1", 4, 0)
app.addLabelEntry("kr1", 5, 0)
app.addLabelEntry("ow1", 6, 0)
app.addLabelEntry("sk1", 7, 0)
app.addLabelEntry("re1", 8, 0)
app.addLabelEntry("ss1", 9, 0)
app.addLabelEntry("b1",  10, 0)
app.addLabelEntry("n1",  11, 0)
app.addLabelEntry("gs1", 12, 0)
app.addLabelEntry("p1",  13, 0)


app.addLabelEntry("mt2", 1, 1)
app.addLabelEntry("dt2", 2, 1)
app.addLabelEntry("lm2", 3, 1)
app.addLabelEntry("cm2", 4, 1)
app.addLabelEntry("kr2", 5, 1)
app.addLabelEntry("ow2", 6, 1)
app.addLabelEntry("sk2", 7, 1)
app.addLabelEntry("re2", 8, 1)
app.addLabelEntry("ss2", 9, 1)
app.addLabelEntry("b2",  10, 1)
app.addLabelEntry("n2",  11, 1)
app.addLabelEntry("gs2", 12, 1)
app.addLabelEntry("p2",  13, 1)

app.addLabel("title", "Lets the battle begin", 14, 0, 2)
app.setLabelBg("title", "red")
app.addButtons(["Better"],  press, 15, 0)
app.addButtons(["Orginal"],  press, 15, 1)
app.addLabel("l1", "", 16, 0, 2)
app.go()

