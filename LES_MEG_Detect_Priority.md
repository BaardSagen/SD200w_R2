# Detect med prioritert søkerekkefølge

Bruk `SD200W_SAIV_OSU107_Detect_Priority.exe`.

Programmet starter allerede separate søketråder for tilgjengelige COM-porter.
Denne funksjonen er beholdt. Hver port prøver nå:

1. 9600 baud, None parity
2. 9600 baud, Even parity
3. 4800 baud, None parity
4. 4800 baud, Even parity

Deretter følger 2400, 19200, 38400, 1200, 600 og 300 baud, med None og Even
for hver hastighet. Hver port går videre uavhengig av de andre, og slutter
å søke når enheten er gjenkjent. Opptatte porter kan ikke åpnes for søk.

Endringen bytter den eksisterende paritetstabellen fra Even/None til
None/Even. Alle tidligere endringer, inkludert grønn funnmarkering, er bevart.
Forrige EXE er ikke overskrevet.

Kontrollert ved kjøring av programmets faktiske valg av serieparametere
og overgang til neste forsøk: alle 16 kombinasjoner, korrekt avslutning og
to lasteadresser. Faktisk GUI-kjøring av oppstart, Detect/avbryt og
Setup/avbryt ga ingen feilmeldinger. Søk mot flere fysiske instrumenter
er ikke testet her; parallelliteten er bekreftet gjennom kodeanalyse.

Bygg: `analysis/set_detect_priority.py`.
Test: `analysis/check_detect_priority.py`.
