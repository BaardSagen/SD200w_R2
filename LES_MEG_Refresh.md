# Detect øverst og automatisk disk-refresh

Program: `SD200W_SAIV_OSU107_Refresh.exe`.
Bygger videre på SelectInstrument-versjonen. Tidligere EXE-filer er beholdt.

Detect og Setup har byttet plass i Instrument-vinduet. Detect står øverst; Setup står under Print. Funksjonene og resten av knappene er bevart.

Når Download mottar den konkrete teksten `Refresh disk Y/N`, avsluttes den gamle nedlastingsdialogen normalt. Programmet sender deretter én `Y` gjennom den eksisterende skrivefunksjonen på instrumentporten, uten ekstra linjeskift. Den gamle ESC-avbrytelsen og etterbehandlingen av nedlastede målinger hoppes over for denne responsen.

Meldingen `Preforming refresh off disks` vises og lukkes automatisk etter omtrent tre sekunder. Den forteller at refresh er forespurt; den bekrefter ikke at enheten har fullført operasjonen. Enhetens egne begrensninger, som sperre under aktiv logging, gjelder fortsatt. Automatisk COM-gjenåpning etter disk-refresh er ikke lagt til i denne endringen.

Andre Y/N-spørsmål besvares ikke automatisk. Log-funksjonen og vanlig Download med måledata beholder den eksisterende oppførselen. En senere Download kan forespørre refresh på nytt; gammel modusgjenkjenning blokkerer ikke knappen.

Kontroller utført:

- Fem grupper maskinkodetester: konkret refresh-spørsmål, fragmenterte pakker, store/små bokstaver, gjentatte nedlastinger, én Y per forespørsel, andre spørsmål, Log, vanlige nedlastinger og flyttet lasteadresse.
- GUI-oppstart og skjermbilde bekrefter ny knappeplassering uten feildialoger.
- Windows-meldingen lukket seg automatisk etter 3,063 sekunder på isolert testskrivebord.
- Seriell utsending er testet med simulert instrument. Ingen fysisk disk-refresh ble utført under denne kontrollen.

Bygg: `analysis/build_download_refresh.py`, `analysis/download_refresh.s`.
Tester: `analysis/test_refresh.py`, `analysis/check_refresh_message.py`.

SHA-256: `db8d760fd1677a6b0dcf915f657e0181f8f50f0dbdfae68a0892d9829bc12f16`
