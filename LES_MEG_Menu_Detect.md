# LES MEG – menubevisst Detect i Delphi-programmet

8. september 2026. Lokal testutgave: **SD200W_SAIV_v1.0.4_MenuDetect_Sept2026.exe**.
SHA-256: `eb7b28cf8d82acab316bc2f74638c637f311f9cb3af2dbd9a39b59181028ee64`.

Nyere utgave: **1.0.5 SoftParity** bruker fysisk 8N1 med programvareparitet. Se [LES_MEG_Software_Parity.md](LES_MEG_Software_Parity.md). 1.0.4 beholdes som historisk byggtrinn.

## Endringen

Detect bruker en egen tilstandsstyrt søkeflyt per port og kommunikasjonsinnstilling:

- Lytter først etter loggeridentitet eller eksisterende instrumenttekst.
- Venter minst 250 ms etter siste mottatte tekst før neste kommando.
- Oppstartsmenyen med automatisk start etter 10 sekunder besvares med `S`.
- Status/start-menyen besvares med `M` for å hente hovedmenyen.
- Gjenkjent hovedmeny avslutter vekkingen. Ingen `I`, `M` eller `R` sendes der.
- Gjenkjente målelinjer identifiserer et instrument som allerede måler, uten å stoppe det.
- Ved stille port prøves `G` før vekkeforsøk. `I` gjentas bare mens ingen tekst mottas. Ukjent eller ufullstendig tekst blokkerer videre blind sending.
- Tekst med åttende bit satt ved 8N1 avviser denne innstillingen uten flere kommandoer, slik at det eksisterende søket går videre til 7E1.
- Avbrudd kontrolleres mellom mottak og korte ventinger. Tidsavbrudd begrenser hvert forsøk.

OSU107 og SAIV110 gjenkjennes fra banner uten CTD-kommandoer. Portnumrene COM7, COM11 og COM18 er testmiljøet, ikke hardkodede instrumentvalg.

## Kontroller og gjenstående arbeid

Maskinkoden testes med Unicorn ved ordinær og flyttet lasteadresse, blant annet menyfragmenter, 250 ms-regelen, avbrudd, ukjent tekst, feil paritet og bevaring av stakk/registere. Resultat: `analysis/menu_detect_validation.json`.

Første fysiske GUI-test fant OSU107 på COM11. COM18 ble ikke identifisert som instrument. COM7 var fortsatt Searching i den første utgaven: et etterfølgende rent mottak viste måledata med paritetsbiter ved 9600 8N1. Rent mottak ved **9600 7E1** ga lesbare målelinjer. Denne observasjonen førte til rettelsen for paritet. Opptakene er `analysis/com7_menu_receive_only.json` og `analysis/com7_menu_receive_only_7e1.json`.

**Den siste EXE-en er ikke ferdig godkjent mot alle fysiske menytilstander på COM7.** Automatisk godkjenningskontroll avviste gjentatt aktivt søk fordi vekkekommandoen I kan endre instrumenttilstand. Ingen omgåelse ble brukt; videre fysisk kontroll var kun mottak. Et nytt aktivt søk krever avklaring/godkjenning. Brukeren ønsker mulig videre bruk etter samtale med Morten Hammersland.

## Bygg på en annen PC

Les `OPPSTART_NY_PC.md` og `sd200DOc/PROSJEKTSTATUS.md`. Behold inngangsfilen `SD200W_SAIV_v1.0.3_Sept2026.exe`. Python-avhengigheter og GNU binutils må være tilgjengelige.

```powershell
python analysis/build_menu_detect.py
python analysis/test_menu_detect.py
python analysis/check_startup_windows.py SD200W_SAIV_v1.0.4_MenuDetect_Sept2026.exe --look-only
```

`--look-only` utfører ikke instrumentsøk. Kjør ikke fysiske søketester ukritisk. Bygget er hashbundet til 1.0.3 og overskriver ingen tidligere leveranse. Vi har fortsatt ikke original Delphi-kildekode; dette er en dokumentert maskinkodepatch. About, kreditering, disclaimer og tidligere formeloppførsel er bevart, med versjon oppdatert til 1.0.4. Filene er lokale og ikke publisert på GitHub.
