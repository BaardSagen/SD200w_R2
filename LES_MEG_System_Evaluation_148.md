# SIT 1.4.8 – enkel systemvurdering i Quick guide

Leveranse: **SAIV_Instrument_Terminal_v1.4.8_Sept2026.exe**. Kunden trenger én EXE. 1.4.7 og tidligere leveranser er bevart.

Help > Quick guide har to nye emner:

- **System evaluation**: en kort anbefaling på under 600 engelske ord for lesere uten spesialkunnskap. Forklarer hva PSS-78, EOS-80 og TEOS-10 gjør, når de ulike valgene er nyttige, CTD kontra STD og gammel/ny temperaturkalibrering.
- **System: measurement quality**: begrunnelse, eksempler og begrensninger for hele kjeden, inkludert trykk/dybde, tetthet, lyd, oksygen på store dyp, OSU107 OX/PAR, turbiditet, fluorescens og PAR.

Start here viser til vurderingen. De detaljerte parameteremnene er bevart. Formlene og metodevalgene i Convert er uendret fra 1.4.7; eksportens metodeidentifikator beholder derfor 1.4.7. Programversjonen er 1.4.8.

## Kildegrunnlag og kvalitet

Vurderingen skiller mellom kalibrering, oppløsning, tekstavrunding og modellvalg. Den nye SD208-rapporten viser samme PSS-78-polynomfamilie som SIT, men små konstant- og grenseforskjeller. Fire numeriske salinitetssammenligninger og 60 lydhastighetssammenligninger mot rapportens Python-referanse er kontrollert. Dette er ikke fysisk instrumentvalidering eller en ny inspeksjon av assemblykoden rapporten bygger på.

Temperaturens tre/fire koeffisienter, Kelvin-konstanten 273,16/273,15 og ITS-90/IPTS-68 behandles som tre forskjellige spørsmål. Et bestemt årstall for overgang mellom instrumentversjoner er ikke dokumentert.

OSU107 har separat analog målekjede for OX/PAR. Handover-notatene dokumenterer ADS1263, referansesjekk, oppvarming og konfigurerbare desimaler, men gir ikke en komplett, sammenlignbar usikkerhet for ferdig kanal. Brukerens opplysning om lavere nøyaktighet er derfor ikke omgjort til en udokumentert tallfestet spesifikasjon. Digitalt mottatte CTD-verdier går ikke gjennom denne analoge kjeden.

Interne kilder:

- asmCTDdoc/sd208-beregninger-og-drift.md og sd208-calculations-reference.py.
- osu107Doc/HANDOVER_2026-07-09.md: ADS1263/ADR4525, referansekontroll, kalibrering og oppvarming.
- osu107Doc/HANDOVER_2026-08-20_SOFTWARE_INTEGRATION.md: ADC-felter, enheter og desimaler.
- osu107Doc/HANDOVER_2026-08-28_INTERVAL_POWER_PREHEAT.md: måleintervall og oppvarming.
- Tidligere rekonstruerte SIT-formler og tester, dokumentert i FORMELKARTLEGGING/FORMELKONTROLL.

Offentlige kilder er lenket i guiden: TEOS-10/GSW, UNESCOs eldre algoritmer og TI ADS1263. Eksemplene oppgir ikke målefil, sted eller installasjon.

## Bygg og verifikasjon

Bygg med analysis/build_single_exe_148.py og C:\MinGW\bin i PATH. Historisk 1.4.7-kilde ligger i analysis/reference/sit_import_v147; byggskriptet for 1.4.7 bruker dette arkivet. Native runtime kontrolleres byte for byte utenom versjon/About/DLL-navn.

analysis/verify_system_evaluation148.py kontrollerer eksemplene, anonymisering, lengden på sammendraget og at endringene i importmodulen bare gjelder hjelpetekst og programversjon. analysis/check_formula_guide148_gui.py kontrollerer alle 33 emner i den leverte EXE-filen, full tekst, rulling, tastatur og lukking. Resultater lagres under analysis/system_evaluation148_validation.json og analysis/runtime_test/guide148/gui_validation.json.

Ingen instrumentkommunikasjon eller publisering inngår i denne leveransen.
