# Syntetiske SAIV110-testfiler

Alle filer er merket SYNTHETIC TEST DATA. Sensorverdiene er kunstige og bygger på formatet i 2026_09_07_19-34-42_C.txt. Originalfilene er urørt.

Master: ../2026_09_03_20-28-52_C.txt (OSU107, 79 rader, 20:28:52–20:31:30 den 3. september 2026).

01 starter fem minutter før og fortsetter etter master. 02 starter ett minutt etter. 03 har fire eksakte treff. 04 har halvt sekund avvik. 05 og 06 ligger henholdsvis 5 og 10 sekunder før første masterrad. 07 ligger 10,1 sekunder før og skal aldri matche ved tillatt toleranse. 08 har feil dato. 09 slutter lenge før. 10 starter lenge etter. 11 har noen få rader mot slutten. 12 har 1000 rader med 0,5 sekund intervall og starter to minutter før.

fixtures.json inneholder start, intervall og radantall. Regenerer med analysis/generate_saiv110_fixtures.py.
