# SAIV Instrument Terminal 1.3.7 - Import til SD2

Arbeidet ligger paa `feature/import-all-fields`. Main beholder bekreftet 1.3.6; denne grenen inkluderer rettingene derfra. Brukeren har fysisk bekreftet at Download-rettingen i 1.3.6 fungerer.

Kunden trenger bare `SAIV_Instrument_Terminal_v1.3.7_Sept2026.exe`. Automatisk oppsett av innebygd runtime/DLL uten administratorrettigheter viderefores.

## Bruk

- File > Import CSV/TXT leser FIELDS-filer, Convert-resultater og Merge-filer. Den gamle ASCII-importen beholdes for eldre instrumenttekst.
- Velg navn paa det nye SD2-datasettet. Standardmappe er kildens mappe. Eksisterende datasett overskrives ikke.
- Datasettet aapnes i programmet, og alle feltene vises i datalisten. Bruk de vanlige grafknappene/menyene eller Multigraph. Grafene for importerte data bruker programmets eksisterende Delphi Multigraph-komponent, med feltvalg lagt til. Vanlige grafmenyer velger ett/to relevante felt; Multigraph viser opptil ti felt samtidig. Alle numeriske felt kan velges, ogsaa M1_/M2_-felter og tellere.
- Import to SD2... ved siden av Export all fields i Convert bruker samme importvei. Den tar med allerede valgte kolonner, konverteringer og enheter, uten aa kjoere konverteringsveiviseren om igjen.
- File > Open aapner lagrede SD2-datasett igjen med de samme tilleggsfeltene.

## Filer som hoerer sammen

SD2 inneholder den vanlige native instrumentrepresentasjonen; RF2 inneholder referanseinformasjon. OX2 og OP2 lages naar tilsvarende originale OX/OF/OT-felt finnes. **SF2 er den nye tilleggsfilen som bevarer alle kildefelt, tomme verdier, metadata og fulle tidsstempler. Behold filene med samme navn samlet i samme mappe.** SF2 inneholder ogsaa en kontrollverdi mot SD2 for aa oppdage feil sammenkobling/endret SD2.

PAR, OxR, Tilt og merge-felt blir ikke omdoept til andre sensorer. Kildeteksten bevares i SF2. FIELDS-separatorer og ekstra DATE/TIME-kolonner vises i listen og behandles ikke som numeriske grafkanaler. Merge-felt plottes mot masterens radtider.

Grafens tidskoordinater kommer fra hver enkelt rad, inkludert brudd i intervallet og desimalsekunder. Trykk vises som dbar og Depth_m som meter. Dybde/trykkvalget er deaktivert naar slike felt mangler. Manglende maaleverdier bevares som tomme/nullpunkter.

For CTD/STD bygges vanlig SD2 med S/C/T/P/lydhastighet der verdiene finnes eller kan beregnes. Manglende native salinitet, lydhastighet og tetthetsavvik beregnes med originale SIT-rutiner. Eksisterende konverterte verdier beholdes. Native Celsius kan rekonstrueres fra Fahrenheit for SD2-representasjonen; valgt T_degF vises fortsatt uendret i feltlisten/grafvalgene. Det gjettes ikke temperatur, salinitet eller lufttrykk for loggerfiler som mangler disse.

Native datointervall: 1981-2079 (1980 er en reservert datomarkoer i originalleseren). Maksimalt 20 MB kildetekst, 100 felt og 200000 rader. Dette er import/visning, ikke synkronisering av de gamle redigeringsverktoeyene med SF2: ved senere endring av SD2 maa kilden importeres paa nytt for aa opprette et samsvarende komplett datasett.

## Verifisering

Alle tre oppgitte filer er importert gjennom faktisk enkelt-EXE, aapnet igjen fra SD2 og kontrollert mot native grafens punktarrayer og eksporterte lister:

- 2026_09_03_20-28-52_C.txt: 79 rader, tidsakse 0-158 sekunder med 4 sekunder mellom de foerste radene.
- 2026_09_07_19-34-42_C.txt: 3 rader med PAR/OxR/Tilt, tidsakse 0/5/10 sekunder.
- 2026_09_03_20-28-52_C_merged-3.txt: 79 rader, master- og M1-felt, feltbytte og tellere.

Rapporter: analysis/native137_release_validation.json, analysis/runtime_test/import137/native137_gui_validation.json, analysis/runtime_test/fahrenheit137/gui_validation.json, analysis/native137_hook_validation.json. Legacy-eksemplet med 43 maalinger gir SD2/RF2/OX2/OP2 byteidentiske med originalimporten. Convert/Fahrenheit/preset-regresjon og direkte Convert-import er kontrollert. Native bro er kontrollert med flyttet image base. Beregnings-, UART- og Download-kode er uendret.

Skjermopptak var svarte/utilgjengelige i denne Windows-oekten. GUI-kontrollen leser faktiske vinduer, kontroller og native grafverdier; visuell kontroll paa brukerens skjerm gjenstaar. Ingen ny fysisk instrumenttest var noedvendig for importarbeidet.

Bygg: analysis/build_single_exe_137.py fra hashbundet analysis/single136/SAIV_IT_Runtime.exe. Kilder: sit_import/native_data.h, native_ui.inc, native_call.s, native137.s og analysis/patch_native137.py. 1.3.6-kildene er bevart i analysis/reference/sit_import_v136 og sit_single_v136. Tidligere leveranser beholdt. Ingen push til GitHub.
