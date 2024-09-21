# DataMoyGraph-05.py
# v04 prog de tracé des valeurs du Datafficheur, fonctionne avec défilement, amélioration grid
# v05 modif couleur courbe (rouge maxi et bleu moy)

# importation des modules 
import serial # import Serial Library
import numpy  # Import numpy
import matplotlib.pyplot as plt #import matplotlib library
from matplotlib.pyplot import figure
figure(figsize=(20, 10), dpi=150)
from drawnow import *
import time # gestion du temps


# from datetime import date
# today = date.today()
# DateJour = today.strftime("%m/%d/%Y")

from datetime import datetime
now = datetime.now()
DateJour = now.strftime("%d/%m/%Y %H:%M:%S")

liste_Moy=[]
liste_Max=[]
liste_temps_mesure =[] # liste pour stocker le temps"brut"
liste_temps=[] # liste pour stocker les valeurs de temps en partant de t=0
#arduinoData = serial.Serial('com11', 115200) #Creating our serial object named arduinoData
arduino_port = '/dev/ttyUSB0' # Préciser ici le port série. Ex. : sous Windows "COM4", sous linux "/dev/ttyACM0" ou "/dev/ttyUSB0"
arduino_baudrate = 9600 # La fréquence de la communication série (baudrate). Doit être identique à celui du code .ino
arduinoData = serial.Serial(arduino_port, arduino_baudrate) # Lancement de la communication série avec Arduino

plt.ion() #Tell matplotlib you want interactive mode to plot live data
cnt=0



def makeFig(): #Create a function that makes our desired plot
#     plt.ylim(80,90)                                 #Set y min and max values
    #plt.figure(figsize=(20,10), dpi=150)
    #plt.subplots(figsize=(20, 10), dpi=150)
    #plt.ylim(0,300)
    plt.ylim(0,350)
    plt.suptitle('DataMoyGraph-v05 (août-2024) pour Datafficheur (Deny-Fady)        Date : '+ DateJour)
    #plt.subtitle(current_date_and_time)
    plt.title('Val. moyenne sur 10 efforts et val. maxi sur ces 10 mesures (KgF)')      #Plot the title
#     plt.title('DataMoyGraph-v04-2024-07-14-Datafficheur-Deny-Fady')
#     plt.grid(True) #Turn the grid on
    plt.grid(True, linestyle='--')
    plt.grid(which='major',axis ='y', linewidth='1', color='black')
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
    plt.minorticks_on()
    plt.ylabel('Moyenne bleu (KgF)')                           #Set ylabels
    plt.xlabel('temps écoulé (s)')                                #,(str(tempsreel)))
#     plt.plot(tempF, 'ro-', label='Moy (KgF)')       #plot the temperature
#     plt.plot(liste_Moy, 'ro-', label='Moy (KgF)')
#     plt.plot(liste_Moy, label='Moy (KgF)')
    plt.plot(liste_Moy, 'r+-', label='Moy (KgF)', color = 'blue')
    plt.legend(loc='upper left')                    #plot the legend
    plt2=plt.twinx()                                #Create a second y axis
#     plt.ylim(93450,93525)                           #Set limits of second y axis- adjust to readings you are getting
    plt.ylim(0,300)
#    plt.xlim(0, tempsreel)
#     plt2.plot(pressure, 'b^-', label='Max (KgF)') #plot pressure data
#     plt2.plot(liste_Max, 'b^-', label='Max (KgF)')
#     plt2.plot(liste_Max, label='Max (KgF)')
    plt2.plot(liste_Max, 'b+-', label='Max (KgF)', color = 'red')
    plt2.set_ylabel('Maximum rouge (KgF)')                    #label second y axis
    plt2.ticklabel_format(useOffset=False)           #Force matplotlib to NOT autoscale y axis
    plt2.legend(loc='upper right') #plot the legend
    
    

while True: # While loop that loops forever
    while (arduinoData.inWaiting()==0): #Wait here until there is data
        pass #do nothing
    arduinoString = arduinoData.readline() #read the line of text from the serial port
    print ("arduinoString =",arduinoString)
    arduinoString = arduinoString.strip()
    print ("arduinoString =",arduinoString)
    arduinoString = arduinoString.split()
    print ("arduinoString =",arduinoString)
    
#     temp = float(arduinoString[0].decode()) # après consulation des données, nous choisissons le 1er élément de listeDonnees
#     P = float(arduinoString[2].decode()) # après consulation des données, nous choisissons le 3ème élément de listeDonnees
    Moy = float(arduinoString[0].decode()) # après consulation des données, nous choisissons le 1er élément de listeDonnees
    Max = float(arduinoString[2].decode()) # après consulation des données, nous choisissons le 3ème élément de listeDonnees

#     print ("Moy = ",temp)
#     print ("Max = ",P)
    print ("Moy = ",Moy)
    print ("Max = ",Max)

    tempsmes = time.time()
    liste_temps_mesure.append(tempsmes) # temps mesuré "brut" stocké dans une liste

#     dataArray = arduinoString.split(',')   #Split it into an array called dataArray
#     temp = float( dataArray[0])            #Convert first element to floating number and put in temp
#     P =    float( dataArray[1])            #Convert second element to floating number and put in P
#     tempF.append(Moy)                     #Build our tempF array by appending temp readings
#     pressure.append(Max)                     #Building our pressure array by appending P readings
    liste_Moy.append(Moy)
    liste_Max.append(Max)

    tempsreel = tempsmes - liste_temps_mesure[0] # pour faire partir le temps de 0 (cette valeur de temps sera stockée dans une autre liste : liste_temps)
    liste_temps.append(tempsreel)
    print("temps mesuré = %f"%(tempsmes), " s") # affichage de la valeur du temps absolu
    print("temps réel= %f"%(tempsreel), " s") # affichage de la valeur du temps en partant de 0
    drawnow(makeFig)                       #Call drawnow to update our live graph
    plt.pause(.000001)                     #Pause Briefly. Important to keep drawnow from crashing
    cnt=cnt+1
    print ("cnt = ",cnt)
    if(cnt>60):                            #If you have 60 or more points, delete the first one from the array
#         tempF.pop(0)                       #This allows us to just see the last 50 data points
#         pressure.pop(0)
        liste_Moy.pop(0)
        liste_Max.pop(0)
