# COM-port uten CTS/DSR-flytkontroll

Program: SD200W_SAIV_OSU107_NoHandshake.exe
Utgangspunkt: SD200W_SAIV_OSU107_RefreshReply_EN.exe

Alle fire kall til SetCommState går gjennom en liten funksjon som slår av fOutxCtsFlow, fOutxDsrFlow og fDsrSensitivity. DTR/RTS, baudrate, paritet og øvrige innstillinger bevares. CTS/DSR i søkeresultatet viser fortsatt de faktiske inngangssignalene, og kan derfor vise on uten at programmet bruker dem som flytkontroll.

Verifisering:
- Ti emulerte kombinasjoner av flagg og lasteadresse bestått. Register, stakk, øvrige DCB-felt og alle fire kallsteder kontrollert. PE-sjekksum korrekt.
- Ny programkopi startet i Instrument-vinduet uten feildialoger. Setup med uendrede innstillinger lukket seg på ca. 31 ms ved OK.
- Separat fysisk vekketest på COM7 ved 9600 8N1, uten RTS/CTS- eller DSR/DTR-flytkontroll, ga instrumentets meny som svar.

Den rapporterte lange ventetiden ved OK er ikke gjenskapt. Målingen gjelder lukking av Setup med uendrede innstillinger, ikke fullføring av et portbytte. Denne utgaven inneholder ingen egen rettelse for en påvist forsinkelse.

Tidligere programkopier er bevart.
