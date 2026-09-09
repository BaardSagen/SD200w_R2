# SAIV Instrument Terminal 1.2.2

Lokal leveranse 8. september 2026. Pakk ut hele `SAIV_IT_v1.2.2_portable.zip` og start `SAIV_Instrument_Terminal_v1.2.2_Sept2026.exe`. `SIT_Import122.dll` må ligge i samme mappe. Windows er tilstrekkelig for kjøring; Python og kompilator trengs bare ved videre utvikling.

## Endringer

- **Import** ligger direkte under **Download** i terminalen og åpner samme **Import CSV/TXT** som File-menyen. Log/Print/Setup er flyttet litt for å gi plass.
- På **T – Temperature**-siden finnes **Calculate sound velocity (m/s)** når filen har fullstendige T/P og salinitet eller C som kan konverteres. Haken er på som standard. Fjern den for å utelate den nye beregnede lydhastighetskolonnen. Beregningen bruker fortsatt original SIT. En eventuell lydhastighetskolonne som allerede finnes i inngangsfilen styres av sitt eget Keep original-valg.
- GPS er valgfritt. **45,508368287°** er reservebreddegraden fra original SIT, brukt til gravitasjon i dybdeberegningen. Den er ikke en målt GPS-posisjon og gir ingen GPS-posisjonslinje i eksporten uten GPS-valg. Koordinatparet `60.3936119227684, 5.29588169849683` er brukerens eksempel på Google Maps-format, ikke en automatisk standardposisjon.
- Den nye loggerimporten spør etter manglende salinitet ved konverteringer som krever den. Den setter ikke automatisk 35. Originalprogrammets eldre reserveverdier er en separat mekanisme (35 i tetthetswrapperen og 34,5 i oksygenwrapperen under respektive manglende-salinitet-flagg).

Øvrige feltvalg, GPS/Paste, enheter og begrensninger er beskrevet i `LES_MEG_Import_121.md`, som følger pakken. Loggerdata har fremdeles eget datavindu og FIELDS-teksteksport; de gamle SD2/RF2/OP2- og standarddybdeeksportene er ikke utvidet til loggergrenen.

## Kontroll og videre utvikling

Windows-testen bruker den nye Import-knappen med OSU107 (79 rader), Surface (3 rader) og syntetiske fullstendige CTD-data (3 rader). Lydhastighet er kontrollert som på som standard og med/uten eksportkolonne. 1430 verdikontroller og 10 maskinkode-/relokeringstester bestod. Opprinnelige CTD-formelbytes er uendret. Ingen ny test mot fysiske instrumenter var nødvendig for disse importendringene.

Bygg: `python analysis/build_logger_import_122.py`. Krever Python/pefile og 32-bits MinGW GCC med as/ld/objcopy. Kilde: `sit_import/`. Bygggrunnlag er den bevarte 1.1.3-EXE-en. 1.2.1-kilden er arkivert i `analysis/reference/sit_import_v121/`, og byggskriptet for 1.2.1 peker på arkivet. Tidligere leveranser er beholdt. Rapporter: `analysis/runtime_test/import122/` og `analysis/runtime_test/logger_hook_122_validation.json`. Ingen GitHub-push er utført.

## SHA-256

EXE: `41745a57982a84749479dbd71fa97c222420bce21634ae07de506c7e1d1ad64a`

DLL: `9a3a1cd506e2ba00c5eeb51d086ce731d3679e66774f84699098551961c0264e`
