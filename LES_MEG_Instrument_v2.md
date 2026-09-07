Bruk SD200W_SAIV_OSU107_Instrument_v2.exe.

Den første oppstartsvarianten, SD200W_SAIV_OSU107_Instrument.exe, skal ikke
brukes: brukertesten viste krasj under oppstart.

V2 er bygget fra den siste fungerende kopien med den opprinnelige
initialiseringen beholdt. Etter at hovedvinduets første aktivering er ferdig,
utfører en engangstimer samme handling som instrumentikonet. Senere aktiveringer
bytter ikke side på nytt.

Download-sperren, fjerningen av Call/Receive, Developer-feltet, versjonsteksten
og Disclaimer-endringen er beholdt.

Kontroll: Faktisk Windows-oppstart på et separat skrivebord med vanlig tilgang.
Hovedvinduet var synlig, Instrument-siden var valgt og prosessen kjørte uten
feildialoger i alle 12 observasjoner over 12 sekunder. Kommunikasjon med et
fysisk instrument er ikke testet i denne kontrollen.

Byggeskript: analysis/build_deferred_start.py
Maskinkodekilde: analysis/start_instrument_deferred.s
Kontrollrapport: analysis/deferred_start_validation.json
