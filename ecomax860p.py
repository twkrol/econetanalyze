# Analizator EcoNet
# (C) 2020 Tomasz Król https://github.com/twkrol/econetanalyze
# Gwarancji żadnej nie daję. Ale można korzystać do woli i modyfikować wg potrzeb

import struct

print("Zaimportowano bibliotekę sterownika EcoMax860P")

# funkcja kierująca odpowiedni typ ramki do obsługującej ją funkcji parsującej
def parseFrame(message):
    if message[0] == 0x08:
        parseFrame08(message)
    else:
        print(f"Parser EcoMax: Nieznany typ ramki 0x{message[0]:02X}")

# funkcja parsująca ramkę typu 0x08 sterownika EcoMax860P
def parseFrame08(message):
    #mapa komunikatu stanu ze sterownika pieco EcoMax860P
    # typ ramki = 0x08          #[0]
    OPERATING_STATUS_byte = 33  #[33]
    TEMP_CWU_float = 74         #[74-77]
    TEMP_FEEDER_float = 78      #[78-81]
    TEMP_CO_float = 82          #[82-85]
    TEMP_WEATHER_float = 90     #[90-93]
    TEMP_EXHAUST_float = 94     #[94-97]
    TEMP_MIXER_float = 106      #[106-109]
    #pompa-stany 4B
    #pompa-nastawy 4B
    #numT 1B
    #iloczyn numT * 5
    TEMP_CWU_SET_byte = 146     #[146] lub #29
    TEMP_CO_SET_byte = 148      #[148]
    #statusCO 1B
    #statusCWU 1B
    #alarmsNo 1B  #[187]
    #iloczyn alarmsNo * 1B
    FUEL_LEVEL_byte=189         #[189]
    #transmission_BYTE=190
    #fanPower_FLOAT=191-194
    BOILER_POWER_byte=196       #[196]
    #boilerPowerKW_FLOAT=197-200
    #fuelStream=201-204
    #thermostat=205
    #versionInfo=204-208
    #moduleBSoftVer=209-211
    #moduleCSoftVer=212-214
    #moduleLambdaSoftVer=215-217 ?a nie zawór mieszacza?
    #moduleEcoSTERSoftVer=218-220
    #modulePanelSoftVer=221-223
    #lambdaStatus=224
    #lambdaSet=225
    LAMBDA_LEVEL_float=226      #[226-229]
    OXYGEN_float = 230          #[230-233]
    POWER100_TIME_short = 235   #[235-236]
    POWER50_TIME_short = 237    #[237-238]
    POWER30_TIME_short = 239    #[239-240]
    FEEDER_TIME_short = 241     #[241-242]
    IGNITIONS_short = 243       #[243-244]

    OPERATION_STATUSES = {0:'WYŁĄCZONY', 1:'ROZPALANIE', 2:'STABILIZACJA', 3:'PRACA', 4:'NADZÓR', 5:'WYGASZANIE', 7:'WYGASZANIE NA ŻĄDANIE'}

    print("")

    #Stan pieca [33]
    print(f"Stan pieca: {OPERATION_STATUSES[message[OPERATING_STATUS_byte]] if message[OPERATING_STATUS_byte] in OPERATION_STATUSES else str(message[OPERATING_STATUS_byte]) }")

    #Poziom paliwa [189]
    print(f"Poziom paliwa: {message[FUEL_LEVEL_byte]}%")

    #Temperatura CWU [74-77]
    tempCWU = struct.unpack("f", bytes(message[TEMP_CWU_float:TEMP_CWU_float+4]))[0]
    print(f"Temperatura CWU: {tempCWU:.1f}")

    #Temperatura CO [82-85]
    tempCO = struct.unpack("f", bytes(message[TEMP_CO_float:TEMP_CO_float+4]))[0]
    print(f"Temperatura CO: {tempCO:.1f}")

    #Temperatura pogodowa
    tempPogodowa= struct.unpack("f", bytes(message[TEMP_WEATHER_float:TEMP_WEATHER_float+4]))[0]
    print(f"Temperatura pogodowa: {tempPogodowa:.1f}")

    #Temperatura spalin
    tempSpalin = struct.unpack("f", bytes(message[TEMP_EXHAUST_float:TEMP_EXHAUST_float+4]))[0]
    print(f"Temperatura spalin: {tempSpalin:.1f}")

    #Temperatura podajnika
    tempPodajnika = struct.unpack("f", bytes(message[TEMP_FEEDER_float:TEMP_FEEDER_float+4]))[0]
    print(f"Temperatura podajnika: {tempPodajnika:.1f}")

    #Tlen
    tlen = struct.unpack("f", bytes(message[OXYGEN_float:OXYGEN_float+4]))[0]
    print(f"Tlen: {tlen:.1f}%")

    #Temperatura mieszacza
    tempMieszacza = struct.unpack("f", bytes(message[TEMP_MIXER_float:TEMP_MIXER_float+4]))[0]
    print(f"Temperatura mieszacza: {tempMieszacza:.1f}")

    #Moc kotła
    moc = message[BOILER_POWER_byte]
    print(f"Moc kotła: {moc:d}%")

    #LambdaSet
    lambdaLevel = struct.unpack("f", bytes(message[226:226+4]))[0]
    print(f"Lambda: {lambdaLevel:.1f}")

    #Zawór mieszacza?
    m = message[215]
    print(f"Zawór mieszacza?: {m:d}%")

