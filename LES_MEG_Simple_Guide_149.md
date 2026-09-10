# SIT 1.4.9 – enklere Quick guide

Leveranse: **SAIV_Instrument_Terminal_v1.4.9_Sept2026.exe**. Kunden trenger én EXE.

Help > Quick guide forklarer brukerens målinger, enheter og valg i SIT med korte tekster og regneeksempler. Guiden har 26 emner, inkludert betjening og GSW-lisens. Convert-knappenes konteksthjelp peker fortsatt til riktig måleemne.

System evaluation gir hjelp til å velge metode for egne data. Temperatur og OSU107 forklares ut fra kalibrering, registrerte verdier og hva brukeren skal kontrollere. Omtale av kodeanalyse, funn i programkode og utviklingshistorikk inngår ikke i brukertekstene. Detaljert formeldokumentasjon er bevart i prosjektet.

Beregninger, instrumentkommunikasjon og metodevalg er uendret. Programversjonen er 1.4.9; beregningsmetodenes identifikator beholdes. Tidligere leveranser og 1.4.8-kilden i `analysis/reference/sit_import_v148` er bevart.

Bygg: `analysis/build_single_exe_149.py`, med `C:\MinGW\bin` i PATH. Rediger guidens måleemner i `docs/SIT_CONVERSIONS_AND_FORMULAS.md`; generatoren lager programmets hjelpetekst.

Kontrollresultater: `analysis/simple_guide149_validation.json` og `analysis/runtime_test/guide149/gui_validation.json`. GUI-testen kontrollerer den ferdige en-EXE-utgaven, alle emnetekster, tastatur, rulling og lukking. Ingen instrumentkommandoer eller serverpublisering inngår.
