# SAIV Instrument Terminal 1.3.0 – Merge

Lokal leveranse 8. september 2026. Pakk ut hele **SAIV_IT_v1.3.0_portable.zip** og start **SAIV_Instrument_Terminal_v1.3.0_Sept2026.exe**. **SIT_Import130.dll må ligge i samme mappe som EXE-filen.** Eldre leveranser er beholdt.

## Slik bruker du Merge

1. Trykk **Merge**, rett under Import i terminalen.
2. Velg en CSV/TXT-fil som **Master file**. Masterfilen bestemmer radene og tidspunktene i resultatet.
3. Velg mappen som inneholder de andre CSV/TXT-filene. Du kan bruke Browse eller lime inn mappebanen.
4. Sett **Time tolerance** fra **0.0 til 10.0 sekunder**. Standard er 0.0, altså nøyaktig lik dato og tid. Både punktum og komma godtas i toleransefeltet.
5. Trykk **Scan folder**. Listen viser bare filer med minst ett treff, med første/siste måling, antall masterrader med treff, filens radantall og største absolutte tidsavvik. Skanningen gjelder valgt mappe, ikke undermapper. Uleselige/ugyldige filer beskrives i feltet under listen.
6. Huk av **én eller to tilleggsfiler**. Masterfilen kommer i tillegg, slik at resultatet kan inneholde data fra tre filer totalt.
7. Velg eventuelt **Add '-' separator column between files**. Denne haken er **av som standard**. Filen bruker alltid semikolon mellom kolonner; haken legger til en egen kolonne med `-` ved hvert filskille.
8. Trykk **Merge files**, og velg et nytt filnavn. Resultatet lagres som CSV/TXT med semikolon og UTF-8. Ingen inngangsfiler eller eksisterende resultatfiler overskrives.

Skanningen kjører i bakgrunnen og kan avbrytes. Endres masterfil, mappe eller toleranse i dialogen, må du skanne på nytt. Endres filinnholdet på disk etter skanning, avvises sammenslåingen til filene er skannet på nytt.

## Hvordan målingene kobles

- Sammenligningen bruker **dato og tid i hver målerad**, ikke filnavn eller Windows-filens dato. Brøkdeler av sekunder støttes med mikrosekundpresisjon.
- **Nærmeste tidspunkt innenfor toleransen** velges uavhengig fra hver tilleggsfil. Grensen er inklusiv: nøyaktig 10.0 sekunder godtas ved 10.0, mens 10.1 ikke godtas.
- Ulik starttid, ulikt intervall og ulikt antall rader er tillatt. Målinger kan også kobles over midnatt dersom de fullstendige dato-/tidspunktene ligger innenfor toleransen.
- Ved lik avstand velges det tidligste tidspunktet. Finnes flere rader med akkurat dette tidspunktet, brukes den første av dem i tilleggsfilen.
- **En rad fra tilleggsfilen kan brukes for flere masterrader.** Det passer med masterfilen som fast tidsakse når instrumentene måler med ulik frekvens. Antallet «Master matches» er derfor ikke nødvendigvis antallet forskjellige rader som brukes fra tilleggsfilen.
- Alle masterrader beholdes i opprinnelig rekkefølge. Uten treff blir tilleggsfilens felter tomme. De tomme feltene betyr manglende treff, ikke verdien null.
- Det gjøres ingen interpolering, utjevning, sensoromregning eller endring av råverdier. Klokkene må være sammenlignbare; programmet foretar ingen tidssonejustering.

Tilleggskolonnene får prefiks **M1_** og **M2_** slik at for eksempel masterens Par ikke forveksles med SAIV110s Par. Også tilleggsfilenes originale COUNT/DATE/TIME beholdes. **M1_Delta_seconds** og **M2_Delta_seconds** viser tilleggsfilens tidspunkt minus masterens tidspunkt. Filhodet inneholder kildefilene, toleransen, koblingsreglene, treffantall og opprinnelige headere.

## Filformater

Merge leser SAIVs `FIELDS:`-filer og vanlige tabeller med semikolon, komma eller tabulator som kolonneseparator. Vanlige tabeller trenger separate **DATE/TIME**-kolonner (også Date/Time eller DATO/TID), med dato `YYYY-MM-DD` og klokke `HH:MM:SS` eller `HH:MM:SS.fraction`. Numeriske og tekstlige målefelt beholdes. Siterte CSV-felter og doble anførselstegn støttes, men ikke linjeskift inne i siterte celler.

Full-format kan brukes når hver rad har eksplisitt dato og tid. Merge gjetter ikke tidspunkt fra filnavn eller starttid/intervall. Filer med ugyldig radtid avvises med forklaring; slike rader slettes ikke i stillhet. Grensene er 20 MB, 200000 rader og 400 felt per inngangsfil.

Merge-resultatet kan leses igjen av Merge eller brukes som semikolonseparert tekst i andre verktøy. Det åpnes ikke automatisk i den gamle graf-/importdelen: den er ikke utvidet til de nye M1_/M2_-dato- og tekstkolonnene. Importkonverteringene fra 1.2.2 finnes fortsatt separat; se LES_MEG_Import_122.md og LES_MEG_Import_121.md.

## Testfiler som følger pakken

Velg **data/2026_09_03_20-28-52_C.txt** som master og **data/saiv110** som mappe. Masteren har 79 rader. Det ligger 12 tydelig merkede **syntetiske** SAIV110-filer der, basert på formatet i data/2026_09_07_19-34-42_C.txt. Originalene er urørt.

Seriene starter før eller etter masteren, har få eller mange rader, ulike intervaller, halve sekunder, 5/10/10.1 sekunders grenseavvik og feil dato. Den lengste har 1000 rader. Se data/saiv110/LES_MEG.md og fixtures.json.

Forventet treffliste ved denne masteren:

| Toleranse | Filer med treff |
|---|---:|
| 0.0 s | 4 |
| 0.5 s | 6 |
| 10.0 s | 8 |

Testverdiene er kunstige og skal ikke behandles som virkelige SAIV110-målinger.

## Verifikasjon og videre utvikling

- 9679 kontroller mot en uavhengig tids-/verdifasit, med alle testfilene, tilfeldige serier, midnatt, brøkdeler, doble tidspunkter, lik avstand, manglende treff, tekstverdier og begge skillevalg.
- 4108 kontroller av verdiene i filer lagret gjennom selve Windows-dialogen.
- Windows-test av Merge-knapp, fil- og mappevelger, trefflister ved 0/0.5/10 sekunder, sperre mot tredje fil, begge skillevalg, avbryt skanning, ugyldig toleranse, overskrivingsvern og endret masterfil.
- Den portable ZIP-pakken er pakket ut i en annen mappe og startet derfra. EXE/DLL, Merge-knappen og de medfølgende testfilene fungerer; skanningen finner seks filer ved 0.5 sekunder.
- Dialogen er kontrollert visuelt. Skjermbilde: analysis/runtime_test/merge130/merge_printwindow.png.
- 16 tester av Merge-hendelsens maskinkode, registre/stakk, adresseflytting og DLL-cache; 10 tilsvarende tester av eksisterende importkobling.
- Eksisterende import er kontrollert gjennom Windows med OSU107, SAIV110 og fullstendige syntetiske CTD-data; alle 1430 verdikontroller bestod. De opprinnelige CTD-formelbytene er uendret.

Kilde: sit_import/merge.h, merge_ui.inc, sit_import.cpp og import_hook_130.s. Bygg fra prosjektroten med **python analysis/build_logger_import_130.py**. Krever Python/pefile og 32-bits MinGW GCC med as/ld/objcopy. Kjøring krever bare Windows og de to programfilene. Bygget bruker den bevarte 1.1.3-EXE-en; original Delphi-kildekode er fortsatt ikke tilgjengelig. 1.2.2-kilden er arkivert i analysis/reference/sit_import_v122, og dens byggskript peker dit.

Det eksisterende dokumentet **docs/merge_filer_dato_tid.md** beskriver en annen implementasjon: 0.1–30 sekunder, engangsbruk av sekundærrader og bare sammenkoblede rader i eksport. Det er bevart uendret. Denne SIT-leveransen følger den nye bestillingen om mappeskanning, opptil to tilleggsfiler og 0.0–10.0 sekunder, med masterbasert nærmeste-tid-kobling som beskrevet over.

Ingen GitHub-push er utført. Build-manifestet analysis/logger_import_130_manifest.json inneholder EXE- og DLL-hashene.
