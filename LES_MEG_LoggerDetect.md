# Detect med OSU107 og SAIV110

Program: `SD200W_SAIV_OSU107_LoggerDetect.exe`

Bygger videre på `SD200W_SAIV_OSU107_Blue_ScrollLine.exe`. Tidligere programfiler er beholdt.

Detect kjenner igjen `OSU107 Instrument logger` og `SAIV110 Surface logger` i oppstartsteksten fra USB-porten. Delte tekstpakker og forskjeller i store/små bokstaver håndteres. Resultatet vises som OSU107 eller SAIV110, med samme grønne radmarkering som andre instrumentfunn. Funnet betyr at loggeren er identifisert; det sier ikke at en tilkoblet CTD er våken.

Søket venter ett sekund før portåpning, slik at en rask lukking/åpning ikke mister USB-hilsenen. Deretter leser det i inntil omtrent 1,5 sekunder før den gamle aktive søkemetoden brukes. Ved gjenkjent logger sendes ikke AT eller I fra denne søkefasen. Parallelle portsøk og rekkefølgen 9600 None, 9600 Even, 4800 None, 4800 Even er bevart. Baud/parity i listen viser portinnstillingen som ble brukt.

Dokumentasjonen i `osu107Doc/HANDOVER_2026-08-26_SURFACE_USB_DTR_SOFTWARE_INTEGRATION.md`, `USB_AUTODETECT_2026-09-07.md` og `SURFACE_TEST_2026-09-07.md` er kontrollert mot endringen. USB-hilsenen kan være deaktivert med `usbDtrInfo=never`, eller utebli under logging med `passive`. Denne gjenkjenningen forutsetter at hilsenen kommer innen lyttevinduet; ellers fortsetter det eksisterende aktive søket. Ingen loggerkonfigurasjon er endret.

Kontrollert 7. september 2026:

- Fysisk GUI-test fant SD200 på COM7 og SAIV110 på COM11 samtidig. COM18 fortsatte å søke uten falskt instrumentfunn.
- Skjermbilder bekrefter at bare instrumentradene er grønne, og at radene forblir synlige når utvalget endres.
- Ingen feildialoger ble observert under oppstart, søk og åpning/lukking av Setup.
- Maskinkodetester dekker begge loggertekstene, oppdelte pakker, små bokstaver, ukjent/stille port, resultatnavn og flyttet lasteadresse. Ingen søkekommandoer sendes i testtilfellene med gjenkjent logger.
- OSU107 er kontrollert med simulerte oppstartstekster, ikke med fysisk OSU107 i instrumentmodus.

Byggeskript: `analysis/build_logger_detect.py`. Maskinkode: `analysis/logger_detect.s`. Testresultater: `analysis/logger_detect_validation.json` og `analysis/runtime_test/SD200W_SAIV_OSU107_LoggerDetect.json`.

SHA-256: `d6b19b035415d159403113bed265f5b530b07819d7ab2aba08e0ad2b1b0c00bf`
