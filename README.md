# econetanalyze
Analizator Econet - do prześwietlania sterowników firmy Plum

# Przeznaczenie
Niniejszy analizator służy do dekodowania transmisji szeregowej pomiędzy sterownikami serii EcoNet firmy Plum na interfejsie RS485.
Producent nie udostępnia dokumentacji używanego protokołu, dlatego konieczna była ręczna analiza przesyłanych danych i odkrywanie ich znaczenia metodą prób i błędów.

Praca nie została ukończona, ale stan obecny pozwala na odczyt podstawowych parametrów, takich jak: poziom paliwa, temperatury, stan pracy kotła, etc.
Na podstawie tych prac możliwe jest wykorzystanie odczytanych danych np. w systemach automatyki domowej takich jak Home Assistant, Domoticz, itp.

# Działanie
Po ściągnięciu plików należy zmodyfikować konfigurację w pliku **start.py** wskazując źródło danych.
Następnie, po jego uruchomieniu zostaną na ekranie wyświetlone kolejne odczytane ramki (z transmisji zapisanej lub na żywo), które można poddać analizie (dane prezentowane są szesnastkowo lub dziesiętnie).

W pliku istnieje również zakomentowany fragment kodu, pozwalający na wyświetlanie znaków wg kodu ASCII (bajty o wartościach 32 do 127) ale zwykle nie jest to potrzebne.

# Wymagania
Do działania wymagany jest python w wersji 3 (testowane na wersji 3.7)

# Zalecany sposób uruchomienia

1. Ściągnij pliki z tego repozytorium do folderu lokalnego (git clone lub pobierając ręcznie z githuba)
2. Uruchom środowisko wirtualne pythona, np. przy pomocy pipenv:
```pipenv --python 3.7```
3. Aktywuj środowisko poleceniem 
```pipenv shell```
4. Zmodyfikuj plik ```start.py``` określając źródło danych do analizy
5. Uruchom analizator poleceniem
```python start.py```

# Obsługiwane sterowniki

## EcoSter/EcoTouch
Analizator potrafi odczytywać podstawowe informacje z paneli sterujących EcoSter

## EcoMax860P
Analizator potrafi odczytywać podstawowe informacje ze sterownika EcoMax860P

## Inne sterowniki
Kod analizatora został napisany modułowo tak, aby możliwe było proste dostosowanie go do potrzeb analizy innych sterowników z rodziny EcoNet. W tym celu należy skopiować odpowiedni plik np. ecoster860p.py, nadać mu własną nazwę i zaimplementować zdekodowane pola.

# Źródła danych
Obsługiwane źródła danych :
- plik ze zrzutem binarnym transmisji
- strumień sieciowy np. serial over telnet
- port szeregowy (nie testowane)

# Tips

## Zamiana liczby zmiennoprzecinkowej na bajty
Poszukując znaczenia danych możemy przeprowadzić analizę znanych wartości i wyszukiwać ich w ciągu bajtów. 
Na przykład: wiemy że zadana temperatura to **23,2** stopni celsjusza. Aby odnaleźć tą wartość zamieńmy ją na zmienną 4-bajtową typu float przy pomocy pythona, w konsoli:
```
python
import struct
struct.pack('f',23.2)
```
W wyniku otrzymujemy ciąg bajtów:
```
b'\x9a\x99\xb9A'
```
Teraz szukamy w dekodowanym strumeniu ciągu wartości **9A 99 9A** i dość łatwo dowiemy się na jakiej pozycji w ramce występuje ta wartość.
Uwaga: float to 4 bajty, więc możemy przetestować raz dobierając do analizy jeden bajt poprzedzający ciąg, a następnie bajt występujący po nim. Wyniki albo będą sensowne, albo pojawią się liczby nieużyteczne. W ten sposób ustalimy która czwórka bajtów jest właściwa.

## Zamiana ciągu 4 bajtów na liczbę zmiennoprzecinkową typu float
Na przykład: podejrzewamy, że ciąg bajtów **9A 99 B9 41** to liczba zmiennoprzecinkowa. Aby odczytać jej wartość dziesiętnie zamieńmy ją z ciągu 4-bajtów na liczbę typu float przy pomocy pythona, w konsoli:
```
python
import struct
struct.unpack('f',bytes([0x9A,0x99,0xB9,0x41]))
```
W wyniku otrzymujemy liczbę:
```
(23.200000762939453,)
```
Możemy również wpisać wartości dziesiętne:
```
struct.unpack('f',bytes([154,153,185,65]))
```




# Podziękowania
Niniejszy analizator nie powstałby bez pomocy użytkowników z forum elektroda.pl: wątek https://www.elektroda.pl/rtvforum/topic3346727.html

Podziękowania dla: cinas, coorass, domadm, kamka27, jamrjan, maslak, miszko, przemo_ns, SławekSS, webster21
