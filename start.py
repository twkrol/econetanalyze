# Analizator EcoNet
# (C) 2020 Tomasz Król https://github.com/twkrol/econetanalyze
# Gwarancji żadnej nie daję. Ale można korzystać do woli i modyfikować wg potrzeb

import functools
import math
import socket
import struct
import sys

#########################################################################
# PARAMETRY ANALIZY
#########################################################################

# aby czytać z portu szeregowego doinstaluj bibliotekę pyserial i odkomentuj poniższy import
# import serial

# import parsera ramek sterowników EcoSter (również EcoTouch) z pliku ecoster.py
import ecoster

# import parsera ramek sterownika EcoMax860p z pliku ecomax860p.py
# jeśli masz inny sterownik - napisz do niego swoją bibliotekę wzorując się na poniższej i podmień import np. import ecomax350 as ecomax
# jednocześnie może być zaimportowana tylko jedna biblioteka o nazwie lub aliasie ecomax
import ecomax860p as ecomax


#ŹRÓDŁO DANYCH
#odkomentuj odpowiednią linię SOURCE=  aby czytać dane z pliku, strumienia sieciowego lub portu szeregowego

# SOURCE = 'FILE'
filePATH = "raw.txt"

SOURCE = 'STREAM'
streamIP = '192.168.99.158'
streamPORT = 23

# SOURCE = 'SERIAL'
serialPORT = "/dev/ttyUSB0"
serialBAUDRATE = 115200



#########################################################################
# START ANALIZY
#########################################################################

#stałe
RAMKA_START = 0x68
RAMKA_STOP = 0x16
NADAWCA_ECONET = 0x56
NADAWCA_ECOMAX860P = 0x45     #piec pelletowy
NADAWCA_ECOSTER = 0x51        #panel dotykowy
NADAWCA_TYP_ECONET = 0x30
# ODBIORCA_BROADCAST = 0x00

#typy ramek
# RAMKA_ALARM = 0xBD
RAMKA_INFO_STEROWNIKA = 0x08
RAMKA_INFO_PANELU = 0x89

try:
  SOURCE
except:
  print("Nie wybrano źródła danych! Popraw konfigurację na początku tego pliku.")
  exit()

if SOURCE == 'FILE':
  f = open(filePATH, 'rb')
  print (f"Plik {filePATH} został otwarty")

elif SOURCE == 'STREAM':
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((streamIP, streamPORT))
  print (f"Port {streamPORT} pod adresem {streamIP} został otwarty")

elif SOURCE == 'SERIAL':
  ser = serial.Serial(serialPORT, serialBAUDRATE)
  ser.bytesize = serial.EIGHTBITS
  ser.parity = serial.PARITY_NONE
  ser.stopbits = serial.STOPBITS_ONE
  ser.open()
  print (f"Port {serialPORT} został otwarty")

else:
  print("Nieznany typ źródła danych. Popraw konfigurację na początku tego pliku.")
  exit()


bajtCzytany = 0 # bajt aktualnie przetwarzany
bajtPoprzedni = 0
ramka = []

#mapa ramki
START_BYTE = 0              #[0]
ROZMIAR_RAMKI_SHORT = 1     #[1,2]
ADRES_ODBIORCY_BYTE = 3     #[3]
ADRES_NADAWCY_BYTE = 4      #[4]
TYP_NADAWCY_BYTE = 5        #[5]
WERSJA_ECONET_BYTE = 6      #[6]
TYP_RAMKI = 7               #[7]
CRC_BYTE = -2               #[przedostatni bajt]
MESSAGE_START = 7           #od-do [7:-2]


while True:
  #pobieramy 1 bajt, z pliku, sieci lub portu szeregowego

  if SOURCE == 'FILE':
    chunk = f.read(1)
    if len(chunk) == 0:
      break
  elif SOURCE == 'STREAM':
    chunk = s.recv(1)
  elif SOURCE == 'SERIAL':
    chunk = ser.read(1)

  bajtCzytany = ord(chunk)

  #badamy czy to początek nowej ramki
  if bajtCzytany == RAMKA_START and bajtPoprzedni == RAMKA_STOP:

    #zaczęła się nowa ramka wiec zebrane do tej pory dane do analizy, jesli jakieś są
    if len(ramka) > 0:
  
      #badanie sumy kontrolnej CRC
      ramkaCRC = ramka[-2]
      myCRC = functools.reduce(lambda x,y: x^y, ramka[:-2])
      # print(f"wyliczone CRC: {myCRC:02X}")

      #analizujemy ramkę tylko jak CRC się zgadza
      if myCRC == ramkaCRC:

        #zawartość ramki w hex dla czytelniejszego kodu i prezentacji
        ramkaHEX = [f'{ramka[i]:02X}' for i in range(0, len(ramka))]
        
        #wyciągamy z ramki właściwy message
        message = ramka[MESSAGE_START:CRC_BYTE]
        messageHEX = ramkaHEX[MESSAGE_START:CRC_BYTE]

        #dane diagnostyczne ramki
        if len(message) > 1:
          print("")
          print(f"== [ramka] [Typ: 0x{ramka[TYP_RAMKI]:02X}] [Długość:{len(ramka)}] [Nadawca: 0x{ramka[ADRES_NADAWCY_BYTE]:02X}] [Odbiorca: 0x{ramka[ADRES_ODBIORCY_BYTE]:02X}] [CRC:0x{ramkaCRC:02X}] ==")
          
          #zawartość ramki w ASCII
          # if True:
          #   tekst = ''
          #   for i in range(7, len(ramka)-2):
          #     if ramka[i] > 32 and ramka[i] < 127:
          #       tekst += chr(ramka[i])
          #   print(tekst)

          #Zawartość ramki w HEX i DEC
          rowsize=12
          for row in range(math.ceil(len(message)/rowsize)):
            od = row*rowsize
            do = od+rowsize if len(message) >= od+rowsize else len(message)
            print(f"{od:03d}-{do-1:03d} \t{' '.join(messageHEX[od:do])}", end='')
            print('   ' * ((od+rowsize)-do), end='')
            print(f" \t{message[od:do]}")


        #Analiza komunikatu ze sterownika pokojowego ECOTouch
        # if ramka[TYP_RAMKI] == RAMKA_INFO_PANELU and ramka[ADRES_NADAWCY_BYTE] == NADAWCA_ECOSTER: #and ramka[RECIPIENT_ADDRESS_BYTE]==ODBIORCA_BROADCAST:
        if ramka[ADRES_NADAWCY_BYTE] == NADAWCA_ECOSTER:
          ecoster.parseFrame(message)

        #Analiza komunikatu ze sterownika pieca EcoMax
        if ramka[TYP_RAMKI] == RAMKA_INFO_STEROWNIKA and ramka[ADRES_NADAWCY_BYTE] == NADAWCA_ECOMAX860P: #and ramka[RECIPIENT_ADDRESS_BYTE]==ODBIORCA_BROADCAST:
          ecomax.parseFrame(message)


    #ramka przeanalizowana, można wyczyścić i aktualny bajt zostanie wpisany już do nowej (poniżej)
    ramka = []


  #dodajemy przeczytany bajt do bieżącej ramki
  ramka.append(bajtCzytany)  

  #zapamiętujemy ostatni bajt żeby zdekodować zakończenie ramki
  bajtPoprzedni = bajtCzytany