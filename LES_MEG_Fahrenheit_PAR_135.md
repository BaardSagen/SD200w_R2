# SAIV Instrument Terminal 1.3.5 - Fahrenheit og PAR-enhet

Leveranse 9. september 2026: **SAIV_Instrument_Terminal_v1.3.5_Sept2026.exe**. Fortsatt en EXE til kunden, med automatisk oppsett av innebygde komponenter uten admin.

## Temperatur i Convert

T-siden har naa to valg:

- Keep temperature (Celsius).
- Convert temperature to Fahrenheit.

Fahrenheit beregnes som **F = C * 9/5 + 32** og faar egen kolonne **T_degF**, merket Fahrenheit/degF i datavindu og graf. Haken **Keep original T values (Celsius)** bestemmer om den opprinnelige T-kolonnen beholdes. Standard er fortsatt Celsius og behold originalverdier. Med Fahrenheit og haken paa eksporteres begge. Med haken av eksporteres bare Fahrenheit-kolonnen for temperatur. Tomme temperaturceller blir tomme Fahrenheit-celler.

Salinitet, lydhastighet, tetthet, dybde og oksygenberegninger bruker fortsatt de opprinnelige Celsius-verdiene. Fahrenheit-kolonnen legges til etter selve sensorberegningene, og originalkolonner fjernes til slutt. De opprinnelige CTD-rutinene i EXE-en er byte-identiske med de bevarte SD200W-rutinene i 1.1.3.

Fahrenheit-valget huskes sammen med de andre konverteringsvalgene. Historikk fra 1.3.4 kan fortsatt leses og betyr Celsius som tidligere. For aa endre et tidligere lagret Celsius-valg, velg Nei i gjenbruksdialogen og velg Fahrenheit paa T-siden.

## PAR

Etter **Photosynthetically Active Radiation** staar naa den konverterte ut-enheten **micromol photons/(m2*s)**, vist med mikro-, kvadrat- og prikktegn i programmet. Den er merket **output**. Valget av faktisk inngangsenhet per m2 eller cm2 er beholdt og maa fortsatt angis naar PAR konverteres. Ingen ny arealfaktor er antatt.

## Tester

- 35 tester av Fahrenheit (-40, 0, 100 og 23 Celsius), tomme celler, behold/utelat original, av/paa, uendrede sensorberegningskall og lesing av 1.3.4-historikk.
- 263 tester av signatur, lagringsformat, ugyldig historikk og nye konverteringsbetingelser.
- 2054 GUI-verdikontroller fra den leverte en-EXE-filen. Celsius, begge temperaturkolonner, Fahrenheit alene, gjenbruk etter omstart og bytte tilbake til Celsius bestod. Alle andre eksportverdier er identiske.
- Temperaturgrafens enhet og PAR-teksten er kontrollert. Bilder: analysis/runtime_test/fahrenheit135/temperature_fahrenheit.png og par_unit.png.
- CTD-formelomraadet RVA 0x10A000-0x10CFFF er byte-identisk med 1.1.3. Automatisk oppstarter/runtime kjorte uten elevasjon. Ingen ny fysisk instrumenttest eller GitHub-push.

Rapporter: analysis/fahrenheit_validation.json og analysis/runtime_test/fahrenheit135/gui_validation.json.

## Bygg

**python analysis/build_single_exe_135.py**. Innebygd DLL: SIT_Import135.dll. Runtime bygger paa bevart 1.3.2 med versjonsressurser og DLL-navn oppdatert. Kilde til 1.3.4 er bevart i analysis/reference/sit_import_v134 og sit_single_v134, og det eldre byggskriptet peker dit. Tidligere leveranser beholdes.

Choices har et nytt Fahrenheit-flagg. Lagringsformat SIT choices 2 lagrer flagget og leser fortsatt SIT choices 1. Signatur og registerplassering er uendret. Dette er en utvidelse av utdata; den eksisterende sensorberegningen er bevart.
