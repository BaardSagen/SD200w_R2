# Last opp SIT 1.4.11

Last opp disse tre filene til `https://saiv.no/software/`, i denne rekkefølgen:

1. `saiv_instrument_terminal_v1.4.11_sept2026.zip`
2. `readme_v1.4.11.txt`
3. `latest.json` – last opp sist og erstatt serverens eksisterende fil.

Filnavn og URL-er bruker små bokstaver fordi serveropplastingen gjør navnene om til små bokstaver. Behold dem slik de står. `latest.json` gjør 1.4.11 synlig i Help > Update software og inneholder SHA-256 for ZIP-filen.

ZIP-filen inneholder det fysisk testede programmet `SAIV_Instrument_Terminal_v1.4.11_Sept2026.exe`, README.txt og lisensnotater. Brukeren trenger ingen separat DLL. Ny firmwaremeny ligger under Help > Firmware. Selve enhetsfirmwaren ligger fortsatt i sin egen firmwarekanal.

Pakken er oppdatert med skjult intern servicetrafikk og kundevendt filtrering av versjonsnotater. Full P-til-R-test bestod med skjult terminaltrafikk; den etterfølgende filtreringen av versjonsnotater ble kontrollert på den fysiske enheten uten ny flashing. ZIP-CRC, pakkeinnhold, kontrollsummer og EXE-versjon er kontrollert. Rapporter: `analysis/update_server1411_validation.json` og `analysis/firmware1411_validation.json`. Last opp alle tre filer på nytt dersom en tidligere 1.4.11-pakke allerede er lastet opp.

Tidligere pakker er beholdt. Den forrige pekeren er arkivert som `latest_v1.4.10.json`; den skal ikke lastes opp i stedet for `latest.json`. Dette instruksjonsnotatet trenger heller ikke lastes opp.

Pakken er laget lokalt. Ingen serveropplasting er utført av agenten.
