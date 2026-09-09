# Import all fields - 1.3.7

Arbeidet er gjenopptatt og utvidet etter brukerens nye beskjed: begge _C-filer og _merged-3 skal inn via Import CSV/TXT og vises i vanlige grafer/multigraph. Samme backend brukes naa direkte fra Convert via Import to SD2. De tidligere avgrensningene under er historikk.

Se [LES_MEG_Import_All_Fields_137.md](../LES_MEG_Import_All_Fields_137.md) og [PROSJEKTSTATUS.md](PROSJEKTSTATUS.md) for implementasjon, tester og begrensninger. Presis radtid, ekstra felt, gjenapning og native grafintegrasjon er implementert. Main 1.3.6 er committet; utviklingen ligger paa feature/import-all-fields.

## Historisk checkpoint fra foer gjenopptakelsen

# Import all fields – utvikling

9. september 2026. Gren: feature/import-all-fields. Siste leveranse fortsatt 1.3.5.

## Status: PAUSED

Import all fields er satt på pause etter brukerens beskjed. Omfanget er bare Convert-resultater, ikke Merge. Leveransen frem til 1.3.5 er sikret på main i commit d219703. Denne grenen bevarer den uferdige prøven separat; ingen ny importfunksjon er levert.

## Avklart omfang

Brukeren presiserte: bare filer som blir konvertert, ikke Merge-filer. Tilleggsfelt fra Convert inngår fortsatt. Målet er en knapp ved siden av Export all fields, med lagring i programmets datasett og bruk av eksisterende grafer og datalister. Valgte kolonner og enheter skal respekteres.

Ingen ny kundeleveranse eller Import all fields-knapp er ferdig. Ingen produktkilde er endret i denne prøven.

## Kontrollert interoperabilitetsprøve

analysis/probe_convert_sd2.py lager et nytt testdatasett fra en tidligere kontrollert Convert-eksport. Originaltekst med alle felt bevares byteidentisk i testmappen. CTD-projeksjonen skrives som SD2/RF2, OF som OP2. Salinitet beregnes for denne interne prøven med den tidligere kontrollerte rekonstruksjonen av originalrutinen.

analysis/check_native_convert_probe.py --live åpnet filen i faktisk 1.3.5-runtimekode, i egen testkopi/prosess med serieportåpning deaktivert. 79 rader og 395 CTD-tall ble lest nøyaktig som skrevet. Native graf åpnet. Ekstra felt er bevart i originalteksten, men ennå ikke integrert i gamle grafer/lister.

Resultatmappe: analysis/runtime_test/native_convert/1788948065716656600/
native_graph.png er kontrollert visuelt. Første prøve med referanseintervall 0 ga programmets standard 0,2 sekunder. Ny prøve med eksplisitt intervall 2 ga grafakse 156 sekunder for 79 rader, mens faktiske radtider går fra 20:28:52 til 20:31:30, altså 158 sekunder. Første intervall er 4 sekunder, resten 2. Grafen bruker nominelt intervall og representerer fortsatt ikke loggerfilen korrekt.

gui_validation.json dokumenterer verdiinnlesing og åpnet graf, ikke korrekt tidsakse eller ferdig full import. Testskriptet er en avgrenset prøve for denne filen, ikke en generell SD2-skriver.

## Formatfunn og gjenstående arbeid

- Undersøkte SD2-versjon 12-eksempler har 52 byte hode og 52 byte per rad: dato/tid, intervall, målenummer og fem double-verdier S/C/T/P/lydhastighet.
- RF2-eksemplene har 72 byte per referansepost og lufttrykk som float i mmHg, ikke hPa. OP2 har to float-verdier per rad.
- Native radtidsleser 0x0045A77C leser år/måned/dag/time/minutt/hele sekunder. Tideler trenger ekstra lagring og riktig tidsakse.
- Alle valgte Convert-felt, tidspunkter, tomme verdier, enheter og metadata må bevares. Ingen stille omdøping av PAR/Tilt til OF/OT. Utvidet lagring og native kanalvalg/dataliste gjenstår.
- Riktig instrumentbeskrivelse/tidssone, trykk kontra dybde og Celsius kontra Fahrenheit må håndteres. Prøvens instrumentmodus er bare et kontrollert teknisk testvalg.
- Endelig GUI-flyt, lagring, gjenåpning og regresjon mot ordinære SD200-filer gjenstår. Ingen sensorkonvertering skal gjentas på ferdig konverterte verdier.

## Bevaring

1.3.5-kilder er bevart i analysis/reference/import_all_fields_baseline_135/ med hashmanifest. Kopiert byggskript er referanse; relative stier er ikke tilpasset arkivmappen. Tidligere leveranser er urørt. Eksisterende ucommittede/usporede filer ligger fortsatt i arbeidsmappen; grenopprettelsen alene sikrer ikke disse.

Native inngangspunkter: Open 0x005A09F4, filinnlesing 0x00590710, kanalflagg 0x0045B33C, hovedvinduoppdatering 0x0059BEE8, listevalg 0x005A0F40. Grafkomponent TChartMH. Utdrag i analysis/native_*.txt. Image base 0x00400000, bruk RVA ved flyttet innlasting. Ingen push eller fysisk instrumenttest.
