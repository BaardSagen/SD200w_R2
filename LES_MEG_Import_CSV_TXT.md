# SAIV Instrument Terminal 1.2.0 – Import CSV/TXT

Lokal leveranse 8. september 2026. Tidligere programversjoner er beholdt.

## Start og import

1. Legg `SAIV_Instrument_Terminal_v1.2.0_Sept2026.exe` og `SIT_Import.dll` i samme mappe. Begge må følge med til en annen PC. Python eller MinGW trengs ikke for å kjøre programmet.
2. Start denne EXE-filen og velg **File → Import CSV/TXT**. Filfilteret viser både `.csv` og `.txt`; den gamle Burst-støtten er beholdt.
3. OSU107/Surface-filer åpner feltvalg. Alle sensorfeltene presenteres etter tur. Originalverdiene beholdes. Par beholdes uendret. For OxR velges prosent, mg/L, mL/L eller begge konsentrasjonsenhetene.
4. Ved oksygenkonvertering brukes målt temperatur og salinitet, eller salinitet beregnet fra CTD. Manglende betingelser må oppgis. Lufttrykk leses fra AP-hodet når det finnes og kan kontrolleres i dialogen. Verdier brukeren oppgir merkes i eksporten.
5. Loggerdata vises i et eget datavindu i SIT med tabell og valgbar tidskurve. Bruk **Export all fields...** der for å lagre alle felt og metadata til en ny tekstfil. Eksisterende filer overskrives aldri. Lukk datavinduet for å gå tilbake til hovedvinduet.

## Det som er bevart

- Alle originale feltverdier, navn og tidspunkter i FIELDS-filene. Loggerens dato/tid og CTD-hodets dato/tid beholdes separat, uten skjult tidssonekorreksjon.
- De første 2–3 målingene kan ifølge brukeren være ute av synk før normal intervallrytme. Tidspunktene i filen beholdes også for disse målingene.
- CTD-resultater for salinitet, lydhastighet og tetthetsavvik beregnes med de eksisterende SIT-rutinene. Rå C/S/T/P og OF/OT beholdes. Nye sensorer forskyver ingen CTD-kolonner.
- Surface uten CTD får ikke oppdiktede CTD-verdier. OxR tolkes som oksygenmetning i prosent; normal import spør ikke om volt eller sensorkalibrering.
- APB5 uten nye loggerfelt går gjennom den gamle importen. Eksisterende SD2/RF2/OP2-åpning og kommunikasjonskode er ikke endret.

## Formater og avgrensning

Den nye grenen leser semikolonseparerte filer med `FIELDS:` og tilhørende `DATE`/`TIME`, samt Full-linjer med feltprefikser som `N`, `C`, `T`, `P`, `OF`, `OT`, `Par`, `OxR` og `Tilt`. CR, LF og blandede linjeskift støttes. Dette er støtte for SAIV-loggerfiler, ikke en generell import av vilkårlige regneark-CSVer.

Full er kontrollert med konstruerte eksempler; en faktisk Full-fil fra instrument er ennå ikke levert. Har Full-linjene egne tidspunkter, bevares de. Ellers kreves et eksplisitt loggerhode med dato/tid og intervall; beregnede tidspunkter merkes som **header-derived times**. Ukjent eller ugyldig radinnhold avvises. Nye loggerfiler har en grense på 20 MB, 200 000 målinger og 100 inngangsfelt.

Loggergrenen lagrer foreløpig et eget FIELDS-tekstformat, ikke SD2/RF2/OP2. Hovedvinduets gamle standarddybde-/profil-eksporter gjelder fortsatt de gamle datasettene. Loggerdataenes egen eksport beholder alle feltene og kan leses inn igjen. Det nye datavinduet er låst mot hovedvinduet mens det er åpent, slik at man ikke ved et uhell eksporterer et eldre datasett derfra.

## Kontroller

- 79 OSU107-rader og 3 Surface-rader importert og eksportert gjennom programvinduet.
- 483 kontroller av eksporterte originalverdier og beregnede resultater.
- 22 parser-, Full-, rundtur-, oksygen- og feilinputtester.
- 10 x86-tester av importgren, manglende DLL og flyttet programbase; registre og stakk bevares.
- Avbryt kontrollert. APB5 går fortsatt gjennom original import og gir 43 rader.
- Meny, filfilter, feltvalg, tabell og graf kontrollert i Windows. Formlenes maskinkode er byte-identisk med 1.1.3.

Testkilder og rapporter finnes i `analysis/check_logger_*.py` og `analysis/runtime_test/logger_*validation.json`. Originalfilene i `data` er ikke endret.

## Bygg og videre arbeid

Ny kildekode ligger i `sit_import/logger.h`, `sit_import/sit_import.cpp` og `sit_import/import_hook.s`. Dette er en C++/Win32-utvidelse til den opprinnelige Delphi-EXE-en; original Delphi-kildekode finnes fortsatt ikke i prosjektet. ImGui-prosjektet er fortsatt på pause.

Bygg fra prosjektroten med `python analysis/build_logger_import.py`. Det krever Python med `pefile`, GNU `as`/`ld`/`objcopy` og en 32-bits MinGW-kompilator med C++11. Det kontrollerte miljøet bruker MinGW GCC 6.3.0. Bygget kontrollerer hash på den bevarte 1.1.3-filen før patching. MinGW C++-kjøretid er statisk lenket; DLL-en avhenger bare av Windows-DLL-er. Lasting skjer fra mappen til SIT-programmet, uavhengig av arbeidsmappe.

Se `sd200DOc/PROSJEKTSTATUS.md`, `OPPSTART_NY_PC.md` og `analysis/logger_import_manifest.json`. Leveransen er lokal; ingen GitHub-push er gjort i denne oppgaven.

## SHA-256

EXE: `870829d01389f700ac0526933e18c5f21cf393d45254bfa479314127c2e70e0b`

DLL: `323a7a978866105597b124f71b2618d1d5cdb1074d5bdbbfc09fd6ac02d6da28`
