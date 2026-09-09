# MiniSoft 1.0.6 — native UART og menystyrt Detect

Ny lokal leveranse: `SD200W_SAIV_v1.0.6_NativeUART_Sept2026.exe`. Fysisk COM7-kontroll bestått; ikke publisert på GitHub. ImGui-programmet er satt på pause etter brukerens ønske.

## Endring

- 7E1 settes i UART. Ingen softwareberegnet paritet på sending eller masking av mottatte bytes.
- Vekking bruker gjentatte I med 50 ms minimum mens det ikke kommer svar. Repetisjonen stopper ved første mottatte tekst.
- Vent på komplett meny og minst 250 ms siden siste mottatte tegn før S eller M.
- Målelinjer som begynner med N stoppes med I. Begge førstemenyer aksepteres, både automatisk start og automatisk passiv etter 10 sekunder. Derfra S til status, M til hovedmenyen.
- Hovedmeny som allerede mottas, godtas uten I eller M.
- Ved paritetsbit under 8N1 settes den åpne porten direkte til native 7E1. Tidligere lukking/gjenåpning mistet menyen som instrumentet skrev samtidig.

Windows-planlegging gir ca. 62–63 ms mellom I i målt spor med dagens 50 ms minimum. Dette er ikke en garanti om nøyaktig 50 ms på ledningen.

## Bygg og etterprøving

Utgangspunkt er uendret 1.0.3, SHA-256 `b817a5898aa2780dbfd502f22de28fbda7b1d4b0a1f8a0f50e0f564b56fdc2c9`.

```powershell
python analysis/build_native_uart_detect.py
python analysis/test_native_uart_detect.py
```

Maskinkode: `analysis/native_uart_detect.s`. Byggmanifest og testresultat ligger i `analysis/native_uart_detect_manifest.json` og `analysis/native_uart_detect_validation.json`.

Fysisk COM7-diagnostikk bygges med `analysis/build_com7_native_diagnostic.py`. Denne kopien blokkerer øvrige porter; den skal ikke leveres som produkt. Valgfrie `add_com7_tx_trace.py` og `add_com7_rx_trace.py` legger til Windows API-spor, i den rekkefølgen. Kjør bare fysisk test på en autorisert oppkobling. Brukeren autoriserte COM7 i denne økten.

## Avgrensning og historikk

Ingen original Delphi-kildekode er tilgjengelig; dette er dokumenterte EXE-patcher. Original og tidligere leveranser beholdes. Formelarbeidet er uendret og dokumentert separat.

1.0.5 SoftParity er historisk og er ikke valgt videre. Dens gamle DCB-test brukte dessuten feil byteoffsetter: Windows DCB ByteSize/Parity/StopBits ligger på 18/19/20, ikke 24/25. Historiske simuleringer dokumenterer derfor ikke korrekt fysisk UART-konfigurering i den utgaven.

Et instrument som allerede står i en taus hovedmeny kan svare på I med intervallmenyen. Den komplette teksten «Current set up:», «Measuring interval» og «Change: Y/N Menu: <G>» gjenkjennes; søket går tilbake med G uten å endre verdien. Dette forløpet er fysisk observert i direkte native test og inngår i emulatortestene. G alene ga ikke gjenutskrift fra hovedmeny i den direkte prøven.

## Verifisering 8. september 2026

557 x86-tilfeller bestod: fragmenterte start-, stopp-, hoved- og intervallmenyer, N-måling, loggere, ukjent tekst, avbryt, 50 ms minimum, 250 ms mottaksro, native DCB-bytte og API-feil. Register/stakk og alternativ lasteadresse er kontrollert.

Fysisk COM7: SD204, serienummer 1756, 9600 7E1. Første oppvåkning etter rettingen nådde hovedmenyen. Gjentatt prøve viste også korrekt e-paritet i søkeraden. Windows GetCommState bekreftet 7 databiter, EVEN og én stoppbit. WriteFile-spor bekreftet sendte tegn; mellom menymottak og neste kommando var minst 250 ms.

`analysis/com7_native_from_passive.json` gjelder første vellykkede paritetsovergang, før retting av paritetskolonnen. `analysis/com7_native_from_main.json` gjelder gjentatt detekt med korrekt kolonne; tilstanden var ikke bekreftet ved oppstart og dette er derfor ikke bevis på GUI-grenen for taus hovedmeny. Tidligere mislykkede rapporter er beholdt for å dokumentere feilen som ble rettet.

SHA-256 for siste kandidat: `4b7c492d8fa64b9bf2ffd939ef629d2d82cde7243d766aecb757810e27056b53`.

Sluttprøve av leveransefilens kode uten ekstra API-spor: `analysis/com7_native_final_selection.json`. Fra bekreftet passiv tilstand ble COM7 funnet som 9600/e og SD200, komplett hovedmeny ble mottatt, og OK-valg lukket Detect uten feildialog. Rapporten er kontrollert med `analysis/verify_com7_native_report.py`. Diagnostikkens eneste ekstra endring i denne prøven er sperren for andre COM-porter. Download er ikke fysisk prøvd i denne kontrollen.
