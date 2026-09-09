# SAIV Instrument Terminal 1.1.3

Start `SAIV_Instrument_Terminal_v1.1.3_Sept2026.exe`.

Programmet heter nå **SAIV Instrument Terminal**. Navnet er oppdatert i tittellinjen, About, Windows-filbeskrivelse og produktnavn, samt de eksisterende dialogtitlene som tidligere brukte MiniSoft-navnet. EXE-filen har også det nye navnet.

Det nye CTD-ikonet og eksisterende funksjoner er videreført. Registerplasseringen for brukerinnstillinger er beholdt slik at valgt COM-port og Show startup text følger med. Kreditering, disclaimer og tidligere leveranser er bevart.

Bygg: `python analysis/build_saiv_name.py`, med Python/pefile og bevart 1.1.2 som inngangsfil. Kontroll: `python analysis/check_saiv_name.py --live`. Den faktiske tittellinjen og About er kontrollert; disclaimer ble kontrollert uendret. Windows-versjonsressursen er lest tilbake med det nye navnet og versjon 1.1.3.

SHA-256: `60f8713bfeda9baffdb690e2bc0c2ff2f4e12516ceb1087b35257ec91b110035`.

Lokal leveranse, ikke publisert på GitHub.
