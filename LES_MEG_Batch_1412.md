# SIT 1.4.12 – konverter flere filer

26. oktober 2026. Program: **SAIV_Instrument_Terminal_v1.4.12_Oct2026.exe**.
Kunden trenger fortsatt bare én EXE.

## Bruk

1. Klikk **Convert**, eller bruk konverteringsvalget i File-menyen.
2. Velg flere TXT/CSV-filer med **Ctrl** eller **Shift**, og velg Open.
3. Velg mappen der resultatene skal lagres.
4. Velg beregninger, enheter og originalkolonner for første fil. De samme
   valgene brukes automatisk på de neste filene med samme instrumenttype og
   kolonneoppsett. Et annet oppsett får sine egne valg.
5. Følg fremdriften i eget vindu. Hver fil får en egen `_SIT.txt`-utfil.

Originalene beholdes. Eksisterende utfiler overskrives ikke; det nye navnet får
nummer, for eksempel `_SIT_2.txt`. Feil listes per fil, og de øvrige filene
behandles videre. **Cancel remaining** stopper videre behandling etter at
arbeid som allerede er startet, er avsluttet. Ferdige utfiler beholdes.

GPS og manglende temperatur, salinitet eller lufttrykk etterspørres separat
for den aktuelle filen når beregningene trenger det. Slike støtteverdier fra
første fil brukes ikke automatisk for de neste filene.

Når bare én fil velges, brukes det eksisterende resultatvinduet med tabell,
kurve, **Export all fields** og **Import to SD2**. Flere filer gir separate
teksteksporter; de blir ikke automatisk slått sammen eller importert til SD2.
Quick guide i programmet er oppdatert.

## Intern bygg- og testinformasjon

Bygg: `analysis/build_single_exe_1412.py`. Intern modul: `SIT_Import152.dll`.
Startgrunnlaget er den verifiserte 1.4.11-runtime med SHA-256
`cd379866e627015607288414a95b68c300183526d850511ffb063b214c72b617`.
1.4.11-kilden er bevart under `analysis/reference/sit_import_v1411`, og det
historiske byggskriptet bruker dette arkivet. Tidligere EXE-er beholdes.

Beregningskilder og firmwarekilder er uendret. Bakgrunnstrådene overtar
Delphi-trådens x87-presisjon og avrundingsmodus, slik at eksisterende
beregninger får samme avrunding som ved enkeltfilkonvertering.

Kontroller: `analysis/check_batch1412.py` og `analysis/validate_batch1412.py`.
GUI-testene bruker egne programkopier på privat skrivebord, blokkerer fysisk
serieportåpning og erstatter registertilgang med minnestubber i testkopiene.
Kundedataene leses fra `data/dataFormCoustomer`; testresultater legges under
`analysis/runtime_test/batch1412`. Detaljrapporten der dokumenterer
samlekonvertering av de 15 kundefilene, sammenligning med individuelle
1.4.11-eksporter, eksisterende utfiler, enkeltfilflyt, ugyldig fil, avbrudd
og nye spørsmål om manglende betingelser. Originalfilenes SHA-256 kontrolleres.

Statisk kontroll: `analysis/batch1412_static_validation.json`. Kunde-EXE-en
inneholder nøyaktig de kontrollerte modulene. Den bevarte Delphi-runtime er
kun endret ved Convert-inngangen, DLL-navnet, versjon/About og nødvendige
PE-størrelser/kontrollsum. Ingen instrumentoperasjon er nødvendig for testen.

Utgaven er foreløpig usignert; kodesignering avventer SAIVs Azure-oppsett.
Ingen serverpublisering, commit eller push er utført for denne endringen.
