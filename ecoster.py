# Analizator EcoNet
# (C) 2020 Tomasz Król https://github.com/twkrol/econetanalyze
# Gwarancji żadnej nie daję. Ale można korzystać do woli i modyfikować wg potrzeb

import struct

print("Zaimportowano bibliotekę sterownika EcoSter/EcoTouch")

# funkcja kierująca odpowiedni typ ramki do obsługującej ją funkcji parsującej
def parseFrame(message):
    if message[0] == 0x89:
        parseFrame89(message)
    else:
        print(f"Parser EcoSter: Nieznany typ ramki 0x{message[0]:02X}")

# funkcja parsująca ramkę typu 0x08 sterownika EcoTouch (i pewnie innych z rodziny EcoSter)
def parseFrame89(message):
    #mapa komunikatu z panelu ECOTouch
    # typ ramki = 0x89            #[0]
    # tekst TIME                  #[1-4]
    # godzina                     #[5]
    # minuta                      #[6]
    # sekunda                     #[7]
    # rok (short)                 #[8-9]
    # miesiąc                     #[10]
    # dzień                       #[11]
    #                             #[12-16]
    TEMP_HOME_SET_FLOAT = 17      #[17-20]
    TEMP_HOME_CURR_FLOAT = 21     #[21-24]
    # nieznana temperatura_FLOAT  #[25-28]
    # nieznana temperatura_FLOAT  #[29-32]
    # nazwa panelu                #[33-n]
    # zero jako koniec nazwy      #[n+1]
    #                             #[n+2-koniec]  

    print("")

    #Temperatura domowa zadana [17-20]
    tempDomSet = struct.unpack("f", bytes(message[TEMP_HOME_SET_FLOAT:TEMP_HOME_SET_FLOAT+4]))[0]
    print(f"Temperatura pokojowa zadana: {tempDomSet:.1f}")

    #Temperatura domowa bieżąca [21-24]
    tempDomCurr = struct.unpack("f", bytes(message[TEMP_HOME_CURR_FLOAT:TEMP_HOME_CURR_FLOAT+4]))[0]
    print(f"Temperatura pokojowa bieżąca: {tempDomCurr:.1f}")

    #Temperatura x [25-28]
    # tempx = struct.unpack("f", bytes(message[25:25+4]))[0]
    # print(f"Temperatura x: {tempx:.1f}")

