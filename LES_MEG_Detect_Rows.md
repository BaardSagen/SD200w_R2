# Grønn markering av instrumentraden

Bruk `SD200W_SAIV_OSU107_Detect_Rows.exe`.

Bare raden med et gjenkjent SD200-instrument får lys grønn bakgrunn og
svart tekst. Dette gjelder også når raden er valgt. Andre rader og det
tomme listeområdet bruker programmets opprinnelige farger. Valg av en
annen rad vises med vanlig blå markering.

Den tidligere endringen av hele listens bakgrunn og valgfarge er fjernet.
Markeringen utføres nå når den enkelte raden tegnes, og avgrenses til
Detect-listen. Portdata og radinnhold endres ikke av fargeleggingen.

Testet 7. september 2026 med de to fysisk tilkoblede portene:

- COM7: SD200 funnet på 9600 baud, Even parity.
- COM18: fortsatte søket uten instrumentfunn under testen.
- Begge rader var synlige ved vekselvis valg av COM7, COM18 og COM7.
- Skjermbilder bekrefter grønn COM7-rad, normalt tomt listeområde og
  lesbar tekst i begge rader ved alle tre valg.
- Detect/avbryt og Setup/avbryt fungerte uten feilmeldinger.

Tidligere endringer og prioritert søkerekkefølge er beholdt.
Forrige EXE er ikke overskrevet.

Bygg: `analysis/build_detect_rows.py`.
Testlogg: `analysis/runtime_test/SD200W_SAIV_OSU107_Detect_Rows.json`.
Skjermbilder: samme mappe, `SD200W_SAIV_OSU107_Detect_Rows_6.png`,
`_9.png`, `_12.png` og `_15.png`.
